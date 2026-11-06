"""M5 - 18 cas limites du contrat B4 et garanties de l'outbox.

Chaque cas part d'un resultat valide puis degrade un seul champ : on verifie
que le validateur refuse exactement ce qui doit l'etre, et rien de plus.
"""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from m5_b4 import (  # noqa: E402
    Outbox, OutboxError, SchemaError, build_hitl, sha256_json, validate_result,
)

BASE = {
    "incident": "I-2026-11",
    "ecarts": [{"chambre": "CF-1", "delta_c": 5.5, "duree_min": 120}],
    "magasins": ["G-1"],
    "lots": ["L-1"],
    "fournisseurs": ["F-1"],
    "obligation": {"texte": "Notification autorite sous 24 h", "delai_h": 24},
    "decision": "RETRAIT",
    "hitl": "REQUIS",
    "sources": ["mock_telemetry.csv#p1"],
}


def mutant(**changes):
    result = copy.deepcopy(BASE)
    result.update(changes)
    return result


class TestSchemaLimites(unittest.TestCase):
    """18 cas limites du schema canonique."""

    def assertRefus(self, result, code):
        with self.assertRaises(SchemaError) as ctx:
            validate_result(result)
        self.assertIn(code, str(ctx.exception))

    def test_01_reference_valide(self):
        validate_result(copy.deepcopy(BASE))

    def test_02_incident_mal_forme(self):
        self.assertRefus(mutant(incident="I-2026-1"), "INCIDENT_INVALIDE")

    def test_03_incident_non_texte(self):
        self.assertRefus(mutant(incident=202611), "INCIDENT_INVALIDE")

    def test_04_cle_manquante(self):
        result = copy.deepcopy(BASE)
        del result["sources"]
        self.assertRefus(result, "CLES_INVALIDES")

    def test_05_cle_extra(self):
        self.assertRefus(mutant(commentaire="hors contrat"), "CLES_INVALIDES")

    def test_06_ecarts_vide_sans_escalade(self):
        self.assertRefus(mutant(ecarts=[]), "ECARTS_VIDE")

    def test_07_ecarts_vide_avec_escalade(self):
        validate_result(mutant(ecarts=[], decision="ESCALADE"))

    def test_08_chambre_mal_formee(self):
        self.assertRefus(mutant(ecarts=[{"chambre": "CF1", "delta_c": 5.5, "duree_min": 10}]), "ECART_INVALIDE")

    def test_09_delta_texte(self):
        self.assertRefus(mutant(ecarts=[{"chambre": "CF-1", "delta_c": "5.5", "duree_min": 10}]), "ECART_INVALIDE")

    def test_10_duree_float(self):
        self.assertRefus(mutant(ecarts=[{"chambre": "CF-1", "delta_c": 5.5, "duree_min": 10.5}]), "ECART_INVALIDE")

    def test_11_delta_negatif_accepte(self):
        validate_result(mutant(ecarts=[{"chambre": "CF-1", "delta_c": -1.5, "duree_min": 0}]))

    def test_12_magasins_mal_formes(self):
        self.assertRefus(mutant(magasins=["MAGASIN-1"]), "MAGASINS_INVALIDE")

    def test_13_magasins_vide(self):
        self.assertRefus(mutant(magasins=[]), "MAGASINS_INVALIDE")

    def test_14_lots_mal_formes(self):
        self.assertRefus(mutant(lots=["LOT-1"]), "LOTS_INVALIDE")

    def test_15_fournisseurs_vide(self):
        self.assertRefus(mutant(fournisseurs=[]), "FOURNISSEURS_INVALIDE")

    def test_16_obligation_extra(self):
        self.assertRefus(mutant(obligation={"texte": "x", "delai_h": 24, "source": "ISO"}), "OBLIGATION_INVALIDE")

    def test_17_decision_inconnue(self):
        self.assertRefus(mutant(decision="DESTRUCTION"), "DECISION_OU_HITL_INVALIDE")

    def test_18_hitl_valeur_libre(self):
        self.assertRefus(mutant(hitl="PEUT_ETRE"), "DECISION_OU_HITL_INVALIDE")

    def test_19_sources_vide(self):
        self.assertRefus(mutant(sources=[]), "SOURCES_INVALIDES")

    def test_20_sources_trop_nombreuses(self):
        self.assertRefus(mutant(sources=[f"src{i}.csv" for i in range(9)]), "SOURCES_INVALIDES")

    def test_21_source_mal_formee(self):
        self.assertRefus(mutant(sources=["../etc/passwd"]), "SOURCES_INVALIDES")


