from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOFS = ROOT / "proofs"
DOCS = ROOT / "docs"
DOCS.mkdir(parents=True, exist_ok=True)

result = json.loads((PROOFS / "result_nominal.json").read_text(encoding="utf-8"))
analysis = json.loads((PROOFS / "analysis_nominal.json").read_text(encoding="utf-8"))
ledger = json.loads((PROOFS / "ledger_record.json").read_text(encoding="utf-8"))
report = json.loads((PROOFS / "test_report.json").read_text(encoding="utf-8"))
trace = list(csv.DictReader((PROOFS / "traceability_matrix.csv").open(encoding="utf-8-sig"), delimiter=";"))
hashes = (PROOFS / "hashes.txt").read_text(encoding="utf-8").splitlines()
result_json = json.dumps(result, ensure_ascii=False, indent=2)
analysis_json = json.dumps(analysis, ensure_ascii=False, indent=2)
ledger_json = json.dumps(ledger, ensure_ascii=False, indent=2)
result_compact = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
ledger_compact = json.dumps({"ledger_id": ledger["ledger_id"], "decision": ledger["decision"], "status": ledger["status"], "actor": ledger["actor"], "actor_role": ledger["actor_role"], "result_hash": "sha256:...", "nonce": "...", "record_hash": "...", "prev_hash": ledger["prev_hash"]}, ensure_ascii=False, separators=(",", ":"))

trace_rows = "".join(
    f"<tr><td>{r['Requirement']}</td><td>{r['Test']}</td><td><code>{r['Evidence']}</code></td><td><b>{r['Status']}</b></td></tr>"
    for r in trace
)
hash_rows = "".join(f"<tr><td><code>{h[:16]}…</code></td><td><code>{h[66:]}</code></td></tr>" for h in hashes[:5])

CSS = """
:root{--navy:#0b1f3a;--orange:#f59e0b;--ink:#1f2937;--muted:#5b6778;--line:#d8dee8;--bg:#f6f8fb;--green:#0f766e;--red:#b91c1c}
*{box-sizing:border-box}html,body{margin:0;padding:0;background:#fff}
body{font-family:"Segoe UI","Calibri",Arial,sans-serif;font-size:9.1pt;line-height:1.36;color:var(--ink)}
@page{size:A4;margin:14mm 13mm 14mm 13mm}
@media print{.page{break-after:page}.page:last-child{break-after:auto}h2,h3{break-after:avoid}tr{break-inside:avoid}}
.page{min-height:250mm;position:relative}
h1{font-size:22pt;color:var(--navy);margin:0 0 4px;line-height:1.1}
h2{font-size:14pt;color:var(--navy);margin:14px 0 6px;padding:6px 0 6px 10px;border-left:5px solid var(--orange);background:linear-gradient(90deg,#eef3f9,#fff)}
h3{font-size:11pt;color:var(--navy);margin:10px 0 4px}
p{margin:0 0 6px}ul,ol{margin:3px 0 6px 16px;padding:0}li{margin:1px 0}
table{width:100%;border-collapse:collapse;margin:5px 0 8px;font-size:7.9pt}
th{background:var(--navy);color:#fff;text-align:left;padding:4px 5px;font-weight:600}
td{border-bottom:1px solid var(--line);padding:3px 5px;vertical-align:top}
tr:nth-child(even) td{background:#fafbfd}
code,pre{font-family:Consolas,monospace}code{font-size:7.8pt;background:#eef2f7;padding:1px 3px;border-radius:2px}
pre{background:var(--navy);color:#e7eef8;padding:7px;font-size:7pt;line-height:1.35;white-space:pre-wrap;overflow-wrap:anywhere;border-radius:3px}
.kicker{font-size:7.6pt;letter-spacing:1.6px;color:#b45309;font-weight:700;text-transform:uppercase}
.hero{background:linear-gradient(150deg,#0b1f3a,#1b3760);color:#fff;padding:16px 18px;border-radius:5px;margin-bottom:10px}
.hero h1{color:#fff;font-size:24pt;margin:2px 0}.hero .sub{color:#dbe7f7;font-size:10.5pt}
.badge{display:inline-block;border:1px solid rgba(255,255,255,.35);border-radius:12px;padding:2px 8px;font-size:7.2pt;margin:2px 3px 0 0}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px}
.card{border:1px solid var(--line);border-radius:4px;padding:7px;background:#fff}
.card .n{font-size:16pt;font-weight:700;color:var(--navy);display:block;line-height:1.1}
.card .l{font-size:6.8pt;color:var(--muted);text-transform:uppercase;letter-spacing:.3px}
.callout{border-left:4px solid var(--orange);background:#fff8eb;padding:7px 9px;margin:7px 0;border-radius:0 3px 3px 0}
.callout.ok{border-left-color:var(--green);background:#ecfdf5}.callout.red{border-left-color:var(--red);background:#fef2f2}
.flow{display:flex;align-items:center;gap:4px;flex-wrap:wrap;margin:6px 0 8px}
.step{border:1px solid #94a3b8;background:#f8fafc;border-radius:4px;padding:5px 6px;font-size:7.4pt;min-width:72px;text-align:center}
.step.hot{border-color:var(--orange);background:#fff8eb}.step.ok{border-color:var(--green);background:#ecfdf5}
.arrow{color:var(--orange);font-weight:700}
.small{font-size:7.4pt;color:var(--muted)}
.footer{position:absolute;bottom:0;left:0;right:0;font-size:6.8pt;color:#8391a5;border-top:1px solid var(--line);padding-top:2px;display:flex;justify-content:space-between}
"""

