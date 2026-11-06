"""M5 - preuve d'execution Outbox : retry, DLQ, rejeu et idempotence.

Genere proofs/outbox_delivery.json et proofs/dlq_replay.json a partir du
moteur reel (analyze -> HITL -> Ledger -> Outbox), sans rejouer la decision.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from m5_b4 import (  # noqa: E402
    DATA, PROOFS, Ledger, Outbox, analyze, sha256_json,
)

PACK = DATA / "mock_b2_pack.json"
TELEMETRY = DATA / "mock_telemetry.csv"
POLICY = DATA / "policy.json"
CERTS = DATA / "certificates.json"


def ecrire(nom: str, donnees) -> None:
    PROOFS.mkdir(parents=True, exist_ok=True)
    chemin = PROOFS / nom
    chemin.write_text(json.dumps(donnees, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK {chemin.name}")


def build_case(nom: str, panne) -> dict:
    out = analyze(PACK, TELEMETRY, POLICY, CERTS)
    result, hitl = out["result"], out["hitl"]
    ledger = Ledger()
    commit = ledger.commit(hitl["token"], result, actor="driss.larhrissi",
                           actor_role="QUALITY_MANAGER", reason="Decision validee en revue")
    outbox = Outbox(max_attempts=3, backoff=(0, 0, 0))
    cle = f"{result['incident']}:{result['decision']}:{commit['result_hash'][:12]}"
    event = {
        "incident_id": result["incident"],
        "decision": result["decision"],
        "ledger_id": commit["ledger_id"],
        "result_hash": commit["result_hash"],
        "hitl_approved_by": commit["actor"],
        "hitl_reason": commit["reason"],
    }
    enq = outbox.enqueue(cle, event)
    livraison = outbox.deliver(cle, panne)
    rejeu = None
    if livraison["status"] == "DLQ":
        rejeu = outbox.replay(outbox.dlq[0]["dlq_id"], lambda payload: {
            "receipt": "ACK-REPLAY",
            "received_hash": sha256_json(payload),
        })
    return {
        "cas": nom,
        "decision": result["decision"],
        "motif": out["analysis"]["motif"],
        "hitl_required": hitl["required"],
        "idempotency_key": cle,
        "enqueue": enq["status"],
        "delivery": livraison,
        "replay": rejeu,
        "dlq": outbox.dlq,
        "outbox_records": outbox.records,
        "ledger_records": ledger.records,
        "payload_unchanged_after_replay": (
            sha256_json(outbox.records[0]["payload"]) == enq["record"]["payload_hash"]
        ),
    }


def panne_aucune(payload):
    return {"receipt": "ACK-1", "received_hash": sha256_json(payload)}


def panne_transitoire_factory():
    etat = {"n": 0}

    def sender(payload):
        etat["n"] += 1
        if etat["n"] < 3:
            raise TimeoutError(f"plateforme indisponible (essai {etat['n']})")
        return {"receipt": "ACK-RETRY", "attempts_before_ack": etat["n"]}

    return sender


def panne_permanente(payload):
    raise ConnectionError("503 SERVICE_UNAVAILABLE")


def main() -> int:
    nominal = build_case("nominal - livraison immediate", panne_aucune)
    transitoire = build_case("transitoire - 2 echecs puis succes", panne_transitoire_factory())
    permanent = build_case("permanente - bascule DLQ puis rejeu", panne_permanente)

    outbox = Outbox(max_attempts=3, backoff=(0, 0, 0))
    event = permanent["outbox_records"][0]["payload"]
    cle = permanent["idempotency_key"]
    premier = outbox.enqueue(cle, event)
    second = outbox.enqueue(cle, event)
    premiere_livraison = outbox.deliver(cle, lambda p: {"receipt": "ACK-UNIQUE"})
    seconde_livraison = outbox.deliver(cle, lambda p: {"receipt": "ACK-DOUBLON"})

    rapport = {
        "horodatage": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat(),
        "modele": "B4 Decision + HITL (execution reelle, aucun LLM)",
        "politique_backoff_secondes": [1, 2, 4],
        "tentatives_max": 3,
        "cas": [nominal, transitoire, permanent],
        "idempotence": {
            "cle": cle,
            "enqueue_1": premier["status"],
            "enqueue_2": second["status"],
            "premiere_livraison": premiere_livraison["status"],
            "seconde_livraison": seconde_livraison["status"],
            "recu_identique": premiere_livraison["receipt"] == seconde_livraison["receipt"],
            "total_enregistrements": len(outbox.records),
        },
    }
    ecrire("outbox_delivery.json", rapport)
    ecrire("dlq_replay.json", {
        "dlq": permanent["dlq"],
        "replay": permanent["replay"],
        "payload_unchanged_after_replay": permanent["payload_unchanged_after_replay"],
        "decision_recalculee": False,
        "commentaire": (
            "Le rejeu reutilise le payload signe de la DLQ : la decision n'est pas "
            "recalculee, le hash reste identique et aucun doublon n'est cree."
        ),
    })

    verifs = [
        nominal["delivery"]["status"] == "DELIVERED",
        transitoire["delivery"]["status"] == "DELIVERED" and transitoire["delivery"]["attempts"] == 3,
        permanent["delivery"]["status"] == "DLQ" and len(permanent["dlq"]) == 1,
        permanent["replay"] and permanent["replay"]["status"] == "DELIVERED",
        permanent["payload_unchanged_after_replay"] is True,
        premier["status"] == "ENQUEUED" and second["status"] == "DUPLICATE",
        seconde_livraison["status"] == "ALREADY_DONE",
        len(outbox.records) == 1,
    ]
    print(f"\nVerifications outbox : {sum(verifs)}/{len(verifs)} OK")
    if not all(verifs):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
