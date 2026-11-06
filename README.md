# Projet 30 — AGRO-FROID

Agent hybride RAG vectoriel + knowledge graph pour décider d'un retrait ou d'un rappel de lots en moins de 30 minutes.

- **Dépôt GitHub** : https://github.com/Dr-aiNiot/agro-froid-projet30
- **Drive (livrables)** : https://drive.google.com/drive/u/2/folders/1Qqt_aieE6jwBaeMkLvPxduOkUjQJfArD
- **Board / planning** : [PROJECT_BOARD.md](PROJECT_BOARD.md)
- **Rôles** : [ROLES.md](ROLES.md)
- **Invitations** : [COLLABORATORS.md](COLLABORATORS.md)
- **Cahier des charges** : `00_DOC/Cahier_des_Charges_Projet30_AGRO-FROID.pdf`
- **Partie M5 (B4 Décision + HITL)** : [M5/README.md](M5/README.md)
- **Preuves M5** : [M5/proofs/](M5/proofs/)
- **Documentation M5** : `M5/docs/Documentation_M5.pdf`
- **Slides M5** : `M5/docs/Slides_M5.pdf`

## Statut au 06/11/2026 03:40

| Lot | Propriétaire | Statut | Preuve |
|---|---|---|---|
| M5 — B4 Décision + HITL | Driss (M5) | **12/12 Done · 10/10 tests** | `M5/proofs/` + `M5/docs/` |
| M1 — B0 Orchestration + front | Ayman (M1) | Backlog | Issues `flow:B0` |
| M2 — B1 Ingestion + KG | Fatima (M2) | Backlog | Issues `flow:B1` |
| M3 — B2 Retrieval hybride | Amal (M3) | Backlog | Issues `flow:B2` |
| M4 — B3 Sécurité + PII | Salaheddine (M4) | Backlog | Issues `flow:B3` |

## Structure

```
00_DOC/                 cahier des charges complet
01_PLANNING/             CSV des 42 tâches
M5/                     partie M5 livrée
  src/                  code B4 + mocks + génération des preuves
  data/                 pack B2, télémétrie signée, politique, certificats
  tests/                10 tests fonctionnels
  proofs/               JSON, HITL, ledger, outbox, matrice, hashes
  docs/                 documentation 5 pages + 2 slides
PROJECT_BOARD.md        board de secours GitHub
ROLES.md                rôles M1-M5
COLLABORATORS.md        emails et invitations
```

## Rejouer M5

```bash
cd M5
python -m unittest discover -s tests -p "test_*.py" -v
python src/run_demo.py
```

Résultat attendu : `RETRAIT`, `HITL REQUIS`, 2 lots, 2 magasins, 10/10 tests.

## Ce qui est mocké

Le pack B2 (`M5/data/mock_b2_pack.json`), la télémétrie et les certificats sont des mocks contrôlés. Le code B4 est réel : validation de schéma, recalcul du delta, politique P1-P6, exposition, token HITL signé, anti-rejeu, ledger et outbox.
