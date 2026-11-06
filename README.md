# Projet 30 — AGRO-FROID

[![M5 - tests B4](https://github.com/Dr-aiNiot/agro-froid-projet30/actions/workflows/m5-tests.yml/badge.svg)](https://github.com/Dr-aiNiot/agro-froid-projet30/actions/workflows/m5-tests.yml)
[![Release](https://img.shields.io/github/v/release/Dr-aiNiot/agro-froid-projet30?label=release)](https://github.com/Dr-aiNiot/agro-froid-projet30/releases)
[![Tests](https://img.shields.io/badge/tests-42%2F42-brightgreen)](M5/proofs/test_output_full.txt)
[![LLM](https://img.shields.io/badge/LLM-aucun%20dans%20la%20d%C3%A9cision-informational)](M5/docs/Agent_Card_M5.pdf)

Agent hybride RAG vectoriel + knowledge graph pour décider d'un retrait ou d'un rappel de lots en moins de 30 minutes.

- **Dépôt GitHub** : https://github.com/Dr-aiNiot/agro-froid-projet30
- **Drive (livrables)** : https://drive.google.com/drive/u/2/folders/1Qqt_aieE6jwBaeMkLvPxduOkUjQJfArD
- **ClickUp (backlog)** : espace `Projet 30 - AGRO-FROID`, folder `Planning M1-M5` (42 tâches)
- **Board / planning** : [PROJECT_BOARD.md](PROJECT_BOARD.md)
- **Rôles** : [ROLES.md](ROLES.md)
- **Contribuer** : [CONTRIBUTING.md](CONTRIBUTING.md)
- **Invitations** : [COLLABORATORS.md](COLLABORATORS.md)
- **Cahier des charges** : `00_DOC/Cahier_des_Charges_Projet30_AGRO-FROID.pdf`
- **Partie M5 (B4 Décision + HITL)** : [M5/README.md](M5/README.md)
- **Preuves M5** : [M5/proofs/](M5/proofs/)
- **Workflow M5 sur Agentic AI de ABA** : M5_B4_DECISION_HITL (5 noeuds, 4 cas prouves) - export `01_JSON/M5_B4_DECISION_HITL.json`, preuve `M5/proofs/platform_runs.json`
- **Documentation M5** : `M5/docs/Documentation_M5.pdf`
- **Agent Card M5** : `M5/docs/Agent_Card_M5.pdf`
- **Slides M5** : `M5/docs/Slides_M5.pdf`

## Statut au 06/11/2026 13:50

| Lot | Propriétaire | Statut | Preuve |
|---|---|---|---|
| M5 — B4 Décision + HITL | Driss (M5) | **12/12 Done · 42/42 tests** | `M5/proofs/` + `M5/docs/` |
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
  tests/                42 tests (10 fonctionnels + 18 cas limites + 14 outbox/HITL)
  proofs/               JSON, HITL, ledger, outbox, matrice, hashes
  docs/                 documentation 5 pages + Agent Card 2 pages + 2 slides
PROJECT_BOARD.md        board de secours GitHub
ROLES.md                rôles M1-M5
COLLABORATORS.md        emails et invitations
```

## Rejouer M5

```bash
cd M5
python -m unittest discover -s tests -p "test_*.py" -v
python src/run_outbox_demo.py
python src/run_demo.py
```

Résultat attendu : `RETRAIT`, `HITL REQUIS`, 2 lots, 2 magasins, 42/42 tests, 8/8 vérifications outbox.

## Ce qui est mocké

Le pack B2 (`M5/data/mock_b2_pack.json`), la télémétrie et les certificats sont des mocks contrôlés. Le code B4 est réel : validation de schéma, recalcul du delta, politique P1-P6, exposition, token HITL signé, anti-rejeu, ledger et outbox.
