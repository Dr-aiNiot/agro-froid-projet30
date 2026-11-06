# Espace Projet 30 — AGRO-FROID

Board de secours GitHub (le Project v2 n'est pas activé faute de scope `project` sur le token). Les 42 tâches sont dans les **Issues**, avec labels, milestones et propriétaires dans le titre.

- Dépôt : https://github.com/Dr-aiNiot/agro-froid-projet30
- Drive : https://drive.google.com/drive/u/2/folders/1Qqt_aieE6jwBaeMkLvPxduOkUjQJfArD
- Issues : https://github.com/Dr-aiNiot/agro-froid-projet30/issues
- ClickUp : espace **Projet 30 - AGRO-FROID**, folder **Planning M1-M5**, 5 listes, 42 tâches.

## Board

| Backlog | Ready | In progress | Review | Done |
|---|---|---|---|---|
| M1 : 6 tâches | M2 : 8 · M3 : 8 · M4 : 8 | — | — | **M5 : 12 tâches** |

## M5 — B4 Décision + HITL (Driss)

| Tâche | Issue | Statut | Preuve |
|---|---|---|---|
| H-01 Validateur du schéma | #35 | **Done** | `M5/src/m5_b4.py` · `validate_result` |
| H-02 Recalcul delta/durée + politique P1-P6 | #36 | **Done** | `M5/proofs/analysis_nominal.json` |
| H-03 Exposition + unresolved | #37 | **Done** | `M5/proofs/analysis_nominal.json` |
| H-04 Package HITL + token signé | #38 | **Done** | `M5/proofs/hitl_package.json` |
| H-05 Commit, ledger, outbox, idempotence | #39 | **Done** | `M5/proofs/ledger_record.json` |
| H-06 Sources, citations, refus | #40 | **Done** | `M5/proofs/result_nominal.json` |
| H-07 Tests B4 + 4 décisions | #41 | **Done** | `M5/proofs/test_output.txt` (10/10) |
| H-08 Agent Card + runbook | #42 | **Done** | `M5/docs/Documentation_M5.pdf` |
| D-01 Contrats + schéma | #1 | **Done** | `M5/src/m5_b4.py` |
| D-05 API HITL | #5 | **Done** | `M5/src/m5_b4.py` · `Ledger.commit` |
| D-09 Démo / captures | #9 | **Done** | `M5/docs/Slides_M5.pdf` |
| D-10 Dossier M5 | #10 | **Done** | `M5/docs/Documentation_M5.pdf` |

## M1 à M4 — état

| Membre | Workflow | Tâches | Statut | Lien |
|---|---|---|---:|---|
| M1 Ayman | B0 Orchestration + front | 6 | Backlog | [issues flow:B0](https://github.com/Dr-aiNiot/agro-froid-projet30/issues?q=label%3Aflow%3AB0) |
| M2 Fatima | B1 Ingestion + KG | 8 | Backlog | [issues flow:B1](https://github.com/Dr-aiNiot/agro-froid-projet30/issues?q=label%3Aflow%3AB1) |
| M3 Amal | B2 Retrieval | 8 | Backlog | [issues flow:B2](https://github.com/Dr-aiNiot/agro-froid-projet30/issues?q=label%3Aflow%3AB2) |
| M4 Salaheddine | B3 Sécurité | 8 | Backlog | [issues flow:B3](https://github.com/Dr-aiNiot/agro-froid-projet30/issues?q=label%3Aflow%3AB3) |

## Jalons

- J1 Cadrage · J2 Verticale · J3 Graphe · J4 HITL · J5 Red Team · J6 Golden+CI · J7 Livraison.

## Règle de mise à jour

Une tâche passe en Done quand : contrat respecté, test exécuté, preuve déposée dans `M5/proofs/` ou `M5/docs/`, issue fermée, statut ClickUp mis à jour.
