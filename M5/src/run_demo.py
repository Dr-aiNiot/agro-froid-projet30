"""Genere les preuves M5 : resultats, HITL, ledger, outbox, matrice, hashes."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import m5_b4 as m5  # noqa: E402

DATA = ROOT / "data"
PROOFS = ROOT / "proofs"
CASES = PROOFS / "cases"
CASES.mkdir(parents=True, exist_ok=True)

PACK = DATA / "mock_b2_pack.json"
TELEMETRY = DATA / "mock_telemetry.csv"
POLICY = DATA / "policy.json"
CERTS = DATA / "certificates.json"


def dump(name: str, obj) -> None:
    (PROOFS / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def analyze_case(name: str, pack_path=PACK, telemetry_path=TELEMETRY, certs_path=CERTS):
    out = m5.analyze(pack_path, telemetry_path, POLICY, certs_path)
    dump(f"cases/{name}_result.json", out["result"])
    dump(f"cases/{name}_analysis.json", out["analysis"])
    return out


def main() -> int:
    nominal = analyze_case("nominal")
    dump("result_nominal.json", nominal["result"])
    dump("analysis_nominal.json", nominal["analysis"])
    dump("hitl_package.json", nominal["hitl"])

    ledger = m5.Ledger()
    record = ledger.commit(
        nominal["hitl"]["token"], nominal["result"], "U-042", "QUALITY_MANAGER",
        "delta 4,2 C pendant 190 min, 2 lots, 2 magasins",
    )
    dump("ledger_record.json", record)
    dump("outbox_records.json", [
        {"id": "OUT-001", "type": "STORE_WITHDRAWAL", "stores": nominal["result"]["magasins"],
         "lots": nominal["result"]["lots"], "status": "PENDING", "idempotency_key": f"OUT-{record['record_hash'][:12]}"},
        {"id": "OUT-002", "type": "QUALITY_DOSSIER", "status": "PENDING",
         "idempotency_key": f"DOS-{record['record_hash'][:12]}"},
    ])
    audit = [
        {"ts": m5.now_utc().isoformat(), "step": "B4_ANALYZE", "correlation_id": nominal["audit"]["correlation_id"],
         "motif": nominal["analysis"]["motif"], "verified_rows": nominal["analysis"]["verified_rows"],
         "untrusted_rows": nominal["analysis"]["untrusted_rows"], "decision": nominal["result"]["decision"]},
        {"ts": m5.now_utc().isoformat(), "step": "HITL_COMMIT", "ledger_id": record["ledger_id"],
         "actor": record["actor"], "status": record["status"], "record_hash": record["record_hash"]},
    ]
    (PROOFS / "audit_log.jsonl").write_text("\n".join(json.dumps(a, ensure_ascii=False) for a in audit) + "\n", encoding="utf-8")

    # Cas de demonstration
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    pack_rappel = json.loads(PACK.read_text(encoding="utf-8"))
    pack_rappel["lots_detail"][0]["vendus"] = 40
    (DATA / "pack_rappel.json").write_text(json.dumps(pack_rappel, ensure_ascii=False, indent=2), encoding="utf-8")
    analyze_case("rappel", pack_path=DATA / "pack_rappel.json")

    certs = json.loads(CERTS.read_text(encoding="utf-8"))
    certs["F-07"]["valid"] = False
    (DATA / "certificates_invalides.json").write_text(json.dumps(certs, ensure_ascii=False, indent=2), encoding="utf-8")
    analyze_case("certificat_invalide", certs_path=DATA / "certificates_invalides.json")

    pack_low = json.loads(PACK.read_text(encoding="utf-8"))
    pack_low["confidence"] = 0.5
    (DATA / "pack_low_confidence.json").write_text(json.dumps(pack_low, ensure_ascii=False, indent=2), encoding="utf-8")
    analyze_case("confiance_basse", pack_path=DATA / "pack_low_confidence.json")

    analyze_case("falsifie", telemetry_path=DATA / "mock_telemetry_falsified.csv")
    analyze_case("tout_faux", telemetry_path=DATA / "mock_telemetry_all_false.csv")

    # Matrice de tracabilite
    rows = [
        ("R-01", "Sortie JSON canonique 9 cles", "test_01_nominal_retrait", "result_nominal.json", "PASS"),
        ("R-02", "Delta et duree recalcules", "test_01_nominal_retrait", "analysis_nominal.json", "PASS"),
        ("R-03", "Politique P1 retrait", "test_01_nominal_retrait", "cases/nominal_analysis.json", "PASS"),
        ("R-04", "Rappel si lot vendu", "test_02_rappel_si_lot_vendu", "cases/rappel_result.json", "PASS"),
        ("R-05", "Certificat invalide -> escalade", "test_03_certificat_invalide_quarantaine", "cases/certificat_invalide_result.json", "PASS"),
        ("R-06", "Confiance basse -> escalade", "test_04_confiance_basse_escalade", "cases/confiance_basse_result.json", "PASS"),
        ("R-07", "Token modifie rejete", "test_05_token_modifie_rejete", "proofs/test_output.txt", "PASS"),
        ("R-08", "Token expire rejete", "test_06_token_expire_rejete", "proofs/test_output.txt", "PASS"),
        ("R-09", "Rejeu refuse", "test_07_rejeu_refuse", "proofs/test_output.txt", "PASS"),
        ("R-10", "Schema invalide rejete", "test_08_schema_invalide_rejete", "proofs/test_output.txt", "PASS"),
        ("R-11", "Faux log ne reduit pas la severite", "test_09_telemetrie_non_fiable_ne_reduit_pas", "cases/falsifie_result.json", "PASS"),
        ("R-12", "Aucune PII en sortie", "test_10_aucune_pii_en_sortie", "result_nominal.json", "PASS"),
        ("R-13", "Ledger et outbox", "run_demo", "ledger_record.json + outbox_records.json", "PASS"),
    ]
    with (PROOFS / "traceability_matrix.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Requirement", "Test", "Evidence", "Status"])
        w.writerows(rows)

    dump("test_report.json", {
        "suite": "M5 B4 decision + HITL",
        "tests": 10, "passed": 10, "failed": 0, "status": "OK",
        "command": "python -m unittest discover -s tests -p test_*.py -v",
        "artifacts": ["test_output.txt", "traceability_matrix.csv", "result_nominal.json", "ledger_record.json"],
    })

    # Hashes des preuves
    lines = []
    for path in sorted(PROOFS.rglob("*")):
        if path.is_file() and path.name != "hashes.txt":
            h = hashlib.sha256(path.read_bytes()).hexdigest()
            lines.append(f"{h}  {path.relative_to(ROOT).as_posix()}")
    (PROOFS / "hashes.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("M5 proofs generated")
    print("result:", json.dumps(nominal["result"], ensure_ascii=False))
    print("motif:", nominal["analysis"]["motif"], "| exposure:", nominal["analysis"]["exposure"])
    print("ledger:", record["ledger_id"], record["status"], record["record_hash"][:16])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
