# Statut — Projet 30 AGRO-FROID

**Derniere mise a jour : 06/11/2026 03:40**

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

## M5 — B4 Decision + HITL : 12/12 Done

| Indicateur | Valeur | Preuve |
|---|---|---|
| Tests fonctionnels | **10/10 PASS** | `M5/proofs/test_output.txt` |
| JSON canonique | **9 cles, RETRAIT, HITL REQUIS** | `M5/proofs/result_nominal.json` |
| Faux journal | **detecte, decision non reduite** | `M5/proofs/cases/falsifie_result.json` |
| Token modifie / expire / rejoue | **refuse** | `M5/proofs/test_output.txt` |
| PII en sortie | **0** | test 10 |
| Ledger + outbox | **APPROVED + PENDING** | `M5/proofs/ledger_record.json` |
| Documentation | **5 pages** | `M5/docs/Documentation_M5.pdf` |
| Slides | **2 pages** | `M5/docs/Slides_M5.pdf` |

## Livrables

- Depot : https://github.com/Dr-aiNiot/agro-froid-projet30
- Drive : https://drive.google.com/drive/u/2/folders/1Qqt_aieE6jwBaeMkLvPxduOkUjQJfArD
- Board : `PROJECT_BOARD.md`
- M5 : `M5/README.md` et `M5/STATUS.md`
- Cahier des charges : `00_DOC/Cahier_des_Charges_Projet30_AGRO-FROID.pdf`
- Planning : `01_PLANNING/TODO_PROJET30.csv`
- Preuves : `M5/proofs/`

## GitHub

- 42 issues creees, labels `flow:B0-B4`, milestones J1-J7.
- 12 issues M5 fermees (#1, #5, #9, #10, #35 a #42).
- Invitations envoyees : `amal620`, `Ayman8Da`, `FatimaSaadane26`, `genaiotcasa-lgtm` (pending).
- Les assignations seront appliquees a l'acceptation des invitations.

## ClickUp

- Espace **Projet 30 - AGRO-FROID** cree.
- Folder **Planning M1-M5**, 5 listes, 42 taches.
- 12 taches M5 passees en **complete**.
- Fatima et Salaheddine : **invitations ClickUp envoyées**, membres ajoutés et tâches M2/M4 assignées.

## Reste a faire (hors M5)

- M1 Ayman : B0 orchestration + front.
- M2 Fatima : B1 ingestion + KG.
- M3 Amal : B2 retrieval.
- M4 Salaheddine : B3 securite.
