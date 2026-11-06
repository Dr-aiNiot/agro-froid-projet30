"""M5 - B4 Decision, exposition et HITL : moteur embarque dans le flux Agentic AI de ABA.

Version autonome (aucune lecture de fichier, aucune dependance externe) executee
dans le noeud Python du workflow M5_B4_DECISION_HITL. La logique est identique
a m5_b4.py ; les donnees sont injectees dans CASES.

Entree  : Q = nominal | rappel | quarantaine | escalade (texte libre accepte)
Sortie  : JSON unique {result, analysis, hitl, audit}
"""
import json
import re
import hmac
import hashlib
import base64
import secrets

Q = """{question}"""

POLICY = {
    "version": "POL-FROID-1.2",
    "consignes": {"CF-3": 4.2},
    "seuils": {"delta_c": 2.0, "duree_min": 120, "confidence_min": 0.6},
    "obligation": {"texte": "ONSSA-retrait", "delai_h": 24},
    "exposure": {"seuil_critique": 70, "seuil_eleve": 40},
}

TELEMETRY = [
    ["2026-11-05T09:10:00Z", 8.4, 10421, True],
    ["2026-11-05T09:40:00Z", 8.4, 10422, True],
    ["2026-11-05T10:10:00Z", 8.4, 10423, True],
    ["2026-11-05T10:40:00Z", 8.4, 10424, True],
    ["2026-11-05T11:10:00Z", 8.4, 10425, True],
    ["2026-11-05T11:40:00Z", 8.4, 10426, True],
    ["2026-11-05T12:10:00Z", 8.4, 10427, True],
    ["2026-11-05T12:20:00Z", 8.4, 10428, True],
]

CASES = {
    "nominal": {
        "pack": {
            "anchor": {"type": "Incident", "id": "I-2026-11"},
            "candidates": {"chambres": ["CF-3"], "capteurs": ["C-118", "C-119"],
                           "lots": ["L-8841", "L-8842"], "magasins": ["G-12", "G-19"],
                           "fournisseurs": ["F-07"], "clients_tokenized_count": 128},
            "lots_detail": [
                {"lot_id": "L-8841", "quantite": 300, "vendus": 0, "magasin": "G-12"},
                {"lot_id": "L-8842", "quantite": 200, "vendus": 0, "magasin": "G-19"}],
            "evidence": [
                {"type": "telemetry", "source": "journal_cf3.csv", "score": 1.0},
                {"type": "chunk", "source": "guide_onssa.pdf#p12", "score": 0.82},
                {"type": "chunk", "source": "procedure_interne.pdf#p4", "score": 0.74}],
            "graph_paths": ["I-2026-11 -SURVEILLE-> CF-3 -STOCKE-> L-8841 -LIVRE_A-> G-12",
                            "I-2026-11 -SURVEILLE-> CF-3 -STOCKE-> L-8842 -LIVRE_A-> G-19"],
            "confidence": 0.87,
            "coverage": {"lots": 1.0, "magasins": 1.0, "fournisseurs": 1.0}},
        "cert_valid": True,
        "cert_reason": "CERTIFICAT_VALIDE",
        "telemetry_trusted": True},
    "rappel": {
        "pack": {
            "anchor": {"type": "Incident", "id": "I-2026-11"},
            "candidates": {"chambres": ["CF-3"], "capteurs": ["C-118", "C-119"],
                           "lots": ["L-8841", "L-8842"], "magasins": ["G-12", "G-19"],
                           "fournisseurs": ["F-07"], "clients_tokenized_count": 128},
            "lots_detail": [
                {"lot_id": "L-8841", "quantite": 300, "vendus": 40, "magasin": "G-12"},
                {"lot_id": "L-8842", "quantite": 200, "vendus": 0, "magasin": "G-19"}],
            "evidence": [
                {"type": "telemetry", "source": "journal_cf3.csv", "score": 1.0},
                {"type": "chunk", "source": "guide_onssa.pdf#p12", "score": 0.82},
                {"type": "chunk", "source": "procedure_interne.pdf#p4", "score": 0.74}],
            "graph_paths": ["I-2026-11 -SURVEILLE-> CF-3 -STOCKE-> L-8841 -LIVRE_A-> G-12",
                            "I-2026-11 -SURVEILLE-> CF-3 -STOCKE-> L-8842 -LIVRE_A-> G-19"],
            "confidence": 0.87,
            "coverage": {"lots": 1.0, "magasins": 1.0, "fournisseurs": 1.0}},
        "cert_valid": True,
        "cert_reason": "CERTIFICAT_VALIDE",
        "telemetry_trusted": True},
    "quarantaine": {
        "pack": {
            "anchor": {"type": "Incident", "id": "I-2026-11"},
            "candidates": {"chambres": ["CF-3"], "capteurs": ["C-118", "C-119"],
                           "lots": ["L-8841", "L-8842"], "magasins": ["G-12", "G-19"],
                           "fournisseurs": ["F-07"], "clients_tokenized_count": 128},
            "lots_detail": [
                {"lot_id": "L-8841", "quantite": 300, "vendus": 0, "magasin": "G-12"},
                {"lot_id": "L-8842", "quantite": 200, "vendus": 0, "magasin": "G-19"}],
            "evidence": [
                {"type": "telemetry", "source": "journal_cf3.csv", "score": 1.0},
                {"type": "chunk", "source": "guide_onssa.pdf#p12", "score": 0.82},
                {"type": "chunk", "source": "procedure_interne.pdf#p4", "score": 0.74}],
            "graph_paths": ["I-2026-11 -SURVEILLE-> CF-3 -STOCKE-> L-8841 -LIVRE_A-> G-12",
                            "I-2026-11 -SURVEILLE-> CF-3 -STOCKE-> L-8842 -LIVRE_A-> G-19"],
            "confidence": 0.87,
            "coverage": {"lots": 1.0, "magasins": 1.0, "fournisseurs": 1.0}},
        "cert_valid": False,
        "cert_reason": "CERTIFICAT_INVALIDE_F-07",
        "telemetry_trusted": True},
    "escalade": {
        "pack": {
            "anchor": {"type": "Incident", "id": "I-2026-11"},
            "candidates": {"chambres": ["CF-3"], "capteurs": ["C-118", "C-119"],
                           "lots": ["L-8841", "L-8842"], "magasins": ["G-12", "G-19"],
                           "fournisseurs": ["F-07"], "clients_tokenized_count": 128},
            "lots_detail": [
                {"lot_id": "L-8841", "quantite": 300, "vendus": 0, "magasin": "G-12"},
                {"lot_id": "L-8842", "quantite": 200, "vendus": 0, "magasin": "G-19"}],
            "evidence": [
                {"type": "telemetry", "source": "journal_cf3.csv", "score": 1.0},
                {"type": "chunk", "source": "guide_onssa.pdf#p12", "score": 0.82}],
            "graph_paths": ["I-2026-11 -SURVEILLE-> CF-3 -STOCKE-> L-8841 -LIVRE_A-> G-12"],
            "confidence": 0.50,
            "coverage": {"lots": 1.0, "magasins": 1.0, "fournisseurs": 0.0}},
        "cert_valid": True,
        "cert_reason": "CERTIFICAT_VALIDE",
        "telemetry_trusted": True},
}

