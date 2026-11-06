"""Genere les journaux de telemetrie signes pour les tests M5."""
from __future__ import annotations

import csv
from pathlib import Path

from m5_b4 import sign_row

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

BASE = [
    ("2026-11-05T09:10:00Z", 8.4),
    ("2026-11-05T09:40:00Z", 8.4),
    ("2026-11-05T10:10:00Z", 8.4),
    ("2026-11-05T10:40:00Z", 8.4),
    ("2026-11-05T11:10:00Z", 8.4),
    ("2026-11-05T11:40:00Z", 8.4),
    ("2026-11-05T12:10:00Z", 8.4),
    ("2026-11-05T12:20:00Z", 8.4),
]


def write(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["ts", "chambre", "capteur", "temp_c", "seq", "key_id", "hmac"])
        w.writeheader()
        w.writerows(rows)


def build(temp_override: dict[int, float] | None = None, sign_as: float = 8.4) -> list[dict]:
    rows = []
    for i, (ts, temp) in enumerate(BASE, start=10421):
        actual = temp_override.get(i, temp) if temp_override else temp
        rows.append({
            "ts": ts, "chambre": "CF-3", "capteur": "C-118", "temp_c": f"{actual:.1f}",
            "seq": i, "key_id": "K-CF3-01",
            "hmac": sign_row(ts, "CF-3", "C-118", sign_as, i),
        })
    return rows


write(DATA / "mock_telemetry.csv", build())
# Une ligne falsifiee : 4.0 C mais HMAC calcule sur 8.4 C -> signature invalide.
write(DATA / "mock_telemetry_falsified.csv", build(temp_override={10421: 4.0}))
# Tout le journal est falsifie -> aucune ligne verifiee -> escalade.
write(DATA / "mock_telemetry_all_false.csv", build(temp_override={i: 4.0 for i in range(10421, 10429)}))
print("telemetry written")
