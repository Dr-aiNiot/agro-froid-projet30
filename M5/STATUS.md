# M5 — Statut des tâches

| ID | Tâche | Statut | Preuve |
|---|---|---|---|
| D-01 | Figer les contrats et le schéma | **Done** | `src/m5_b4.py` · `validate_result` |
| D-05 | API HITL : token, commit, rejet | **Done** | `src/m5_b4.py` · `Ledger` |
| D-09 | Démo, captures, vidéo | **Done** | `docs/Slides_M5.pdf` |
| D-10 | Dossier M5 | **Done** | `docs/Documentation_M5.pdf` |
| H-01 | Validateur du schéma canonique | **Done** | test 01 + test 08 |
| H-02 | Recalcul delta/durée + politique P1-P6 | **Done** | test 01/02/03/04/09 |
| H-03 | Exposition et lots non résolus | **Done** | `proofs/analysis_nominal.json` |
| H-04 | Package HITL et token signé | **Done** | `proofs/hitl_package.json` |
| H-05 | Commit, ledger, outbox, DLQ, idempotence | **Done** | `proofs/ledger_record.json` · `outbox_records.json` |
| H-06 | Sources, citations et refus | **Done** | `proofs/result_nominal.json` |
| H-07 | Tests B4 et 4 décisions | **Done** | `proofs/test_output.txt` (10/10) |
| H-08 | Agent Card et runbook | **Done** | `docs/Documentation_M5.pdf` (rôle, contrôles, limites) |

## Flux M5 sur Agentic AI de ABA - LIVRE

| Element | Valeur |
|---|---|
| Projet | **Projet 30** (folder `f87f09a0-2c80-46bd-8cd8-8e53a297b12d`) |
| Workflow | **M5_B4_DECISION_HITL** (`6656f31f-ad1f-4591-b2ef-0d68c8aa6dad`) |
| Topologie | 5 noeuds / 4 liens : ChatInput > Prompt moteur B4 > Python > Parser > ChatOutput |
| LLM | **aucun** - moteur deterministe, 0 appel externe, 0 cle API |
| Export | `01_JSON/M5_B4_DECISION_HITL.json` |
| Runs | **4/4** : RETRAIT, RAPPEL, QUARANTAINE, ESCALADE - schema 9 cles OK, HITL requis |
| Preuve | `M5/proofs/platform_runs.json` + `01_JSON/m5_canvas.png` |

**Bilan : 12/12 Done.**
