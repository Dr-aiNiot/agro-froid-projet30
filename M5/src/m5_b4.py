"""M5 - B4 Decision, exposition et HITL.

Prototype deterministe, sans dependance externe. Toutes les valeurs critiques
(delta, duree, exposition, politique, token) sont calculees en Python.
"""
from __future__ import annotations

import base64
import csv
import hashlib
import hmac
import json
import re
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROOFS = ROOT / "proofs"
SECRET = b"AGRO-FROID-DEMO-HMAC-KEY-2026"  # demo only; production: env / vault

REQUIRED = ["incident", "ecarts", "magasins", "lots", "fournisseurs",
            "obligation", "decision", "hitl", "sources"]
DECISIONS = {"RETRAIT", "RAPPEL", "SURVEILLANCE", "ESCALADE"}


class M5Error(Exception):
    pass


class SchemaError(M5Error):
    pass


class HitlError(M5Error):
    pass


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(obj: Any) -> str:
    return sha256_text(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def hmac_hex(key: bytes, message: str) -> str:
    return hmac.new(key, message.encode("utf-8"), hashlib.sha256).hexdigest()


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Telemetrie signee
# ---------------------------------------------------------------------------

def sign_row(ts: str, chambre: str, capteur: str, temp: float, seq: int,
             key_id: str = "K-CF3-01", key: bytes = SECRET) -> str:
    msg = f"{ts}|{chambre}|{capteur}|{temp}|{seq}"
    return hmac_hex(key, msg)[:16]


def verify_row(row: dict[str, str], key: bytes = SECRET) -> bool:
    expected = sign_row(row["ts"], row["chambre"], row["capteur"],
                        float(row["temp_c"]), int(row["seq"]), row["key_id"], key)
    return hmac.compare_digest(expected, row["hmac"])


def load_telemetry(path: str | Path, key: bytes = SECRET) -> dict[str, Any]:
    rows, verified, quarantine = [], [], []
    with Path(path).open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(row)
            if verify_row(row, key):
                verified.append(row)
            else:
                quarantine.append({**row, "motif": "HMAC_INVALIDE"})
    return {"rows": rows, "verified": verified, "quarantine": quarantine,
            "trusted": len(quarantine) == 0}


def compute_ecarts(verified: list[dict[str, str]], consignes: dict[str, float]) -> list[dict[str, Any]]:
    by_chambre: dict[str, list[dict[str, str]]] = {}
    for row in verified:
        by_chambre.setdefault(row["chambre"], []).append(row)
    ecarts = []
    for chambre, rows in by_chambre.items():
        temps = [float(r["temp_c"]) for r in rows]
        ts = sorted(datetime.fromisoformat(r["ts"].replace("Z", "+00:00")) for r in rows)
        duree = int((ts[-1] - ts[0]).total_seconds() // 60) if len(ts) > 1 else 0
        consigne = float(consignes.get(chambre, 4.0))
        delta = round(max(temps) - consigne, 1)
        if delta > 0:
            ecarts.append({"chambre": chambre, "delta_c": delta, "duree_min": duree})
    return sorted(ecarts, key=lambda e: e["chambre"])


# ---------------------------------------------------------------------------
# Politique et exposition
# ---------------------------------------------------------------------------

def certificate_ok(pack: dict[str, Any], certificates: dict[str, Any]) -> tuple[bool, str]:
    for fid in pack["candidates"]["fournisseurs"]:
        cert = certificates.get(fid)
        if not cert or not cert.get("valid", False):
            return False, f"CERTIFICAT_ABSENT_OU_INVALIDE:{fid}"
        if cert.get("expires_at", "9999-12-31") < "2026-11-05":
            return False, f"CERTIFICAT_EXPIRE:{fid}"
        for lot in pack["candidates"]["lots"]:
            if lot not in cert.get("lot_ids", []):
                return False, f"CERTIFICAT_NON_LIE_AU_LOT:{fid}:{lot}"
    return True, "OK"


def compute_exposure(pack: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    details = pack.get("lots_detail", [])
    n_magasins = len({d.get("magasin") for d in details}) or len(pack["candidates"]["magasins"])
    f_magasin = 1.0 if n_magasins <= 1 else (1.2 if n_magasins == 2 else 1.4)
    f_delai = 1.5 if policy["obligation"]["delai_h"] < 24 else 1.0
    total = 0.0
    for d in details:
        q = float(d.get("quantite", 0))
        vendus = float(d.get("vendus", 0))
        f_vente = 1 + min(vendus / q, 1.0) if q > 0 else 1.0
        total += q * f_magasin * f_vente * f_delai
    score = min(100.0, round(100.0 * total / 1000.0, 1))
    niveau = "CRITIQUE" if score >= policy["exposure"]["seuil_critique"] else (
        "ELEVE" if score >= policy["exposure"]["seuil_eleve"] else "MODERE")
    return {"score": score, "niveau": niveau, "lots": len(details),
            "magasins": n_magasins, "clients_tokenized": int(pack["candidates"].get("clients_tokenized_count", 0)),
            "f_magasin": f_magasin, "f_delai": f_delai, "total_brut": round(total, 1)}


def decide(pack: dict[str, Any], ecarts: list[dict[str, Any]], cert_ok: bool,
           cert_reason: str, policy: dict[str, Any], telemetry: dict[str, Any]) -> tuple[str, str, bool]:
    if not telemetry["trusted"] and not telemetry["verified"]:
        return "ESCALADE", "E_NO_VERIFIED_TELEMETRY", True
    if not ecarts:
        return "ESCALADE", "E_NO_ECART_VERIFIE", True
    if pack.get("confidence", 0) < policy["seuils"]["confidence_min"]:
        return "ESCALADE", "E_LOW_CONFIDENCE", False
    if not cert_ok:
        return "ESCALADE", cert_reason, True
    delta = max(e["delta_c"] for e in ecarts)
    duree = max(e["duree_min"] for e in ecarts)
    if delta >= policy["seuils"]["delta_c"] and duree >= policy["seuils"]["duree_min"]:
        vendus = sum(int(d.get("vendus", 0)) for d in pack.get("lots_detail", []))
        if vendus > 0:
            return "RAPPEL", "P2_LOT_VENDU", False
        return "RETRAIT", "P1_DELTA_DUREE", False
    return "SURVEILLANCE", "P6_SOUS_SEUIL", False


# ---------------------------------------------------------------------------
# Construction et validation
# ---------------------------------------------------------------------------

def build_result(pack: dict[str, Any], ecarts: list[dict[str, Any]], decision: str,
                 policy: dict[str, Any], sources: list[str]) -> dict[str, Any]:
    result = {
        "incident": pack["anchor"]["id"],
        "ecarts": ecarts,
        "magasins": pack["candidates"]["magasins"],
        "lots": pack["candidates"]["lots"],
        "fournisseurs": pack["candidates"]["fournisseurs"],
        "obligation": {"texte": policy["obligation"]["texte"], "delai_h": int(policy["obligation"]["delai_h"])},
        "decision": decision,
        "hitl": "REQUIS" if decision in {"RETRAIT", "RAPPEL", "ESCALADE"} else "NON_REQUIS",
        "sources": sources[:8],
    }
    validate_result(result)
    return result


def validate_result(result: dict[str, Any]) -> None:
    if set(result) != set(REQUIRED):
        raise SchemaError(f"CLES_INVALIDES: manquantes={set(REQUIRED)-set(result)} extras={set(result)-set(REQUIRED)}")
    if not re.match(r"^I-\d{4}-\d{2}$", result["incident"]):
        raise SchemaError("INCIDENT_INVALIDE")
    if not result["ecarts"] and result["decision"] != "ESCALADE":
        raise SchemaError("ECARTS_VIDE")
    for e in result["ecarts"]:
        if not re.match(r"^CF-\d+$", e["chambre"]) or not isinstance(e["delta_c"], (int, float)) or not isinstance(e["duree_min"], int):
            raise SchemaError("ECART_INVALIDE")
    for key, pattern in (("magasins", r"^G-\d+$"), ("lots", r"^L-\d+$"), ("fournisseurs", r"^F-\d+$")):
        if not result[key] or not all(re.match(pattern, x) for x in result[key]):
            raise SchemaError(f"{key.upper()}_INVALIDE")
    if not isinstance(result["obligation"], dict) or set(result["obligation"]) != {"texte", "delai_h"}:
        raise SchemaError("OBLIGATION_INVALIDE")
    if result["decision"] not in DECISIONS or result["hitl"] not in {"REQUIS", "NON_REQUIS"}:
        raise SchemaError("DECISION_OU_HITL_INVALIDE")
    if not (1 <= len(result["sources"]) <= 8) or not all(re.match(r"^[A-Za-z0-9_.-]+(#(p\d+|L\d+))?$", s) for s in result["sources"]):
        raise SchemaError("SOURCES_INVALIDES")


# ---------------------------------------------------------------------------
# HITL signe, anti-rejeu
# ---------------------------------------------------------------------------

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def b64url_decode(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def build_hitl(result: dict[str, Any], policy: dict[str, Any], when: datetime | None = None) -> dict[str, Any]:
    when = when or now_utc()
    payload = {
        "incident_id": result["incident"],
        "decision": result["decision"],
        "result_hash": sha256_json(result),
        "nonce": secrets.token_hex(8),
        "issued_at": when.isoformat(),
        "expires_at": (when + timedelta(minutes=30)).isoformat(),
        "required_role": "QUALITY_MANAGER",
        "dual_control": result["decision"] == "RAPPEL",
    }
    payload_b64 = b64url(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    token = payload_b64 + "." + b64url(hmac.new(SECRET, payload_b64.encode(), hashlib.sha256).digest())
    return {"required": result["hitl"] == "REQUIS", "token": token, "payload": payload,
            "expires_at": payload["expires_at"], "required_role": payload["required_role"],
            "dual_control": payload["dual_control"]}


def verify_token(token: str, result: dict[str, Any], actor_role: str,
                 used_nonces: set[str], when: datetime | None = None) -> dict[str, Any]:
    when = when or now_utc()
    try:
        payload_b64, sig_b64 = token.split(".")
    except ValueError as exc:
        raise HitlError("TOKEN_MALFORME") from exc
    expected = b64url(hmac.new(SECRET, payload_b64.encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(expected, sig_b64):
        raise HitlError("SIGNATURE_INVALIDE")
    payload = json.loads(b64url_decode(payload_b64))
    if payload["result_hash"] != sha256_json(result):
        raise HitlError("RESULTAT_MODIFIE")
    if when.isoformat() > payload["expires_at"]:
        raise HitlError("TOKEN_EXPIRE")
    if payload["nonce"] in used_nonces:
        raise HitlError("TOKEN_DEJA_UTILISE")
    if actor_role != payload["required_role"] and actor_role != "DUTY_MANAGER":
        raise HitlError("ROLE_NON_AUTORISE")
    return payload


class Ledger:
    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []
        self.used_nonces: set[str] = set()
        self.prev_hash = "GENESIS"

    def commit(self, token: str, result: dict[str, Any], actor: str, actor_role: str,
               reason: str, when: datetime | None = None) -> dict[str, Any]:
        payload = verify_token(token, result, actor_role, self.used_nonces, when)
        self.used_nonces.add(payload["nonce"])
        record = {
            "ledger_id": f"LED-{len(self.records)+1:04d}",
            "incident_id": result["incident"],
            "decision": result["decision"],
            "status": "APPROVED",
            "result_hash": payload["result_hash"],
            "actor": actor,
            "actor_role": actor_role,
            "reason": reason,
            "nonce": payload["nonce"],
            "decided_at": (when or now_utc()).isoformat(),
            "prev_hash": self.prev_hash,
        }
        record["record_hash"] = sha256_json(record)
        self.prev_hash = record["record_hash"]
        self.records.append(record)
        return record


# ---------------------------------------------------------------------------
# Orchestration M5
# ---------------------------------------------------------------------------

def analyze(pack_path: str | Path, telemetry_path: str | Path, policy_path: str | Path,
            certificates_path: str | Path) -> dict[str, Any]:
    pack = load_json(pack_path)
    policy = load_json(policy_path)
    certificates = load_json(certificates_path)
    telemetry = load_telemetry(telemetry_path)
    ecarts = compute_ecarts(telemetry["verified"], policy["consignes"])
    cert_ok, cert_reason = certificate_ok(pack, certificates)
    decision, motif, quarantine = decide(pack, ecarts, cert_ok, cert_reason, policy, telemetry)
    sources = [e["source"] for e in pack.get("evidence", [])]
    result = build_result(pack, ecarts, decision, policy, sources)
    exposure = compute_exposure(pack, policy)
    hitl = build_hitl(result, policy)
    analysis = {
        "motif": motif,
        "confidence": pack.get("confidence"),
        "exposure": exposure,
        "quarantine": quarantine,
        "untrusted_rows": len(telemetry["quarantine"]),
        "verified_rows": len(telemetry["verified"]),
        "policy_version": policy.get("version", "POL-FROID-1.2"),
        "paths": [p.get("path") for p in pack.get("graph_paths", [])],
    }
    return {"result": result, "analysis": analysis, "hitl": hitl,
            "audit": {"correlation_id": f"6f1c2a9e-{secrets.token_hex(6)}",
                      "quarantine": telemetry["quarantine"]}}


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="M5 B4 decision + HITL")
    parser.add_argument("--pack", default=str(DATA / "mock_b2_pack.json"))
    parser.add_argument("--telemetry", default=str(DATA / "mock_telemetry.csv"))
    parser.add_argument("--policy", default=str(DATA / "policy.json"))
    parser.add_argument("--certificates", default=str(DATA / "certificates.json"))
    args = parser.parse_args(argv)
    out = analyze(args.pack, args.telemetry, args.policy, args.certificates)
    print(json.dumps({"result": out["result"], "analysis": out["analysis"],
                      "hitl": {"required": out["hitl"]["required"], "expires_at": out["hitl"]["expires_at"],
                               "dual_control": out["hitl"]["dual_control"]}},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
