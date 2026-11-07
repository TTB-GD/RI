# Run It — Plan de développement

> Document de pilotage, pas spécification de Game Design. Le GDD reste l'autorité de design et `CURRENT_STATE.md` le snapshot compact du prototype.

## 1. Gouvernance

Les statuts ont un sens strict : **FACT** vérifié dans le dépôt ; **DECISION VALIDATED** porté par le GDD ; **OPEN** arbitrage requis ; **PROPOSAL** ordre recommandé ; **CURRENT** comportement du prototype ; **INTEGRATED** branché dans le chemin retenu ; **EXPERIMENTAL** non promu en règle ; **IMPLEMENTATION GAP** frontière absente/incomplète ; **HISTORICAL** preuve conservée sans portée actuelle ; **LATER** volontairement différé.

Chaîne de gouvernance :

```text
IDÉE → ANALYSE DESIGN → PROPOSITION → DÉCISION UTILISATEUR → GDD
→ AUDIT → IMPLÉMENTATION → TESTS → SIMULATION
```

Une hypothèse n'est pas une règle, un harness n'est pas une spécification, et une policy automatique n'est pas un comportement joueur. La roadmap ne modifie pas le GDD.

Priorités : **P0** bloque la phase structurante ; **P1** nécessaire avant analyse quantitative sérieuse ; **P2** amélioration après la première boucle intégrée ; **LATER** hors chemin critique.

## 2. État consolidé

### Training CURRENT

**DECISION VALIDATED / CURRENT.** Le pool persistant commence à `4d6`, gagne un d6 aux seuils CTL 50 et 100 (disponible au tour suivant), et quatre qualités réussies améliorent un dé `d6 → d8 → d10 → d12` (bonus permanent nul). Le lancer fournit D99, énergie et RPE Max. Les contraintes incluent au plus sept séances, entrées Qualité uniques, EF répétables et `qualités ≤ EF` par tour. RPE Max fixe la zone sûre ; une Qualité au-dessus peut être choisie puis risquée, EF au-dessus est indisponible. Le premier bust conserve les séances sûres, annule les Qualités risquées postérieures et laisse une décision explicite de redistribution en EF, vide ou partielle. Seules les séances réellement complétées après résolution avancent CTL, prérequis et progression des dés.

La simulation Training emploie un RNG local seedable/injectable pour le budget de dés et le risque ; le flux global `random` n’est pas reseedé. Les journaux distinguent les occurrences de séances, y compris les répétitions, et identifient les séances planifiées et les EF redistribuées. Les PR #29–#31 ont ajouté l’injection et les tests de rejeu/transitions ; consulter les checks GitHub pour l’état d’exécution, car la présence des tests n’atteste pas leur succès.

### Race V2 CURRENT / INTEGRATED

La frontière locale utilise `PhysiologyProfile(EF, Seuil, VMA)` avec `EF < Seuil < VMA`, `Charge = Production + Difficulty`, `Charge <= VMA`, `Cost = EF` si `Charge <= EF`, pentes 2/3 **EXPERIMENTAL** au-dessus de EF, et score `Production`. Le moteur longitudinal conserve encore des éléments expérimentaux. Le mapping complet Training → profil est absent.

### Training V2

Training CURRENT (catalogue, composition, risque/bust, CTL, progression, pool) et Training V2 expérimental (partition EF/Q et pistes physiologiques) sont deux modèles distincts. Aucune conversion vers Race ne peut sélectionner implicitement V2 comme cible de production ; le choix A/B/C dépend de la vision Game Design et reste **OPEN**.

`D1_TRAINING_WORKING_DESIGN.md` rassemble des propositions et décisions de travail formulées en discussion. Il constitue une base de préparation pour C1/C2/D1, pas une spécification normative ni une décision de remplacement de Training CURRENT.

## 3. Portes et statut

### Porte A — Fiabilité des preuves (P0)

**A1 TERMINÉ.** F9 assaini chirurgicalement : JSON historique intact conservé, point d'entrée cohérent, blocs A/A2/B/B2/C classés `REPRODUCIBLE` avec provenance et limites dans `experiments/current/training_v2_minimal/README.md` ; aucune valeur remplacée silencieusement.

**A2 TERMINÉ.** `experiments/current/training_v2_minimal/REPORT.md` contient la matrice d'audit, les sources et corrections, ainsi que les limites d'inférence. Les campagnes n'ont pas été relancées ; l'audit rapporte 481 valeurs vérifiées et aucun chiffre à remplacer.

**A3 TERMINÉ.** La CI valide les JSON suivis et exécute explicitement les tests légers des harnesses ; les campagnes longues restent exclues.

### Porte B — Intégrité du Training CURRENT (P0)

