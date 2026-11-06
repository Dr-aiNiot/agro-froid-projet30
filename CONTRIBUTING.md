# Contribuer - Projet 30 AGRO-FROID

## 1. Rejoindre le depot

Une invitation GitHub a ete envoyee a chaque membre. Elle se trouve ici :

- https://github.com/Dr-aiNiot/agro-froid-projet30/invitations
- ou dans la boite mail du compte GitHub concerne (expediteur : GitHub).

Tant que l'invitation n'est pas acceptee, le compte peut lire le depot public
mais **ne peut pas pousser**. Les affectations d'issues sont appliquees apres
acceptation.

| Membre | Lot | Compte GitHub |
|---|---|---|
| Ayman | M1 - B0 orchestration + front | `Ayman8Da` |
| Fatima | M2 - B1 ingestion + graphe | `FatimaSaadane26` |
| Amal | M3 - B2 retrieval | `amal620` |
| Salaheddine | M4 - B3 securite | `genaiotcasa-lgtm` |
| Driss | Lead + M5 B4 decision/HITL | `Dr-aiNiot` |

## 2. Flux de travail

1. Prendre une issue **de son lot** (`flow:B0` a `flow:B3`).
2. Creer une branche : `feat/<lot>-<issue>-<sujet-court>` (ex. `feat/b1-12-parseur-csv`).
3. Commiter en francais, au format `type(scope): message` (`feat`, `fix`, `test`, `docs`, `chore`).
4. Ouvrir une pull request vers `main` et y coller la preuve d'execution.
5. Une tache n'est **Done** que si : contrat respecte, test execute, preuve deposee, issue fermee, statut ClickUp mis a jour.

## 3. Regles de preuve

- Tout resultat annonce doit pointer vers un fichier du depot (JSON, capture, sortie de test).
- Aucun secret en clair : ni cle API, ni mot de passe, ni URI de base avec identifiants.
- Les sorties d'agent sont versionnees dans `M5/proofs/` (ou le dossier de preuve du lot).
- Une decision sans preuve est traitee comme non faite.

## 4. Contrats partages

Les 5 contrats (pack B2, telemetrie signee, politique, certificats, resultat canonique)
sont figes par le lot M5. Personne ne modifie un champ sans passer par une issue `contrat`.

Resultat canonique attendu, 9 cles exactement :
`incident`, `ecarts`, `magasins`, `lots`, `fournisseurs`, `obligation`, `decision`, `hitl`, `sources`.

## 5. Environnement local

```bat
cd M5
python -m unittest discover -s tests -p "test_*.py"
python src/run_outbox_demo.py
```

Python 3.12, aucune dependance externe.

## 6. Questions

Ouvrir une issue avec le label `question` et mentionner le proprietaire du lot.