class TestOutbox(unittest.TestCase):
    def setUp(self):
        self.outbox = Outbox(max_attempts=3, backoff=(0, 0, 0))
        self.event = {"incident": "I-2026-11", "decision": "RETRAIT", "hitl": "APPROVED"}

    def test_22_idempotence_enqueue(self):
        a = self.outbox.enqueue("I-2026-11:RETRAIT", self.event)
        b = self.outbox.enqueue("I-2026-11:RETRAIT", self.event)
        self.assertEqual(a["status"], "ENQUEUED")
        self.assertEqual(b["status"], "DUPLICATE")
        self.assertEqual(len(self.outbox.records), 1)

    def test_23_cle_vide_refusee(self):
        with self.assertRaises(OutboxError):
            self.outbox.enqueue("", self.event)

    def test_24_retry_puis_succes(self):
        self.outbox.enqueue("k1", self.event)
        calls = {"n": 0}

        def sender(payload):
            calls["n"] += 1
            if calls["n"] < 2:
                raise TimeoutError("plateforme indisponible")
            return {"receipt": "ACK-1"}

        out = self.outbox.deliver("k1", sender)
        self.assertEqual(out["status"], "DELIVERED")
        self.assertEqual(out["attempts"], 2)

    def test_25_bascule_dlq_apres_3_echecs(self):
        self.outbox.enqueue("k2", self.event)

        def sender(payload):
            raise ConnectionError("503")

        out = self.outbox.deliver("k2", sender)
        self.assertEqual(out["status"], "DLQ")
        self.assertEqual(len(self.outbox.dlq), 1)
        self.assertEqual(self.outbox.dlq[0]["attempts"], 3)
        self.assertEqual(self.outbox.records[0]["status"], "DLQ")

    def test_26_rejeu_meme_payload(self):
        self.outbox.enqueue("k3", self.event)
        self.outbox.deliver("k3", lambda p: (_ for _ in ()).throw(TimeoutError("t")))
        dlq_id = self.outbox.dlq[0]["dlq_id"]
        before = sha256_json(self.outbox.records[0]["payload"])

        out = self.outbox.replay(dlq_id, lambda p: {"receipt": "ACK-REPLAY"})
        self.assertEqual(out["status"], "DELIVERED")
        self.assertEqual(sha256_json(self.outbox.records[0]["payload"]), before)
        self.assertEqual(self.outbox.dlq[0]["status"], "REPLAYED")
        self.assertTrue(self.outbox.dlq[0]["payload_unchanged"])

    def test_27_pas_de_double_livraison(self):
        self.outbox.enqueue("k4", self.event)
        first = self.outbox.deliver("k4", lambda p: {"receipt": "ACK-1"})
        second = self.outbox.deliver("k4", lambda p: {"receipt": "ACK-2"})
        self.assertEqual(first["status"], "DELIVERED")
        self.assertEqual(second["status"], "ALREADY_DONE")
        self.assertEqual(second["receipt"]["receipt"], "ACK-1")

    def test_28_pas_de_rejeu_hors_dlq(self):
        with self.assertRaises(OutboxError):
            self.outbox.replay("DLQ-9999", lambda p: {})

    def test_29_payload_dlq_integre(self):
        self.outbox.enqueue("k5", self.event)
        self.outbox.deliver("k5", lambda p: (_ for _ in ()).throw(TimeoutError("t")))
        entry = self.outbox.dlq[0]
        self.assertEqual(entry["payload_hash"], sha256_json(self.event))
        self.assertIn("last_error", entry)

    def test_30_dlq_isole_les_incidents(self):
        self.outbox.enqueue("ok", self.event)
        self.outbox.deliver("ok", lambda p: {"receipt": "ACK"})
        self.outbox.enqueue("ko", self.event)
        self.outbox.deliver("ko", lambda p: (_ for _ in ()).throw(TimeoutError("t")))
        self.assertEqual(len(self.outbox.dlq), 1)
        self.assertEqual(self.outbox.records[0]["status"], "DONE")


class TestHitlPayload(unittest.TestCase):
    def test_31_token_porte_le_hash_du_resultat(self):
        hitl = build_hitl(copy.deepcopy(BASE), {"obligation": {"delai_h": 24}})
        self.assertEqual(hitl["payload"]["result_hash"], sha256_json(BASE))
        self.assertEqual(hitl["required_role"], "QUALITY_MANAGER")

    def test_32_rappel_exige_double_controle(self):
        rappel = mutant(decision="RAPPEL")
        hitl = build_hitl(rappel, {"obligation": {"delai_h": 24}})
        self.assertTrue(hitl["dual_control"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
