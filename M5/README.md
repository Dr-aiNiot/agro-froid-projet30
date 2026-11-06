# M5 — B4 Décision, exposition et HITL

Propriétaire : **Driss Larhrissi (M5)** · Workflow **B4** · Projet 30 AGRO-FROID.

## Ce que fait M5

Transforme un pack de preuves B2 en :

1. un **JSON canonique** de 9 clés (`RETRAIT`, `HITL REQUIS`, 2 lots, 2 magasins, F-07) ;
2. un calcul d'**exposition** (score 60/100, niveau ELEVE) ;
3. un **package HITL signé** (hash du résultat, nonce, expiration 30 min, rôle) ;
4. un **ledger append-only** et une **outbox** idempotente.

## Résultat nominal

```json
{"incident":"I-2026-11","ecarts":[{"chambre":"CF-3","delta_c":4.2,"duree_min":190}],"magasins":["G-12","G-19"],"lots":["L-8841","L-8842"],"fournisseurs":["F-07"],"obligation":{"texte":"ONSSA-retrait","delai_h":24},"decision":"RETRAIT","hitl":"REQUIS","sources":["journal_cf3.csv","guide_onssa.pdf#p12","procedure_interne.pdf#p4"]}
```

## Tests

**10/10 PASS** — `python -m unittest discover -s tests -p "test_*.py" -v`

| Test | Vérifie |
|---|---|
| 01 | Nominal RETRAIT, JSON 9 clés |
| 02 | RAPPEL si lot vendu + double contrôle |
| 03 | Certificat invalide → ESCALADE + quarantaine |
| 04 | Confiance < 0,60 → ESCALADE |
| 05 | Token modifié → SIGNATURE_INVALIDE |
| 06 | Token expiré → TOKEN_EXPIRE |
| 07 | Rejeu → TOKEN_DEJA_UTILISE |
| 08 | Schéma invalide → SchemaError |
| 09 | Faux journal → RETRAIT maintenu ; tout faux → ESCALADE |
| 10 | Aucune PII en sortie |

## Rejouer

```bash
cd M5
python -m unittest discover -s tests -p "test_*.py" -v
python src/run_demo.py
```

## Preuves

- `proofs/result_nominal.json`
- `proofs/hitl_package.json`
- `proofs/ledger_record.json`
- `proofs/outbox_records.json`
- `proofs/traceability_matrix.csv`
- `proofs/test_report.json`
- `proofs/test_output.txt`
- `proofs/cases/` (7 scénarios)
- `proofs/hashes.txt`

## Documentation

- `docs/Documentation_M5.pdf` (5 pages)
- `docs/Slides_M5.pdf` (2 slides)

## Limites

Le pack B2, la télémétrie et les certificats sont des mocks. Le token utilise un secret de démonstration. Le double contrôle RAPPEL est modélisé dans le payload ; l'écran deux acteurs reste à câbler. DLQ/outbox sont simulés en JSON.
