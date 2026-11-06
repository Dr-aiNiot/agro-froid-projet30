"""9 tests d'audit fonctionnel M5 - B4 decision + HITL."""
from __future__ import annotations

import copy
import json
import re
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import m5_b4 as m5  # noqa: E402

DATA = ROOT / "data"


def base_pack() -> dict:
    return json.loads((DATA / "mock_b2_pack.json").read_text(encoding="utf-8"))


def write_temp(obj: dict, name: str) -> str:
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(obj, tmp, ensure_ascii=False)
    tmp.close()
    return tmp.name


class TestM5(unittest.TestCase):
    def test_01_nominal_retrait(self):
        out = m5.analyze(DATA / "mock_b2_pack.json", DATA / "mock_telemetry.csv",
                         DATA / "policy.json", DATA / "certificates.json")
        r = out["result"]
        self.assertEqual(set(r), set(m5.REQUIRED))
        self.assertEqual(r["incident"], "I-2026-11")
        self.assertEqual(r["ecarts"], [{"chambre": "CF-3", "delta_c": 4.2, "duree_min": 190}])
        self.assertEqual(r["magasins"], ["G-12", "G-19"])
        self.assertEqual(r["lots"], ["L-8841", "L-8842"])
        self.assertEqual(r["fournisseurs"], ["F-07"])
        self.assertEqual(r["decision"], "RETRAIT")
        self.assertEqual(r["hitl"], "REQUIS")
        self.assertEqual(out["analysis"]["motif"], "P1_DELTA_DUREE")
        self.assertFalse(out["analysis"]["quarantine"])

    def test_02_rappel_si_lot_vendu(self):
        pack = base_pack()
        pack["lots_detail"][0]["vendus"] = 40
        p = write_temp(pack, "pack_rappel")
        out = m5.analyze(p, DATA / "mock_telemetry.csv", DATA / "policy.json", DATA / "certificates.json")
        self.assertEqual(out["result"]["decision"], "RAPPEL")
        self.assertEqual(out["result"]["hitl"], "REQUIS")
        self.assertTrue(out["hitl"]["dual_control"])

    def test_03_certificat_invalide_quarantaine(self):
        certs = json.loads((DATA / "certificates.json").read_text(encoding="utf-8"))
        certs["F-07"]["valid"] = False
        c = write_temp(certs, "certs_invalides")
        out = m5.analyze(DATA / "mock_b2_pack.json", DATA / "mock_telemetry.csv", DATA / "policy.json", c)
        self.assertEqual(out["result"]["decision"], "ESCALADE")
        self.assertTrue(out["analysis"]["quarantine"])
        self.assertIn("CERTIFICAT", out["analysis"]["motif"])

    def test_04_confiance_basse_escalade(self):
        pack = base_pack()
        pack["confidence"] = 0.5
        p = write_temp(pack, "pack_low")
        out = m5.analyze(p, DATA / "mock_telemetry.csv", DATA / "policy.json", DATA / "certificates.json")
        self.assertEqual(out["result"]["decision"], "ESCALADE")
        self.assertEqual(out["analysis"]["motif"], "E_LOW_CONFIDENCE")

    def test_05_token_modifie_rejete(self):
        out = m5.analyze(DATA / "mock_b2_pack.json", DATA / "mock_telemetry.csv",
                         DATA / "policy.json", DATA / "certificates.json")
        token = out["hitl"]["token"]
        tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
        ledger = m5.Ledger()
        with self.assertRaises(m5.HitlError) as ctx:
            ledger.commit(tampered, out["result"], "U-042", "QUALITY_MANAGER", "test")
        self.assertEqual(str(ctx.exception), "SIGNATURE_INVALIDE")

    def test_06_token_expire_rejete(self):
        out = m5.analyze(DATA / "mock_b2_pack.json", DATA / "mock_telemetry.csv",
                         DATA / "policy.json", DATA / "certificates.json")
        issued = m5.now_utc() - timedelta(minutes=31)
        package = m5.build_hitl(out["result"], m5.load_json(DATA / "policy.json"), issued)
        ledger = m5.Ledger()
        with self.assertRaises(m5.HitlError) as ctx:
            ledger.commit(package["token"], out["result"], "U-042", "QUALITY_MANAGER", "test")
        self.assertEqual(str(ctx.exception), "TOKEN_EXPIRE")

    def test_07_rejeu_refuse(self):
        out = m5.analyze(DATA / "mock_b2_pack.json", DATA / "mock_telemetry.csv",
                         DATA / "policy.json", DATA / "certificates.json")
        ledger = m5.Ledger()
        ledger.commit(out["hitl"]["token"], out["result"], "U-042", "QUALITY_MANAGER", "ok")
        with self.assertRaises(m5.HitlError) as ctx:
            ledger.commit(out["hitl"]["token"], out["result"], "U-042", "QUALITY_MANAGER", "ok")
        self.assertEqual(str(ctx.exception), "TOKEN_DEJA_UTILISE")

    def test_08_schema_invalide_rejete(self):
        out = m5.analyze(DATA / "mock_b2_pack.json", DATA / "mock_telemetry.csv",
                         DATA / "policy.json", DATA / "certificates.json")
        bad = copy.deepcopy(out["result"])
        bad["extra"] = "interdit"
        with self.assertRaises(m5.SchemaError):
            m5.validate_result(bad)
        missing = copy.deepcopy(out["result"])
        del missing["sources"]
        with self.assertRaises(m5.SchemaError):
            m5.validate_result(missing)

    def test_09_telemetrie_non_fiable_ne_reduit_pas(self):
        out = m5.analyze(DATA / "mock_b2_pack.json", DATA / "mock_telemetry_falsified.csv",
                         DATA / "policy.json", DATA / "certificates.json")
        self.assertEqual(out["result"]["decision"], "RETRAIT")
        self.assertEqual(out["analysis"]["untrusted_rows"], 1)
        all_false = m5.analyze(DATA / "mock_b2_pack.json", DATA / "mock_telemetry_all_false.csv",
                               DATA / "policy.json", DATA / "certificates.json")
        self.assertEqual(all_false["result"]["decision"], "ESCALADE")
        self.assertEqual(all_false["analysis"]["motif"], "E_NO_VERIFIED_TELEMETRY")

    def test_10_aucune_pii_en_sortie(self):
        out = m5.analyze(DATA / "mock_b2_pack.json", DATA / "mock_telemetry.csv",
                         DATA / "policy.json", DATA / "certificates.json")
        text = json.dumps(out["result"], ensure_ascii=False)
        self.assertNotIn("tok_", text)
        self.assertNotIn("@", text)
        self.assertIsNone(re.search(r"\b\d{13,19}\b", text))


if __name__ == "__main__":
    unittest.main(verbosity=2)