**B1 TERMINÉ (PR #25).** `plan_validation.validate_plan(...)` fournit une validation structurée, indépendante du sélecteur. Les tests couvrent les contraintes du programme ; le risque sans taille de dé renvoie une violation explicite.

**B2 TERMINÉ (PR #30).** La simulation journalise chaque occurrence séparément, conserve les traces correspondantes et indique l'origine des séances redistribuées en EF.

**B3 TERMINÉ (PR #27 ; CI confirmée le 2026-11-06).** `tests/test_d99_table.py` contient des fixtures indépendantes des tables de production pour les 23 signatures CURRENT : 5 lignes à 4 dés, 7 à 5 dés et 11 à 6 dés. Le test vérifie l'égalité exacte avec `SESSION_EFFECTS` et les sorties de `session_outcome`. Le workflow [Tests #42254642083](https://github.com/TTB-GD/RI/actions/runs/42254642083), exécuté sur `main` au commit `40151114`, est terminé avec succès ; la suite unitaire de 98 tests inclut ces cas. La convention à 3 dés reste séparément **OPEN / IMPLEMENTATION POLICY** : elle n'est ni une décision de design ni une condition de clôture de B3.

**B4 TERMINÉ — implémentation et couverture de base (PR #29–#31).** Le RNG local/injectable permet le rejeu des lancers de dés et de risque ainsi que de la simulation. Les tests couvrent le rejeu avec une seed et l'absence de mutation de l'état aléatoire global. La reproductibilité est attendue dans le même environnement logiciel ; aucune garantie de séquence inter-version Python n’est posée.

**B5 TERMINÉ pour les invariants testés (PR #31).** Les tests protègent les paliers CTL 50/100, l'ajout unique/plafonné de dés, les seuils et le plafond des améliorations et leur application au tour suivant. Ils n'imposent pas de policy gloutonne aux règles de progression.

### Porte C — Vision et expérience cible (P0 — GAME DESIGN)

**C1 TERMINÉ — direction validée le 2026-11-07.** La fantaisie est celle d'un entraîneur qui construit une préparation pour une course. Training construit le moteur physiologique ; Race le met à l'épreuve. L'expérience cible est d'environ 2/3 Training et 1/3 Race, 60–90 minutes, 2–4 joueurs et 12–16 tours de Training à tester. Les décisions d'allocation, la composition des séances, le risque volontaire et la progression durable sont au cœur du Training. Les profils doivent être différenciés et leurs conséquences observables en Race. **Arbitrage déterminant : la qualité de la préparation prime sur le seul résultat de Race.** La course reste indispensable comme épreuve et révélateur, mais une performance isolée ne doit pas effacer la cohérence et la qualité des choix de préparation. Le hasard crée des contraintes et opportunités ; le joueur arbitre. Une erreur isolée ne doit pas condamner toute la préparation. La coopération est positive sans dépendance systématique entre joueurs. Référence détaillée : `D1_TRAINING_WORKING_DESIGN.md` (section « C1 — direction validée »).

**C2 TODO — formalisation / validation.** Définir des critères de comparaison A/B/C : choix réels, lisibilité, diversité des builds, impact Race, risque, interaction pool/D99/progression, charge cognitive, rythme, équilibrage et testabilité. Pondération **OPEN**.

`D1_TRAINING_WORKING_DESIGN.md` contient déjà des matériaux préparatoires issus du travail C1/C2/D1, notamment les orientations et arbitrages D1-S1 à D1-S8. Il reste explicitement **WORKING DESIGN / NON NORMATIF** : sa présence ne clôt ni C1/C2, ne vaut pas sélection A/B/C et ne promeut pas ses hypothèses dans le GDD.

Sortie C : direction Game Design validée avant toute sélection A/B/C.

### Porte D — Modèle Training cible (P0 — GAME DESIGN)

**D1 TODO.** Décision explicite `TRAINING TARGET = A / B / C`, principes retenus et éléments écartés/reportés, inscrits au GDD après C. A = conserver CURRENT ; B = remplacer substantiellement par V2 ; C = hybride explicite. Aucun mapping Training → profil avant cette décision.

### Porte E — Cohérence Training ↔ Race (P0/P1)

**E1 TODO :** résoudre seulement les décisions qui bloquent réellement le modèle retenu (au besoin RPE Max, TN, ordre des risques, réserve/D99).

**E2 TODO :** si requis par D1, mapping déterministe/documenté `Training state → EF → Seuil → VMA → PhysiologyProfile`.

**E3 TODO :** vérifier l'échelle Cost ↔ Reserve avant end-to-end. La réserve actuelle inclut une baseline expérimentale `race_length × 2 + floor(CTL / 50)` ; ne pas modifier `Charge <= EF ↔ Cost = EF` sans décision de design.

**E4 TODO :** analyse combinatoire légère D99 × upgrades sur pools accessibles, sans campagne massive ni changement de règle.

### Porte F — End-to-end et diagnostics (P1, après D/E)

**F1 TODO :** fixer le cadre minimal de partie/horizon. **F2 TODO :** scénario déterministe Training → progression → profil → moteur Race V2 intégré. **F3 TODO :** comparer une policy Training risk-aware à la baseline technique. **F4 TODO :** instrumenter et mesurer la sensibilité Race (profils faibles/intermédiaires/forts). **F5 TODO :** diagnostic de 100–1 000 trajectoires, jamais un équilibrage final.

### Portes ultérieures

**G1 TODO :** profondeur Race/solver après E3 et premier end-to-end ; séparer oracle à information future d'une policy jouable. **H1 TODO :** calibration séquentielle (Réserve, courbe, Form, Freshness, SL), un paramètre à la fois. **I1 TODO :** choix joueur et Fatigue après observations de la boucle intégrée.

### LATER

SPEC, blessures, surentraînement définitif, nutrition, save-a-die, personnages, refonte du catalogue, Godot, Event Bus, ECS, DI, moteur abstrait, état global, optimisation prématurée et Monte-Carlo massif restent différés. SPEC est **OPEN / NOT IMPLEMENTED**, pas abandonné.

## 4. Dépendances et chemin critique

```text
A — preuves fiables ─┐
                     ├→ C — vision → D — cible Training → E — cohérence → F — end-to-end
B — CURRENT protégé ┘                                            → G → H → I → LATER
```

A et B sont désormais clôturées sur leur périmètre documenté : A1–A3 et B1–B5, avec B3 confirmé par la CI du 2026-11-06. C s'appuie sur les preuves fiabilisées sans choisir le modèle. D dépend de C ; E dépend de D ; F dépend du mapping et de Cost ↔ Reserve ; G suit le premier end-to-end. Ne pas interpréter quantitativement Race avant E3.

## 5. Tableau de pilotage

| ID | Porte | Priorité | Nature | Action | Dépend de | Critère de sortie | Statut |
|---|---|---|---|---|---|---|---|
| A1 | A | P0 | TECH | Assainir F9 | — | blocs classés et preuves traçables | DONE |
| A2 | A | P0 | AUDIT | Revalider les REPORT | A1 | conclusions alignées sur preuves | DONE |
| A3 | A | P0 | TECH | CI harness/JSON | A1 | régression F9 détectée | DONE |
| B1 | B | P0 | TECH | `validate_plan` pur | — | règles indépendantes du sélecteur | DONE (PR #25) |
| B2 | B | P0 | BUG | Trace EF répétées/redistribution | — | occurrence et origine distinctes | DONE (PR #30) |
| B3 | B | P0 | TEST | D99 table-driven | — | lignes CURRENT protégées ; 3 dés séparés | DONE (PR #27 ; CI #42254642083) |
| B4 | B | P0 | TECH | RNG injectable minimal | — | replay contrôlé d'un tour | DONE (PR #29–#31) |
| B5 | B | P0 | TEST | Transitions longitudinales | B1, B4 | transitions/invariants protégés | DONE (PR #31) |
| C1 | C | P0 — GAME DESIGN | DESIGN | Piliers / expérience cible | A, B | direction courte validée | DONE (validation utilisateur 2026-11-07) |
| C2 | C | P0 — GAME DESIGN | DESIGN | Critères A/B/C | C1 | critères comparables | TODO |
| D1 | D | P0 — GAME DESIGN | DESIGN | Choisir Training A/B/C | C2 | décision intégrée au GDD | TODO |
| E1 | E | P1 | DESIGN | Décisions strictement bloquantes | D1 | règles nécessaires définies | TODO |
| E2 | E | P1 | DESIGN+TECH | Mapping profil | D1, E1 | dérivation documentée | TODO |
| E3 | E | P0/P1 | DESIGN+SIM | Cost ↔ Reserve | E2 | échelles compatibles | TODO |
| E4 | E | P1 | ANALYSE | D99 × upgrades | B3 | interaction mesurée | TODO |
| F1–F5 | F | P1 | DESIGN/TEST/SIM | Cadre, end-to-end, diagnostic | D1, E | trajectoire interprétable | TODO |
| G1 | G | P1/P2 | ANALYSE | Solver / oracle Race | E3, F2 | profondeur mesurée | TODO |
| H1 | H | P1/P2 | BALANCE | Calibration séquentielle | F5, G1 | paramètres isolés | TODO |
| I1 | I | P2 | DESIGN | Choix joueur / Fatigue | H1 | justifié par observations | TODO |

## 6. Prochain chantier recommandé

A et B étant clôturées, C1 est validée ; reprendre C2 en s'appuyant sur les matériaux non normatifs de `D1_TRAINING_WORKING_DESIGN.md`. La convention D99 à 3 dés reste **OPEN** et n'est pas modifiée par la clôture B3. Aucune décision Training A/B/C, aucun mapping Training → profil et aucune analyse quantitative Race ne doivent précéder la validation de ces portes et E3.