DOC = f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><title>M5 — Documentation technique</title><style>{CSS}</style></head><body>

<section class="page">
<div class="hero">
  <div class="kicker">Projet 30 · AGRO-FROID · M5</div>
  <h1>B4 — Décision, exposition et HITL</h1>
  <div class="sub">Documentation technique · preuves · audit fonctionnel · traçabilité</div>
  <div style="margin-top:6px">
    <span class="badge">M5 · Driss</span><span class="badge">10/10 tests</span>
    <span class="badge">JSON 9 clés</span><span class="badge">0 PII</span><span class="badge">HITL signé</span>
  </div>
</div>

<h2>1. Rôle et périmètre</h2>
<p><b>M5 = B4</b> : transformer un pack de preuves B2 en une décision traçable, un JSON canonique, un calcul d'exposition et un package HITL signé. B4 ne planifie pas, ne cherche pas et ne rédige pas : il vérifie, calcule, applique la politique et prépare l'action humaine.</p>
<table>
<tr><th style="width:22%">Élément</th><th>Contenu</th></tr>
<tr><td>Entrée</td><td><code>mock_b2_pack.json</code> : ancre I-2026-11, 2 lots, 2 magasins, F-07, 3 preuves, confiance 0,87 ; télémétrie signée ; politique P1-P6 ; certificats.</td></tr>
<tr><td>Traitement</td><td>Vérification HMAC, recalcul delta/durée, contrôle certificat, politique, exposition, validation du schéma, token HITL, ledger, outbox.</td></tr>
<tr><td>Sortie</td><td>JSON canonique 9 clés + <code>analysis</code> (motif, exposition, quarantaine) + <code>hitl</code> (token, expiry, rôle, double contrôle).</td></tr>
<tr><td>Décision nominale</td><td><b>{result['decision']}</b> · HITL <b>{result['hitl']}</b> · {len(result['lots'])} lots · {len(result['magasins'])} magasins · fournisseur {result['fournisseurs'][0]}</td></tr>
</table>

<div class="grid3">
  <div class="card"><span class="n">10/10</span><span class="l">Tests fonctionnels</span></div>
  <div class="card"><span class="n">4,2 °C</span><span class="l">Delta recalculé / 190 min</span></div>
  <div class="card"><span class="n">0</span><span class="l">PII en sortie</span></div>
</div>

<div class="callout ok"><b>Règle de non-réduction.</b> Une ligne de journal non signée ne peut jamais réduire la sévérité. Le test 09 le prouve : le faux log à 4,0 °C est mis en quarantaine, la décision reste RETRAIT ; si tout le journal est faux, B4 escalade.</div>

