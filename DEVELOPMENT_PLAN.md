# Run It — Plan de développement

> **Portée :** document de pilotage, pas spécification de Game Design.  État
> vérifié au commit `5c6e2f8` (fusion de la PR #19). Le GDD reste l'autorité de
> design et `CURRENT_STATE.md` le snapshot compact du prototype.

## 1. Lecture et gouvernance

Les mentions suivantes ont un sens strict dans ce document :

- **FACT** — vérifié dans le dépôt au HEAD indiqué ci-dessus ;
- **DECISION VALIDATED** — décision déjà portée par le GDD ;
- **OPEN** — arbitrage requis, sans décision prise par cette roadmap ;
- **PROPOSAL** — ordre de développement recommandé ;
- **CURRENT** — comportement courant du prototype ;
- **INTEGRATED** — frontière effectivement branchée dans le chemin intégré ;
- **EXPERIMENTAL** — mécanisme, fixture ou policy d'étude non promu en règle ;
- **IMPLEMENTATION GAP** — frontière attendue mais absente ou incomplète ;
- **HISTORICAL** — preuve conservée pour traçabilité sans portée CURRENT ;
- **LATER** — travail volontairement hors du chemin critique.

Le travail suit la chaîne de gouvernance :

```text
IDÉE
→ ANALYSE DESIGN
→ PROPOSITION
→ DÉCISION UTILISATEUR
→ GDD
→ AUDIT
→ IMPLÉMENTATION
→ TESTS
→ SIMULATION
```

Une hypothèse n'est donc pas une règle, un harness n'est pas une
spécification, une policy automatique n'est pas un comportement joueur et une
divergence ne devient pas un bug sans vérification. Cette roadmap ne modifie
pas le GDD.

Priorités des actions : **P0** bloque la prochaine phase structurante ; **P1**
est nécessaire avant une analyse quantitative sérieuse ; **P2** améliore le
système après obtention d'une boucle intégrée ; **LATER** est volontairement
différé.

## 2. État consolidé

### Training CURRENT

**DECISION VALIDATED / CURRENT.** Le pool persistant commence à `4d6`, puis
gagne un d6 aux seuils CTL 50 et 100, utilisable au tour suivant. Quatre
qualités réussies donnent un upgrade `d6 → d8 → d10 → d12`; les bonus
permanents sont `0 / 0 / 0`. Le lancer fournit D99, l'énergie et RPE Max. La
composition respecte notamment la limite de sept séances, l'unicité des
entrées Qualité, la répétition possible d'EF et `qualités ≤ EF`.

RPE Max délimite la zone sûre : le risque d'une Qualité éligible au-dessus est
volontaire, tandis qu'une EF au-dessus reste indisponible. Le premier bust
conserve les séances sûres, annule les Qualités risquées ultérieures et expose
un choix explicite de redistribution en EF. CTL, prérequis et progression des
dés ne comptent que les séances réellement réussies après résolution.

### Race V2 CURRENT / INTEGRATED

**FACT / CURRENT / INTEGRATED.** La frontière locale utilise :

```text
PhysiologyProfile(EF, Seuil, VMA), avec EF < Seuil < VMA
Charge = Production + Difficulty
Charge <= VMA
Cost = EF si Charge <= EF
pentes 2 / 3 EXPERIMENTAL au-dessus de EF
Score = Production
```

Le moteur longitudinal existant réutilise les sous-ensembles de Production,
la révélation de Form en S1–S3, la révélation de Réserve, le clamp S3, le
filtre d'abordabilité en S4+, le DNF et des policies techniques. Ces éléments
longitudinaux restent majoritairement **EXPERIMENTAL** ; leur présence dans le
moteur ne les transforme pas en design validé.

### Chaînon manquant et F12 — deux modèles Training

**FACT / IMPLEMENTATION GAP.** Aucun mapping complet ne relie aujourd'hui
l'état Training CURRENT au profil intégré :

```text
Training CURRENT
        ↓
   [mapping absent]
        ↓
PhysiologyProfile
        ↓
     Race V2
```

Deux modèles coexistent et ne doivent pas être confondus :

```text
Production CURRENT                 Training V2 EXPERIMENTAL
catalogue de séances               partition physique EF / Q
→ composition                      → pistes / milestones
→ risque / bust                    → EF / Seuil / VMA
→ CTL / progression
→ pool
```

**OPEN.** Avant tout mapping, la cible du futur Training doit être décidée.
Le harness Training V2 ne devient pas silencieusement la cible de production.

## 3. Faits techniques motivant l'ordre

### F9 — Training V2 minimal

**FACT — BUG / TRACEABILITY ISSUE.**

- `experiments/current/training_v2_minimal/results.json` n'est pas un JSON
  syntaxiquement valide au HEAD vérifié ;
- `harness.py` construit d'abord A/A2/B/B2, puis réaffecte `results` et perd
  A2/B2 dans `run_all()` ; deux blocs `if __name__ == "__main__"` écrivent
  successivement le même fichier selon deux stratégies incompatibles ;
- le README contient des paragraphes dupliqués et contradictoires sur le
  périmètre et le contenu de `results.json` ;
- A2/B2 figurent dans le REPORT et dans le fichier de résultats endommagé,
  mais ne sont pas proprement régénérables par le point d'entrée au HEAD.

La roadmap ne conclut pas que les chiffres A2/B2 sont faux. Ils ne sont
simplement pas considérés comme **reproductibles depuis le HEAD actuel** tant
que leur traçabilité n'est pas restaurée.

### F10 — couverture CI

**FACT / IMPLEMENTATION GAP.** `.github/workflows/tests.yml` exécute seulement
`python -m unittest discover -s tests -v`. Les tests propres aux harnesses et
la validité des JSON versionnés ne sont donc pas protégés automatiquement.

### F1 — légalité des programmes

**FACT / IMPLEMENTATION GAP.** Les contraintes de composition sont surtout
appliquées pendant la construction gloutonne dans `session_selector.py`.
`session_resolution.py` valide certaines contraintes de résolution et de
redistribution, mais il n'existe pas de frontière normative générale
`validate_plan(...)` (ou équivalent) indépendante du sélecteur.

### Trace des EF répétées

**FACT — BUG à faible effort.** `simulate_player.py` réduit la trace de
sélection à `{nom_de_séance: étape}` via `trace_by_name`. Plusieurs occurrences
d'une même EF peuvent donc partager la dernière trace du même nom ; une EF
issue de redistribution peut également récupérer cette trace au lieu d'être
identifiée sans ambiguïté comme redistribution.

### D99

**FACT.** Les tables d'implémentation couvrent les motifs à 3, 4, 5 et 6 dés,
mais les tests CURRENT observés protègent surtout les contraintes dérivées
(plafond Qualité, inclusion de SL, répétition EF), pas chaque ligne de la table
par un test table-driven exhaustif. Le besoin est donc : **tests table-driven
complets pour les motifs CURRENT**. Les lignes à trois dés restent séparées,
avec le statut **OPEN / IMPLEMENTATION POLICY** ; cette roadmap ne les valide
pas en design.

### RNG Training

**FACT / IMPLEMENTATION GAP.** `Die.roll()` et la simulation Training utilisent
le module `random` global, et `run_player_simulation()` appelle
`random.seed(seed)`. Race Engine V2 génère au contraire les lancers avec un
`random.Random(seed)` local. Un seam ciblé existe déjà pour le risque via
`first_bust_index(..., roll_face=...)`, mais pas pour l'ensemble du tour
Training. Le besoin est une injection RNG minimale, pas un service ou framework.

## 4. Portes successives

### Porte A — Fiabilité des preuves

**Priorité : P0.**

**PROPOSAL — objectif.** Garantir que chaque expérience conservée est soit
reproductible, soit explicitement identifiée comme non reproductible depuis le
HEAD, sans ambiguïté de statut.

#### A1 — Assainir F9 de façon chirurgicale

Mission future : restaurer un point d'entrée cohérent, rendre le JSON valide,
identifier les résultats reproductibles, sans recalcul silencieux ni
modification d'une règle expérimentale.

**Garde-fou.** Ne pas en faire une restauration générale de Training V2. Si
A2/B2 exige de reconstruire des choix historiques incertains :

```text
STOP
→ conserver les résultats comme HISTORICAL — NOT REPRODUCIBLE FROM CURRENT HEAD
```

**Critère de sortie :** chaque bloc A/A2/B/B2/C porte explicitement
`REPRODUCIBLE` ou
`HISTORICAL — NOT REPRODUCIBLE FROM CURRENT HEAD`.

#### A2 — Revalider les REPORT associés

Relire uniquement les conclusions dépendant des résultats classés par A1, sans
refaire le Game Design.

**Critère de sortie :** aucune conclusion expérimentale n'est présentée comme
démontrée lorsque son résultat source n'est pas reproductible.

#### A3 — CI légère

Ajouter ultérieurement la validation des JSON, les tests unitaires des
harnesses et une sonde déterministe bon marché. Ne pas exécuter les grandes
campagnes Monte-Carlo en CI.

**Critère de sortie :** une régression analogue à F9 fait échouer la CI.

### Porte B — Intégrité du Training CURRENT

**Priorité : P0.** Cette porte protège le jeu CURRENT quel que soit le futur
choix A/B/C ; elle ne présélectionne pas son architecture finale.

#### B1 — Frontière normative de validation d'un programme

Créer ultérieurement une petite fonction pure `validate_plan(...)` ou
équivalent portant les contraintes CURRENT, et non une policy de sélection.
Préférer conceptuellement une réponse structurée `PlanValidation` /
`PlanViolation`, avec codes de motif réutilisables par tests, agents, UI future
et éventuel port Godot. Ne pas introduire de Rule Engine général.

**Critère de sortie :** la couche de règles rejette un programme illégal même
s'il ne provient pas de `session_selector`.

#### B2 — Corriger la trace des EF répétées

Journaliser les occurrences réelles et distinguer une EF redistribuée.

**Critère de sortie :** deux occurrences identiques d'EF ne partagent plus
accidentellement leur trace analytique et toute EF de redistribution est
identifiable comme telle.

#### B3 — Tests D99

Compléter les tests table-driven des motifs CURRENT, en séparant les lignes à
trois dés **OPEN / IMPLEMENTATION POLICY**.

**Critère de sortie :** toute dérive involontaire d'une ligne D99 CURRENT
provoque un test rouge.

#### B4 — RNG minimal injectable

Ajouter seulement le seam nécessaire pour contrôler les tirages Training ; ne
pas créer `RandomService`, framework DI ou `GameEngine RNG`.

```text
tirages connus
→ décision
→ programme
→ risque
→ bust
→ résolution
→ progression
→ tour suivant
```

**Critère de sortie :** ce scénario longitudinal est rejouable exactement à
partir de tirages contrôlés, sans dépendre du flux `random` global.

#### B5 — Tests de transitions

Protéger au minimum : CTL gagné au tour N ; d6 débloqué au tour N+1 ; quatrième
Qualité réussie ; upgrade disponible au tour suivant ; bust ; annulation ;
redistribution EF ; progression des seules réussites ; invariants `≤ 7`,
`qualités ≤ EF`, D99 et énergie.

**Critère de sortie :** les principales transitions longitudinales CURRENT
sont protégées sans dépendre d'une policy gloutonne particulière.

### Porte C — Vision et expérience cible

**Priorité : P0 — GAME DESIGN.**

**OPEN / objectif.** Produire une direction courte, et non une refonte complète
du GDD, donnant des critères suffisamment explicites pour comparer les modèles
Training A/B/C. Le choix ne doit pas découler du code existant, du nombre de
fonctions déjà implémentées, des seuls résultats de harnesses ou de la facilité
technique.

#### C1 — Formaliser les piliers de Run It

La future tâche de Game Design doit expliciter, sans que cette roadmap invente
les réponses :

- la fantaisie centrale et le rôle du joueur — construire puis piloter son
  moteur de coureur ;
- les décisions recherchées pendant le Training, le rôle attendu du risque et
  l'équilibre contrôle / hasard ;
- l'importance relative de Training et Race et la différenciation souhaitée
  entre profils de coureurs ;
- la complexité acceptable, la lisibilité des conséquences, le rythme et la
  durée cible approximative ;
- l'horizon Training approximatif et la fonction de la course finale ;
- l'interaction multijoueur au seul niveau nécessaire pour orienter le design.

#### C2 — Définir les critères de comparaison A/B/C

Examiner la richesse des choix réels, la lisibilité, la différenciation des
builds, l'impact mesurable sur Race, la place du risque, l'interaction avec
pool/D99/progression, la charge cognitive, le rythme de progression, le
potentiel d'équilibrage et la testabilité. La complexité d'implémentation reste
un critère secondaire. La pondération de ces critères demeure **OPEN**.

**Critère de sortie de la Porte C :** une courte direction Game Design validée
permet de répondre à « qu'attend-on du système Training pour qu'il soit
cohérent avec l'expérience Run It ? ». Aucune option A/B/C n'est sélectionnée
avant cela et avant l'arbitrage F12 entre les deux modèles Training.

### Porte D — Décision du modèle Training cible

**Priorité : P0 — GAME DESIGN.** Aucune implémentation Training →
`PhysiologyProfile` ne commence avant cette décision, elle-même évaluée à
partir des piliers et critères de la Porte C.

- **A — conserver Training CURRENT :** catalogue, risque, bust et progression
  restent le cœur ; le profil est dérivé ensuite de cet état.
- **B — faire de Training V2 la nouvelle cible :** partition EF/Q et pistes
  physiologiques remplacent substantiellement l'architecture actuelle.
- **C — hybride explicite :** certaines idées V2 entrent dans Training CURRENT,
  chacune après décision explicite, jamais comme conséquence implicite du code.

La décision doit aussi utiliser les preuves classées par A, sans conclure à
partir du seul critère « déjà codé » ou « plus moderne ».

**Critère de sortie :** décision utilisateur explicite
`TRAINING TARGET = A / B / C`, principes retenus et éléments rejetés/reportés,
puis intégration au GDD avant implémentation.

### Porte E — Cohérence Training ↔ Race

**Priorité : P0 / P1.** Cette porte résout les seuls verrous nécessaires au
modèle retenu avant tout vrai scénario end-to-end.

#### E1 — Résoudre uniquement les décisions bloquantes

Ne pas rouvrir toutes les anciennes questions. Selon la cible retenue, traiter
séparément RPE Max, la convention de réserve ou la convention D99 liée au dé
écarté uniquement si elles bloquent effectivement le raccord.

**OPEN / NEEDS EXPLICIT DESIGN CONFIRMATION :** si le modèle les utilise :

- **TN :** le prototype possède une convention technique, mais sa définition
  normative doit être confirmée avant emploi dans Fatigue ou les simulations ;
- **ordre des risques :** puisque le premier bust affecte les Qualités
  ultérieures, préciser si l'ordre est choisi par le joueur, imposé ou défini
  autrement. Une policy gloutonne ne doit pas fixer silencieusement cet ordre.

**Critère de sortie :** seules les règles nécessaires au modèle retenu sont
définies et portées dans le GDD.

#### E2 — Mapping Training → `PhysiologyProfile`

Si la cible retenue le requiert, construire le minimum :

```text
Training state → EF → Seuil → VMA → PhysiologyProfile
```

**Critère de sortie :** deux états Training pertinents et différents produisent
deux profils différents de manière déterministe et documentée.

#### E3 — Cohérence physiologique / échelle Race

**FACT.** Le chemin intégré utilise `C(x) = EF` pour `x <= EF`, puis les pentes
expérimentales 2/3. La Réserve longitudinale provient encore de la baseline
expérimentale antérieure :

```text
base_reserve = race_length × 2 + floor(CTL / 50)
```

avec Form et Freshness comme ajustements. Ces échelles n'ont pas été
recalibrées conjointement.

**DÉDUCTION DE COHÉRENCE D'ÉCHELLE, PAS NOUVELLE RÈGLE.** Un raccord technique
correct ne démontre pas que l'unité de coût physiologique et l'unité de Réserve
sont compatibles. Avant l'end-to-end, comparer coûts minimum, typiques et
maximum à la Réserve disponible, déterminer comment EF se traduit en dépense de
Réserve, puis établir si la Réserve doit être remise à l'échelle ou si une autre
relation est nécessaire.

La règle `Charge <= EF → Cost = EF` n'est pas rouverte par cette roadmap : elle
est seulement confrontée à l'échelle de Réserve. Toute modification exigerait
une nouvelle décision Game Design.

**Critère de sortie :** pour une longueur représentative, le coût minimal permet
une arrivée, la plage de Réserve est cohérente avec les coûts, et les différences
EF/Seuil/VMA restent observables sans rendre la course automatiquement triviale
ou impossible.

#### E4 — Micro-étude D99 × upgrades

**QUESTION D'ÉQUILIBRAGE / INTERACTION À MESURER — pas un bug.** D99 dépend des
répétitions de faces brutes. À nombre de dés égal, passer de d6 à d8/d10/d12
peut réduire certains motifs, alors que l'upgrade améliore valeurs, RPE Max et
capacité Race : il pourrait donc aussi réduire les slots Qualité.

Effectuer plus tard une analyse combinatoire ou exhaustive légère sur `4d6`,
les pools mixtes réellement accessibles, puis les pools à 5 et 6 dés. Mesurer
la distribution des plafonds D99, la fréquence du bonus de réserve et leur
évolution après upgrades. Ne lancer aucune campagne massive et ne modifier
aucune règle sans résultats.

**Critère de sortie :** l'interaction sur les pools accessibles est mesurée et
qualifiée sans préjuger de son caractère volontaire ou problématique.

### Porte F — End-to-end et simulation diagnostique

**Priorité : P1.** Cette porte dépend de la décision D et de la cohérence E.

#### F1 — Cadre minimal de partie

Fixer l'horizon Training, le moment de la course, la structure minimale des
courses si nécessaire et la définition d'une trajectoire complète. Ne pas
forcer ici multijoueur complet, personnages ou toutes les conditions de victoire.

**Critère de sortie :** une campagne représente une partie ou un cycle défini.

#### F2 — Scénario end-to-end déterministe

Utiliser le moteur Race V2 intégré, sans recopier sa boucle dans
`training_race_bridge` :

```text
Player initial → plusieurs tours Training → progression → PhysiologyProfile
→ Race V2 intégré → S1–S3 → Réserve → S4+ → arrivée ou DNF
```

**Critère de sortie :** un scénario lisible et exactement reproductible traverse
réellement les deux systèmes.

#### F3 — Policy Training risk-aware

Conserver la baseline et ajouter au moins une policy technique intégrant
explicitement la probabilité de bust avant toute comparaison quantitative de
stratégies Training. Toutes restent des **EXPERIMENTAL TECHNICAL POLICIES**.
Une policy actuelle aveugle au risque ne représente pas un joueur rationnel.
Les conventions de Training V2 B2 diffèrent du Training CURRENT : ses résultats
ne permettent pas de conclure que « le risque CURRENT ne paie pas ».

**Critère de sortie :** une comparaison déterministe distingue effet de la
mécanique et effet d'un agent aveugle au risque.

#### F4 — Instrumentation et sensibilité Training → Race

Instrumenter contraintes saturées, CTL/upgrades, risques/busts, redistribution,
profil, options Race disponibles/payables, score, DNF et Réserve. Comparer, à
conditions Race et Difficulties comparables, au minimum un profil faiblement
entraîné, un profil intermédiaire et un profil fortement entraîné.

Question centrale : **le résultat du Training produit-il un écart de capacité
Race suffisamment visible pour que la préparation ait un poids réel ?** Mesurer
au minimum score, DNF, Production disponible et choisie, Réserve consommée et
restante, et effets selon Difficulty. Cette seule étude ne valide pas
l'équilibrage final.

**Critère de sortie :** le poids du Training sur Race est mesuré et interprétable.

#### F5 — Première campagne intégrée

Commencer par **100 à 1 000 trajectoires**, selon la question, pour un diagnostic
structurel, jamais un équilibrage final.

**Critère de sortie :** une relation interprétable est mesurée entre trajectoire
Training, profil physiologique et comportement en course.

### Porte G — Profondeur Race

**Priorité : P1 / P2.** Seulement après cohérence Cost ↔ Reserve et premier
end-to-end.

Comparer EFFICIENT, AGGRESSIVE, ADAPTIVE et GREEDY à une borne de référence
pour déterminer si une stratégie simple approche systématiquement l'optimum.
Une programmation dynamique ou un oracle doit distinguer explicitement :

```text
oracle avec information future ≠ policy jouable par un humain
```

Si possible, séparer optimum à information parfaite et meilleure policy non
anticipative.

**Critère de sortie :** on sait si les policies techniques laissent un espace
stratégique significatif ou si Race est quasi résolue dans certaines
configurations.

### Porte H — Calibration

**Priorité : P1 / P2 selon les résultats.** Seulement après les portes E à G,
un paramètre à la fois :

```text
1. Réserve
2. courbe physiologique / pentes
3. Form
4. Freshness
5. SL
```

Les pentes `2 / 3` restent **CALIBRATION EXPERIMENTAL** jusqu'à validation
explicite.

**Critère de sortie :** chaque paramètre est isolé, son protocole et ses limites
sont consignés, et toute décision de design est validée séparément.

### Porte I — Approfondissement du jeu

**Priorité : P2.** Après validation structurelle et calibration, réexaminer le
choix du dé écarté, l'ordre du programme, la présentation des choix Race, les
policies joueur, la lisibilité et le contrôle, puis Fatigue V1.

Avant Fatigue V1, séparer si nécessaire résolution et logging, découpler la
règle de fatigue de l'utilité des policies et ajouter uniquement l'état
persistant minimal. Ne pas engager de refonte architecturale générale.

**Critère de sortie :** le chantier répond à une observation de la boucle
intégrée et dispose de sa décision de design lorsque nécessaire.

## 5. LATER — ne pas faire maintenant

Les éléments suivants sont explicitement hors du chemin critique :

```text
SPEC
blessures
surentraînement définitif
nutrition
save-a-die D6
personnages
refonte générale du catalogue
format de données Godot
Godot
Event Bus
ECS
DI
GameEngine abstrait
GameState global
optimisation prématurée
Monte-Carlo massif
```

**OPEN — NOT IMPLEMENTED.** SPEC est différé, pas abandonné.

## 6. Dépendances et chemin critique

**PROPOSAL.**

```text
A — preuves fiables
        ↓
B — CURRENT protégé
        ↓
C — vision / piliers Game Design
        ↓
D — choix Training A/B/C
        ↓
E — cohérence Training ↔ Race et Cost ↔ Reserve
        ↓
F — end-to-end / simulation diagnostique
        ↓
G — profondeur Race
        ↓
H — calibration
        ↓
I — approfondissement
        ↓
LATER — extensions / Godot
```

A et B peuvent avancer en parallèle. C s'appuie sur leur état fiabilisé sans
choisir le futur modèle Training. D dépend explicitement des piliers de C. E
dépend du choix D ; F dépend du mapping et de la cohérence d'échelle E ; G suit
le premier end-to-end ; H dépend des diagnostics F et G. Fatigue et les
extensions ne doivent pas remonter avant cette chaîne.

```text
Impossible de choisir rationnellement A/B/C
sans critères de vision Game Design.

Impossible d'interpréter quantitativement Race V2 intégré
sans vérifier la cohérence d'échelle Cost ↔ Reserve.
```

## 7. Tableau de pilotage

| ID | Porte | Priorité | Nature | Action | Dépend de | Critère de sortie | Statut |
|---|---|---|---|---|---|---|---|
| A1 | A | P0 | TECH | Assainir F9 | — | A/A2/B/B2/C classés reproductibles ou historiques non reproductibles | TODO |
| A2 | A | P0 | AUDIT | Revalider les REPORT | A1 | conclusions reliées à des preuves classées | TODO |
| A3 | A | P0 | TECH | CI harness/JSON | A1 | régression analogue à F9 détectée | TODO |
| B1 | B | P0 | TECH | `validate_plan` ou équivalent | — | règles indépendantes du sélecteur | TODO |
| B2 | B | P0 | BUG | Trace EF | — | occurrences et redistributions distinctes | TODO |
| B3 | B | P0 | TEST | D99 table-driven complet | — | lignes CURRENT protégées, trois dés séparés | TODO |
| B4 | B | P0 | TECH | RNG injectable minimal | — | replay longitudinal déterministe | TODO |
| B5 | B | P0 | TEST | Transitions longitudinales | B1, B4 | transitions et invariants protégés | TODO |
| C1 | C | P0 — GAME DESIGN | DESIGN | Formaliser piliers / expérience cible | A, B | direction courte validée | TODO |
| C2 | C | P0 — GAME DESIGN | DESIGN | Critères de comparaison A/B/C | C1 | critères utilisables, pondération non présumée | TODO |
| D1 | D | P0 — GAME DESIGN | DESIGN | Choisir Training A/B/C | C2 | décision utilisateur puis GDD | TODO |
| E1 | E | P1 | DESIGN | Décisions strictement bloquantes | D1 | règles nécessaires définies | TODO |
| E2 | E | P1 | DESIGN+TECH | Mapping profil | D1, E1 | profil dérivé et documenté | TODO |
| E3 | E | P0 / P1 | DESIGN+SIM | Vérifier Cost ↔ Reserve | E2 | échelles compatibles | TODO |
| E4 | E | P1 | ANALYSE | D99 × upgrades | B3 | interaction mesurée sur pools accessibles | TODO |
| F1 | F | P1 | DESIGN | Cadre de partie minimal | C1, D1 | horizon ou cycle défini | TODO |
| F2 | F | P1 | TEST | End-to-end | E2, E3, F1 | Training → Race reproductible | TODO |
| F3 | F | P1 | SIM | Policy Training risk-aware | D1 | comparaison interprétable | TODO |
| F4 | F | P1 | SIM | Sensibilité Training → Race | F2 | poids du Training mesuré | TODO |
| F5 | F | P1 | SIM | Campagne diagnostique | F2, F3, F4 | relation Training/Race mesurée | TODO |
| G1 | G | P1 / P2 | ANALYSE | Solver / oracle Race | E3, F2 | profondeur stratégique mesurée | TODO |
| H1 | H | P1 / P2 | BALANCE | Calibration séquentielle | F5, G1 | paramètres étudiés séparément | TODO |
| I1 | I | P2 | DESIGN | Choix joueur / Fatigue | H1 | chantier justifié par les résultats | TODO |

## 8. Prochain chantier recommandé

**PROPOSAL.** Commencer par **A1 — assainissement chirurgical de F9**, tout en
préparant indépendamment les petites protections de la Porte B. A1 restaure la
qualité des preuves nécessaires à la future comparaison sans choisir le modèle
Training. La prochaine étape de Game Design est C1, puis C2 ; aucune décision
A/B/C ne doit les précéder. Aucun end-to-end ni résultat quantitatif Race ne
doit être interprété avant la vérification Cost ↔ Reserve de E3.