REQUIRED = ["incident", "ecarts", "magasins", "lots", "fournisseurs",
            "obligation", "decision", "hitl", "sources"]
DECISIONS = {"RETRAIT", "RAPPEL", "QUARANTAINE", "SURVEILLANCE", "ESCALADE"}
SECRET = b"AGRO-FROID-DEMO-HMAC-KEY-2026"


def main(Q=Q, CASES=CASES, POLICY=POLICY, TELEMETRY=TELEMETRY):
    from datetime import datetime as _dt, timedelta as _td, timezone as _tz
    key = (Q or "").strip().lower()
    if key not in CASES:
        key = "nominal"
    case = CASES[key]
    pack = case["pack"]
    policy = POLICY
    consigne = policy["consignes"]["CF-3"]

    # H-02 : ecarts recalcules depuis la telemetrie verifiee
    rows = [r for r in TELEMETRY if r[3]] if case["telemetry_trusted"] else []
    ecarts = []
    if rows:
        delta = round(max(r[1] for r in rows) - consigne, 1)
        t0 = rows[0][0]
        t1 = rows[-1][0]
        d0 = _dt.strptime(t0, "%Y-%m-%dT%H:%M:%SZ")
        d1 = _dt.strptime(t1, "%Y-%m-%dT%H:%M:%SZ")
        duree = int((d1 - d0).total_seconds() / 60)
        if delta > 0:
            ecarts = [{"chambre": "CF-3", "delta_c": delta, "duree_min": duree}]

    # H-03 : exposition
    details = pack["lots_detail"]
    n_mag = len(set(d["magasin"] for d in details))
    f_mag = 1.0 if n_mag <= 1 else (1.2 if n_mag == 2 else 1.4)
    f_delai = 1.5 if policy["obligation"]["delai_h"] < 24 else 1.0
    total = 0.0
    for d in details:
        q = float(d["quantite"])
        vendus = float(d["vendus"])
        f_vente = 1 + min(vendus / q, 1.0) if q > 0 else 1.0
        total += q * f_mag * f_vente * f_delai
    score = min(100.0, round(100.0 * total / 1000.0, 1))
    niveau = ("CRITIQUE" if score >= policy["exposure"]["seuil_critique"]
              else ("ELEVE" if score >= policy["exposure"]["seuil_eleve"] else "MODERE"))
    exposure = {"score": score, "niveau": niveau, "lots": len(details),
                "magasins": n_mag,
                "clients_tokenized": int(pack["candidates"].get("clients_tokenized_count", 0)),
                "f_magasin": f_mag, "f_delai": f_delai, "total_brut": round(total, 1)}

    # H-02 : politique P1-P6
    if not rows:
        decision, motif, quarantined = "ESCALADE", "E_NO_VERIFIED_TELEMETRY", True
    elif not ecarts:
        decision, motif, quarantined = "ESCALADE", "E_NO_ECART_VERIFIE", True
    elif pack.get("confidence", 0) < policy["seuils"]["confidence_min"]:
        decision, motif, quarantined = "ESCALADE", "E_LOW_CONFIDENCE", False
    elif not case["cert_valid"]:
        decision, motif, quarantined = "QUARANTAINE", case["cert_reason"], True
    elif ecarts[0]["delta_c"] >= policy["seuils"]["delta_c"] and ecarts[0]["duree_min"] >= policy["seuils"]["duree_min"]:
        vendus = sum(int(d["vendus"]) for d in details)
        if vendus > 0:
            decision, motif, quarantined = "RAPPEL", "P2_LOT_VENDU", False
        else:
            decision, motif, quarantined = "RETRAIT", "P1_DELTA_DUREE", False
    else:
        decision, motif, quarantined = "SURVEILLANCE", "P6_SOUS_SEUIL", False

    result = {
        "incident": pack["anchor"]["id"],
        "ecarts": ecarts,
        "magasins": pack["candidates"]["magasins"],
        "lots": pack["candidates"]["lots"],
        "fournisseurs": pack["candidates"]["fournisseurs"],
        "obligation": {"texte": policy["obligation"]["texte"],
                       "delai_h": int(policy["obligation"]["delai_h"])},
        "decision": decision,
        "hitl": "REQUIS" if decision in {"RETRAIT", "RAPPEL", "QUARANTAINE", "ESCALADE"} else "NON_REQUIS",
        "sources": [e["source"] for e in pack.get("evidence", [])][:8],
    }

    # H-01 : validateur du schema canonique (9 cles, ni plus ni moins)
    checks = []
    checks.append(("C1_9_CLES", sorted(result.keys()) == sorted(REQUIRED)))
    checks.append(("C2_INCIDENT", bool(re.match(r"^I-\d{4}-\d{2}$", result["incident"]))))
    checks.append(("C3_ECARTS", bool(result["ecarts"]) or result["decision"] == "ESCALADE"))
    checks.append(("C4_MAGASINS", bool(result["magasins"]) and all(re.match(r"^G-\d+$", x) for x in result["magasins"])))
    checks.append(("C5_LOTS", bool(result["lots"]) and all(re.match(r"^L-\d+$", x) for x in result["lots"])))
    checks.append(("C6_FOURNISSEURS", bool(result["fournisseurs"]) and all(re.match(r"^F-\d+$", x) for x in result["fournisseurs"])))
    checks.append(("C7_OBLIGATION", set(result["obligation"].keys()) == {"texte", "delai_h"}))
    checks.append(("C8_DECISION", result["decision"] in DECISIONS))
    checks.append(("C9_HITL", result["hitl"] in {"REQUIS", "NON_REQUIS"}))
    checks.append(("C10_SOURCES", 1 <= len(result["sources"]) <= 8))
    schema_ok = all(v for _, v in checks)

    # H-04 : package HITL signe (HMAC-SHA256, nonce, expiry 30 min)
    now = _dt.now(_tz.utc)
    result_bytes = json.dumps(result, ensure_ascii=False, sort_keys=True).encode("utf-8")
    result_hash = hashlib.sha256(result_bytes).hexdigest()
    payload = {
        "incident_id": result["incident"],
        "decision": result["decision"],
        "result_hash": result_hash,
        "nonce": secrets.token_hex(8),
        "issued_at": now.isoformat(),
        "expires_at": (now + _td(minutes=30)).isoformat(),
        "required_role": "QUALITY_MANAGER",
        "dual_control": result["decision"] == "RAPPEL",
    }
    p64 = base64.urlsafe_b64encode(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).decode().rstrip("=")
    sig = base64.urlsafe_b64encode(hmac.new(SECRET, p64.encode(), hashlib.sha256).digest()).decode().rstrip("=")
    token = p64 + "." + sig

    out = {
        "case": key,
        "result": result,
        "analysis": {
            "motif": motif,
            "confidence": pack.get("confidence"),
            "exposure": exposure,
            "quarantine": quarantined,
            "verified_rows": len(rows),
            "policy_version": policy["version"],
            "paths": pack.get("graph_paths", []),
            "schema_ok": schema_ok,
            "schema_checks": [{"id": cid, "ok": ok} for cid, ok in checks],
        },
        "hitl": {
            "required": result["hitl"] == "REQUIS",
            "token": token,
            "payload": payload,
            "expires_at": payload["expires_at"],
            "required_role": payload["required_role"],
            "dual_control": payload["dual_control"],
        },
        "audit": {"correlation_id": "COR-" + hashlib.sha256((key + result_hash).encode()).hexdigest()[:12],
                  "engine": "M5-B4 deterministic", "llm_used": False},
    }
    print("RESULT_M5: " + json.dumps(out, ensure_ascii=False))


main()