<h2>2. Entrées / sorties attendues</h2>
<table>
<tr><th style="width:24%">Champ</th><th style="width:16%">Type</th><th>Valeur / contrainte</th></tr>
<tr><td><code>result.incident</code></td><td>string</td><td><code>I-2026-11</code> · format <code>I-AAAA-MM</code></td></tr>
<tr><td><code>result.ecarts[]</code></td><td>array</td><td><code>{{"chambre":"CF-3","delta_c":4.2,"duree_min":190}}</code></td></tr>
<tr><td><code>result.magasins / lots / fournisseurs</code></td><td>array</td><td>G-12, G-19 / L-8841, L-8842 / F-07</td></tr>
<tr><td><code>result.obligation</code></td><td>object</td><td><code>{{"texte":"ONSSA-retrait","delai_h":24}}</code></td></tr>
<tr><td><code>result.decision / hitl</code></td><td>enum</td><td>RETRAIT / RAPPEL / SURVEILLANCE / ESCALADE · REQUIS / NON_REQUIS</td></tr>
<tr><td><code>result.sources[]</code></td><td>array</td><td>1 à 8 · <code>journal_cf3.csv</code>, <code>guide_onssa.pdf#p12</code>, <code>procedure_interne.pdf#p4</code></td></tr>
</table>
<pre>{result_compact}</pre>
<div class="footer"><span>M5 — Documentation technique</span><span>Page 1 / 5</span></div>
</section>

<section class="page">
<h2>3. Architecture B4 et machine HITL</h2>
<div class="flow">
  <div class="step">Pack B2<br>preuves</div><span class="arrow">→</span>
  <div class="step hot">Vérifier<br>télémétrie HMAC</div><span class="arrow">→</span>
  <div class="step">Recalcul<br>delta / durée</div><span class="arrow">→</span>
  <div class="step">Certificat<br>fournisseur</div><span class="arrow">→</span>
  <div class="step">Politique<br>P1-P6</div><span class="arrow">→</span>
  <div class="step">Exposition<br>score</div><span class="arrow">→</span>
  <div class="step ok">JSON<br>canonique</div><span class="arrow">→</span>
  <div class="step hot">Package<br>HITL signé</div>
</div>
<p>Le chemin est volontairement linéaire et déterministe. Aucun LLM n'intervient dans B4. Les seules sources de vérité sont la télémétrie vérifiée, la politique versionnée et le registre des certificats.</p>

