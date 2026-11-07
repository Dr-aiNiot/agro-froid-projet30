# Statut — Projet 30 AGRO-FROID

**Derniere mise a jour : 06/11/2026 13:45**

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

## Finalisation du reste a faire - cloture 06/11/2026

| Chantier | Etat | Preuve |
|---|---|---|
| 18 cas limites du contrat B4 | **Livre** - 42/42 tests OK | `M5/proofs/test_output_full.txt`, `M5/tests/test_edge_cases.py` |
| Outbox : retry, DLQ, rejeu, idempotence | **Livre** - 8/8 verifications OK | `M5/proofs/outbox_delivery.json`, `M5/proofs/dlq_replay.json` |
| Agent Card (2 pages) | **Livre** | `M5/docs/Agent_Card_M5.pdf` + `.json` |
| Durcissement du validateur | **Livre** - refus typÃ© au lieu de crash | `validate_result` insensible aux types inattendus |

Constat de test : une entrÃ©e non textuelle faisait planter le validateur (`TypeError`) au lieu de le refuser proprement. Corrige : desormais `SchemaError` avec code explicite.

Regle de rejeu : la DLQ conserve le payload signe ; le rejeu verifie le hash, ne recalcule pas la decision et ne cree aucun doublon.

## Workflow unique M5 - 06/11/2026 19:00

| Element | Valeur |
|---|---|
| Flux | **M5_B4_DECISION_HITL** (`6656f31f-ad1f-4591-b2ef-0d68c8aa6dad`) |
| Topologie | **6 noeuds / 5 liens** : Entree > Prompt (moteur) > Python > Parseur > **FusionDB (MongoDBQuery)** > Sortie |
| LLM | aucun - moteur deterministe, 0 cle API |
| Mongo | `agro_froid.hitl_pending`, operation `insert_one`, URI en variable plateforme `URI MONGO` |
| Passages | **2 tours dans le meme chat** (voir ci-dessous) |

### Les deux tours (demonstration)

**Tour 1 - decision + demande d'approbation**
Entree `rappel` > RAPPEL / P2_LOT_VENDU / schema 9-9 > FusionDB `insert_one` d'un document
`{type: PENDING_DOSSIER, statut: PENDING, pending_id: MFP-xxxx, instruction: "APPROBATION REQUISE - repondre : APPROVE pending_id=... actor=..."}`.
Le flux s'arrete la, en attente de l'humain.

**Tour 2 - approbation dans le meme chat**
Entree `APPROVE pending_id=MFP-xxxx actor=DRISS_LARHRISSI` > FusionDB `insert_one` d'un document
`{type: APPROVAL, verdict: APPROVE, statut: DONE, actor: ..., token_verifie: true, journal: append-only}`.

Preuves au run (07/11) :
- tour 1 : `pending_id=MFP-724fa931514a2b5a`, `insert_one` OK, instruction presente ;
- tour 2 : `type=APPROVAL`, `verdict=APPROVE`, `statut=DONE`, `inserted_id` retourne ;
- Mongo verifie : 2 PENDING_DOSSIER + 2 APPROVAL dans `agro_froid.hitl_pending`.

Captures : `01_JSON/canvas_M5_B4_DECISION_HITL.png`, `01_JSON/m5_canvas.png`.
Export importable : `01_JSON/M5_B4_DECISION_HITL.json` (6 noeuds / 5 liens).

### Regles plateforme appliquees

- 1 workflow par membre (regle M0 / RunFlow) : les flux F1 et F2 ont ete supprimes ; archive dans `02_ANNEXES/archive_3flux/`.
- Les liens sont persistes et visibles au rechargement (l'id de poignee du noeud Mongo est `MONGO-OUTBOX`, pas l'id du noeud : c'est ce qui faisait elaguer les liens).
- Toujours cliquer sur **Save** (disquette) apres une modification du canvas.

## Validation du 07/11 - captures reelles

| Preuve | Fichier |
|---|---|
| Canvas 6 noeuds / 5 liens avec FusionDB cable | `01_JSON/live_canvas_6n.png` |
| Tour 1 playground (PENDING + inserted_id) | `01_JSON/live_tour1.png` |
| Tour 2 playground (APPROVAL + DONE + inserted_id) | `01_JSON/live_tour2.png` |
| Verification Mongo (pymongo, 7 documents) | `01_JSON/live_mongo_proof.png` + `mongo_dump_0711.txt` |
| CI GitHub Actions (4 runs verts) | `01_JSON/live_ci_github.png` |

Contrainte constatee : le nœud FusionDB ferme son client Mongo apres execution.
Le deuxieme passage exige de recharger le playground (sinon "Cannot use MongoClient
after close"). Protocole detaille dans `M5/docs/Script_Presentation_M5.txt`.

Video : `M5/docs/Demo_M5_Complet.mp4` - 3 min 24, captures reelles (plus de terminaux simules).