<table>
<tr><th style="width:22%">Contrôle</th><th>Mise en œuvre</th><th style="width:24%">Preuve</th></tr>
<tr><td>Authenticité</td><td>HMAC-SHA256 par ligne, clé identifiée, séquence, quarantaine des lignes invalides</td><td><code>cases/falsifie_analysis.json</code></td></tr>
<tr><td>Non-réduction</td><td>Un journal non fiable ne peut pas annuler une alerte ; s'il est la seule source, escalade</td><td>test 09</td></tr>
<tr><td>Certificat</td><td>Présence, validité, émetteur, liaison certificat ↔ lot</td><td>test 03</td></tr>
<tr><td>Politique</td><td>P1 delta ≥ 2 °C et durée ≥ 120 min ; P2 lot vendu ; P3 certificat ; P5 confiance &lt; 0,60</td><td><code>cases/*_analysis.json</code></td></tr>
<tr><td>HITL</td><td>Token signé, hash du résultat, nonce, expiration 30 min, rôle, double contrôle si RAPPEL</td><td><code>hitl_package.json</code></td></tr>
<tr><td>Ledger</td><td>Enregistrement append-only, hash du précédent, acteur, motif</td><td><code>ledger_record.json</code></td></tr>
</table>

<h3>Machine à états HITL</h3>
<table>
<tr><th style="width:16%">État</th><th style="width:34%">Déclencheur</th><th>Transition</th></tr>
<tr><td>PROPOSED</td><td>B4 a calculé la décision</td><td>HITL requis → PENDING_HITL ; sinon COMMITTED</td></tr>
<tr><td>PENDING_HITL</td><td>Package émis</td><td>Approbation → APPROVED ; rejet → REJECTED ; 30 min → EXPIRED</td></tr>
<tr><td>APPROVED</td><td>Token valide, rôle correct, nonce neuf</td><td>Écriture ledger + outbox → COMMITTED</td></tr>
<tr><td>REJECTED / EXPIRED</td><td>Motif ou délai</td><td>Nouveau package possible, nonce différent</td></tr>
</table>
<div class="callout red"><b>Anti-rejeu.</b> Le token contient le hash du résultat et un nonce à usage unique. Modifier le token, rejouer le token ou changer le résultat produit une erreur : <code>SIGNATURE_INVALIDE</code>, <code>TOKEN_DEJA_UTILISE</code> ou <code>RESULTAT_MODIFIE</code>.</div>

<h3>Exposition</h3>
<p><code>E_lot = quantite × f_magasin × f_vente × f_delai</code>. Score nominal : <b>{analysis['exposure']['score']}/100</b> ({analysis['exposure']['niveau']}), {analysis['exposure']['lots']} lots, {analysis['exposure']['magasins']} magasins, {analysis['exposure']['clients_tokenized']} clients tokenisés. Le score sert à prioriser ; la décision vient de la politique.</p>
<div class="footer"><span>M5 — Documentation technique</span><span>Page 2 / 5</span></div>
</section>

<section class="page">
<h2>4. Stack technique et choix</h2>
<table>
<tr><th style="width:16%">Technologie</th><th style="width:20%">Rôle</th><th style="width:30%">Pourquoi</th><th style="width:18%">Alternative</th><th style="width:16%">Risque</th></tr>
<tr><td>Python 3.12</td><td>Moteur B4</td><td>Standard, lisible, testable, aucune dépendance</td><td>Node.js</td><td>Faible</td></tr>
<tr><td>HMAC-SHA256</td><td>Signature lignes + token</td><td>Standard, rapide, constant-time compare</td><td>Ed25519</td><td>Clé de démo en dur ; production = coffre</td></tr>
<tr><td>JSON / CSV</td><td>Contrats et données</td><td>Formats du sujet, auditables</td><td>Protobuf</td><td>Faible</td></tr>
<tr><td>unittest</td><td>10 tests fonctionnels</td><td>Zéro installation, reproductible</td><td>pytest</td><td>Faible</td></tr>
<tr><td>GitHub</td><td>Repo, issues, board</td><td>Traçabilité, revue, historique</td><td>ClickUp seul</td><td>Invitations pending</td></tr>
<tr><td>ClickUp</td><td>Planning M1-M5</td><td>Suivi d'avancement équipe</td><td>Jira</td><td>API invite Enterprise</td></tr>
<tr><td>Edge headless</td><td>PDF doc + slides</td><td>Rendu identique au HTML, zéro installation</td><td>LaTeX</td><td>Faible</td></tr>
</table>

<h3>Décisions structurantes</h3>
<ol>
<li><b>B4 déterministe.</b> Un LLM peut proposer, pas calculer un delta, une exposition ou une signature. T=0 ne suffit pas ; le code est la source de vérité.</li>
<li><b>Pas de dépendance externe.</b> Le jury peut rejouer M5 avec Python seul, sans clé API, sans réseau, sans Mongo.</li>
<li><b>HITL structurel.</b> Le token n'est pas un bouton : il est signé, lié au résultat, expirant et à usage unique.</li>
<li><b>Preuves reproductibles.</b> Chaque test écrit un artifact JSON et un hash. La matrice de traçabilité relie exigence, test et preuve.</li>
</ol>

<div class="callout"><b>Ce qui est mocké et ce qui ne l'est pas.</b> Le pack B2, la télémétrie et les certificats sont des mocks contrôlés. Le code B4, la politique, le token, le ledger et les tests sont réels. Le mock permet de tester sans attendre B1/B2/B0.</div>

<h3>Coût et performance</h3>
<table>
<tr><th>Poste</th><th>Valeur</th></tr>
<tr><td>Dépendances</td><td>0 (stdlib Python)</td></tr>
<tr><td>Temps des 10 tests</td><td>0,067 s</td></tr>
<tr><td>Coût LLM B4</td><td>0 € (aucun appel LLM)</td></tr>
<tr><td>Artefacts de preuve</td><td>21 fichiers JSON/CSV/TXT</td></tr>
</table>
<div class="footer"><span>M5 — Documentation technique</span><span>Page 3 / 5</span></div>
</section>

<section class="page">
<h2>5. Audit fonctionnel et traçabilité</h2>
<table>
<tr><th style="width:8%">ID</th><th style="width:38%">Test</th><th style="width:34%">Attendu</th><th style="width:20%">Résultat</th></tr>
<tr><td>T01</td><td>Nominal : RETRAIT, 2 lots, 2 magasins, F-07</td><td>JSON 9 clés, HITL REQUIS</td><td><b>PASS</b></td></tr>
<tr><td>T02</td><td>Lot vendu</td><td>RAPPEL + double contrôle</td><td><b>PASS</b></td></tr>
<tr><td>T03</td><td>Certificat invalide</td><td>ESCALADE + quarantaine</td><td><b>PASS</b></td></tr>
<tr><td>T04</td><td>Confiance &lt; 0,60</td><td>ESCALADE</td><td><b>PASS</b></td></tr>
<tr><td>T05</td><td>Token modifié</td><td>SIGNATURE_INVALIDE</td><td><b>PASS</b></td></tr>
<tr><td>T06</td><td>Token expiré</td><td>TOKEN_EXPIRE</td><td><b>PASS</b></td></tr>
<tr><td>T07</td><td>Rejeu du token</td><td>TOKEN_DEJA_UTILISE</td><td><b>PASS</b></td></tr>
<tr><td>T08</td><td>Schéma invalide</td><td>SchemaError</td><td><b>PASS</b></td></tr>
<tr><td>T09</td><td>Journal falsifié / tout faux</td><td>RETRAIT maintenu / ESCALADE</td><td><b>PASS</b></td></tr>
<tr><td>T10</td><td>Aucune PII en sortie</td><td>0 token, 0 email, 0 carte</td><td><b>PASS</b></td></tr>
</table>
<p><b>Résultat global : {report['passed']}/{report['tests']} PASS · {report['status']}</b> · commande <code>{report['command']}</code>.</p>

<h3>Matrice de traçabilité</h3>
<table>
<tr><th style="width:10%">Exigence</th><th style="width:38%">Test</th><th style="width:36%">Preuve</th><th style="width:16%">Statut</th></tr>
{trace_rows}
</table>
<div class="footer"><span>M5 — Documentation technique</span><span>Page 4 / 5</span></div>
</section>

<section class="page">
<h2>6. Preuves et résultats</h2>
<div class="grid">
<div class="card"><h3 style="margin-top:0">Résultat canonique</h3><pre>{result_compact}</pre></div>
<div class="card"><h3 style="margin-top:0">Ledger HITL</h3><pre>{ledger_compact}</pre></div>
</div>

<p><b>Motif :</b> {analysis['motif']} · <b>Exposition :</b> {analysis['exposure']['score']}/100 ({analysis['exposure']['niveau']}) · <b>Lignes non fiables :</b> {analysis['untrusted_rows']} · <b>Lignes vérifiées :</b> {analysis['verified_rows']}</p>

<h3>Empreintes SHA-256</h3>
<table><tr><th style="width:18%">Hash</th><th>Fichier</th></tr>{hash_rows}</table>

<h3>Limites et suite</h3>
<ul>
<li>Le pack B2, la télémétrie et les certificats sont des mocks ; le branchement réel se fait par contrat, sans modifier B4.</li>
<li>Le token utilise un secret de démonstration ; en production, clé dans un coffre et rotation.</li>
<li>Le double contrôle RAPPEL est modélisé dans le payload ; l'écran deux acteurs reste à câbler.</li>
<li>DLQ et outbox sont simulés en JSON ; le retry réel sera branché avec B0.</li>
</ul>

<h3>Liens</h3>
<table>
<tr><td>GitHub</td><td><code>https://github.com/Dr-aiNiot/agro-froid-projet30</code></td></tr>
<tr><td>Issues M5</td><td><code>https://github.com/Dr-aiNiot/agro-froid-projet30/issues?q=label%3Aflow%3AB4</code></td></tr>
<tr><td>ClickUp B4</td><td><code>https://app.clickup.com/90152674771/v/li/1200380000011340</code></td></tr>
<tr><td>Preuves</td><td><code>M5/proofs/</code> · <code>test_report.json</code> · <code>traceability_matrix.csv</code></td></tr>
</table>
<div class="callout ok"><b>Verdict M5.</b> B4 est exécutable, testé, traçable et signé. La décision nominale est RETRAIT avec HITL REQUIS ; le faux journal est détecté sans réduire la sévérité ; les tokens modifiés, expirés ou rejoués sont refusés ; aucune PII ne sort.</div>
<div class="footer"><span>M5 — Documentation technique</span><span>Page 5 / 5</span></div>
</section>
</body></html>"""

SLIDES = f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><title>M5 — Slides</title><style>
:root{{--navy:#0b1f3a;--orange:#f59e0b;--ink:#1f2937;--muted:#5b6778;--line:#d8dee8;--green:#0f766e;--red:#b91c1c}}
*{{box-sizing:border-box}}html,body{{margin:0;padding:0;background:#fff}}
body{{font-family:"Segoe UI",Arial,sans-serif;color:var(--ink)}}
@page{{size:338mm 190mm;margin:0}}
.slide{{width:338mm;height:190mm;padding:12mm 14mm;position:relative;break-after:page;background:#fff;overflow:hidden}}
.slide:last-child{{break-after:auto}}
.kicker{{font-size:8pt;letter-spacing:2px;color:#b45309;font-weight:700;text-transform:uppercase}}
h1{{font-size:30pt;color:var(--navy);margin:4px 0 2px;line-height:1.05}}
h2{{font-size:18pt;color:var(--navy);margin:0 0 6px}}
.sub{{font-size:12pt;color:var(--muted);margin-bottom:9mm}}
.flow{{display:flex;align-items:center;gap:2.5mm;flex-wrap:nowrap;margin:6mm 0}}
.step{{border:1px solid #94a3b8;background:#f8fafc;border-radius:2mm;padding:3mm 3.5mm;font-size:9pt;min-width:25mm;text-align:center;line-height:1.3}}
.step.hot{{border:2px solid var(--orange);background:#fff8eb}}.step.ok{{border:2px solid var(--green);background:#ecfdf5}}
.arrow{{color:var(--orange);font-size:16pt;font-weight:700}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:4mm}}
.card{{border:1px solid var(--line);border-radius:2mm;padding:4mm;background:#fff}}
.card .n{{display:block;font-size:26pt;font-weight:700;color:var(--navy);line-height:1}}
.card .l{{display:block;font-size:8pt;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}}
.two{{display:grid;grid-template-columns:1.1fr .9fr;gap:8mm}}
pre{{background:var(--navy);color:#e7eef8;padding:5mm;font-size:8pt;line-height:1.4;white-space:pre-wrap;border-radius:2mm;font-family:Consolas,monospace}}
.badge{{display:inline-block;border:1px solid var(--orange);color:#b45309;border-radius:10mm;padding:1mm 3mm;font-size:8pt;margin-right:2mm}}
.foot{{position:absolute;bottom:5mm;left:14mm;right:14mm;font-size:7pt;color:#8391a5;border-top:1px solid var(--line);padding-top:2mm;display:flex;justify-content:space-between}}
</style></head><body>
<section class="slide">
<div class="kicker">Projet 30 · AGRO-FROID · M5</div>
<h1>B4 — Décider, prouver, faire valider</h1>
<div class="sub">Du pack de preuves B2 au JSON canonique + package HITL signé</div>
<div class="flow">
<div class="step">Pack B2<br>2 lots · 2 magasins</div><span class="arrow">→</span>
<div class="step hot">Vérifier<br>HMAC · séquence</div><span class="arrow">→</span>
<div class="step">Recalcul<br>4,2 °C · 190 min</div><span class="arrow">→</span>
<div class="step">Politique<br>P1-P6</div><span class="arrow">→</span>
<div class="step">Exposition<br>60/100</div><span class="arrow">→</span>
<div class="step ok">JSON<br>RETRAIT</div><span class="arrow">→</span>
<div class="step hot">HITL<br>token signé</div>
</div>
<div class="two">
<div>
<h2>Ce que M5 garantit</h2>
<ul style="font-size:12pt;line-height:1.6">
<li>JSON canonique <b>9 clés</b>, validé à 100 %</li>
<li>Delta et durée <b>recalculés</b>, jamais lus dans un LLM</li>
<li>Faux journal <b>détecté</b>, décision non réduite</li>
<li>Token <b>signé, expirant, à usage unique</b></li>
<li>Ledger <b>append-only</b> + outbox idempotente</li>
<li><b>0 PII</b> en sortie</li>
</ul>
</div>
<div class="card" style="background:#0b1f3a;color:#fff;border:none">
<div style="font-size:8pt;color:#ffd48a;letter-spacing:1.5px">RÉSULTAT NOMINAL</div>
<pre style="background:transparent;padding:2mm 0;font-size:9pt;color:#e7eef8">{result_json}</pre>
</div>
</div>
<div class="foot"><span>M5 — Driss · B4 Décision + HITL</span><span>Slide 1 / 2</span></div>
</section>

<section class="slide">
<div class="kicker">Preuves et audit</div>
<h1 style="font-size:26pt">10/10 tests · 0 PII · 0 faux log accepté</h1>
<div class="grid" style="margin:8mm 0">
<div class="card"><span class="n">10/10</span><span class="l">Tests fonctionnels</span></div>
<div class="card"><span class="n">4,2 °C</span><span class="l">Delta / 190 min</span></div>
<div class="card"><span class="n">60/100</span><span class="l">Exposition</span></div>
<div class="card"><span class="n">0</span><span class="l">PII en sortie</span></div>
</div>
<div class="two">
<div>
<h2>Tests clés</h2>
<table style="width:100%;border-collapse:collapse;font-size:10pt">
<tr style="background:#0b1f3a;color:#fff"><th style="text-align:left;padding:2mm">Cas</th><th style="text-align:left;padding:2mm">Résultat</th></tr>
<tr><td style="border-bottom:1px solid #d8dee8;padding:2mm">Nominal RETRAIT</td><td><b>PASS</b></td></tr>
<tr><td style="border-bottom:1px solid #d8dee8;padding:2mm">Rappel + double contrôle</td><td><b>PASS</b></td></tr>
<tr><td style="border-bottom:1px solid #d8dee8;padding:2mm">Certificat invalide</td><td><b>PASS</b></td></tr>
<tr><td style="border-bottom:1px solid #d8dee8;padding:2mm">Token modifié / expiré / rejoué</td><td><b>PASS</b></td></tr>
<tr><td style="border-bottom:1px solid #d8dee8;padding:2mm">Faux journal</td><td><b>PASS</b></td></tr>
<tr><td style="padding:2mm">PII</td><td><b>PASS</b></td></tr>
</table>
</div>
<div>
<h2>Preuves</h2>
<pre style="font-size:7.6pt">proofs/
  result_nominal.json
  hitl_package.json
  ledger_record.json
  outbox_records.json
  traceability_matrix.csv
  test_report.json
  test_output.txt
  hashes.txt
  cases/ (7 scénarios)</pre>
<div class="badge">GitHub</div><div class="badge">ClickUp</div><div class="badge">PDF 5 pages</div>
</div>
</div>
<div style="margin-top:6mm;font-size:11pt;color:#5b6778">Verdict : B4 est exécutable, testé, traçable et signé. La décision reste humaine ; la preuve est déterministe.</div>
<div class="foot"><span>M5 — Driss · B4 Décision + HITL</span><span>Slide 2 / 2</span></div>
</section>
</body></html>"""

(DOCS / "Documentation_M5.html").write_text(DOC, encoding="utf-8")
(DOCS / "Slides_M5.html").write_text(SLIDES, encoding="utf-8")
print("written", DOCS / "Documentation_M5.html", DOCS / "Slides_M5.html")
