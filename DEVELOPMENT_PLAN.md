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

### Training B — cible et prototype

**DECISION VALIDATED — cible B.** Training B est la base de développement. Le Training CURRENT historique est conservé comme référence, sans obligation de compatibilité. Le prototype `training_v2/` reste partiel et monoposte ; les règles et paramètres issus des harnesses demeurent EXPERIMENTAL tant qu'ils ne sont pas explicitement promus dans le GDD.

La cohérence Training ↔ Race n'est pas encore réalisée. Ne pas déduire de configuration Race complète depuis les seules expériences synthétiques.

### Race V2 — règles et prototype

**DECISION VALIDATED — design Race V2 consolidé le 2026-11-12.** Les règles détaillées sont dans `docs/game-design/RACE_V2_DESIGN.md` et leur statut normatif est résumé dans le GDD.

**PROTOTYPE / EXPERIMENTAL — PR #67 fusionnée.** `experiments/current/race_v2_prototype/` orchestre une course multi-secteur avec forme du jour, cartes, groupes, aspiration, pool complet de dés, relances individuelles, sélection libre et capital global de relance. Le prototype ne constitue pas une boucle jouable complète et ne valide pas l'équilibrage.

**IMPLEMENTATION GAP — Training → Race.** Les entrées Race sont encore explicites : table physiologique entière, AS, crédit initial `S0`, pool de dés et palier d'affûtage. Leur dérivation déterministe depuis un état Training B réel reste à spécifier et intégrer. En particulier, le mapping fatigue résiduelle → palier d'affûtage n'est pas implémenté.

### Pause d'implémentation — 2026-11-12

À la demande de l'utilisateur, l'implémentation est suspendue après PR #67. Le chantier immédiat est documentaire : aligner GDD, spécification Race V2, snapshot d'implémentation, README, roadmap et références historiques. Aucun nouveau code, mapping Training → Race ou calibrage ne doit être engagé avant clôture de cette consolidation et nouvelle instruction explicite.

## 3. Portes et statut

### Porte A — Fiabilité des preuves (P0)

A1, A2 et A3 sont terminées sur leur périmètre documenté. Les rapports et harnesses restent des preuves techniques limitées ; ils ne constituent pas des validations automatiques de design.

### Porte B — Training CURRENT historique

B1 à B5 sont clôturées sur le périmètre de l'ancien Training. Ce système est conservé comme référence historique et n'est pas le chemin de développement cible.

### Porte C — Vision et expérience cible (P0 — GAME DESIGN)

C1/C2 sont terminées : fantaisie d'un entraîneur qui prépare une course ; cible d'environ 2/3 Training et 1/3 Race, 60–90 minutes, principalement 2–4 joueurs, 12–16 tours de Training à tester. La qualité de la préparation prime sur le seul résultat de course.

### Porte D — Training B

Training B est la cible validée. Son prototype et ses décisions doivent continuer à être distingués des paramètres expérimentaux des harnesses. La promotion des règles dans le GDD suit les décisions explicites, pas le seul état du code.

### Porte E — Cohérence Training ↔ Race

**E0 — DOCUMENTATION : EN COURS dans cette PR.** Réconcilier les documents normatifs, le snapshot du code et les références obsolètes.

Après clôture documentaire, les points techniques encore ouverts sont :
- **E1 — Table physiologique :** définir la dérivation de la table entière Race à partir du profil Training B, sans interpolation.
- **E2 — AS :** déterminer la valeur propre à la course et son lien avec le profil Training.
- **E3 — Soutenabilité initiale :** définir la construction de `S0` depuis le Training ; ne pas réutiliser implicitement l'ancien modèle de réserve basé sur investissements EF/Seuil/VMA ou CTL.
- **E4 — Affûtage :** déterminer le palier depuis la fatigue résiduelle et le plus haut dé, conformément aux seuils du GDD.
- **E5 — Validation de l'échelle :** vérifier la cohérence des plages de dépense, de la consommation par rapport à AS et de la soutenabilité, sans lancer de campagne massive prématurée.

### Porte F — Boucle end-to-end (LATER / bloquée par E)

Une fois E défini et explicitement relancé :
- scénario déterministe Training → profil → Race ;
- vérification des transitions et diagnostics ;
- première observation de profils faibles/intermédiaires/forts ;
- évaluation de la lisibilité et de la durée de la boucle.

Aucune de ces tâches ne démarre pendant la pause documentaire.

### Portes ultérieures

Solver/oracle Race, calibration séquentielle des paramètres, politique joueur et équilibrage humain viennent après une première boucle intégrée. Les expériences automatiques ne remplacent pas les tests avec joueurs.

### LATER

SPEC, blessures, surentraînement définitif, nutrition, save-a-die, personnages, Godot, Event Bus, ECS, DI, moteur abstrait, état global, optimisation prématurée et Monte-Carlo massif restent différés. SPEC est OPEN / NOT IMPLEMENTED, pas abandonné.

## 4. Dépendances et chemin critique

```text
A — preuves fiables ─┐
                     ├→ C — vision / cible B → D — Training B
B — audit historique ┘                         │
                                               ↓
                                   E0 — consolidation documentaire
                                               │
                               [pause d'implémentation — 12/11]
                                               │
                          E1–E5 — Training → Race (à relancer)
                                               ↓
                                  F — boucle end-to-end
                                               ↓
                                  G — diagnostics / solver
                                               ↓
                                  H — calibration / I — choix joueur
```

Le jalon immédiat est la consolidation documentaire E0. L'implémentation reste suspendue après PR #67. La reprise de E1–E5 et de la boucle end-to-end nécessite une instruction explicite après revue de la documentation.

## 5. Tableau de pilotage

| ID | Porte | Priorité | Nature | Action | Statut |
|---|---|---|---|---|---|
| A1–A3 | A | P0 | AUDIT / TEST | Fiabilité des preuves et CI harness | DONE |
| B1–B5 | B | P0 | TECH / TEST | Intégrité de l'ancien Training CURRENT | DONE — HISTORICAL |
| C1–C2 | C | P0 | DESIGN | Vision et trajectoire Training B | DONE — validé 2026-11-07 |
| D1 | D | P0 | DESIGN | Training B comme cible | DONE — validé 2026-11-07 |
| R1 | Race | P0 | DESIGN | Consolider les décisions Race V2 | DONE — 2026-11-12 |
| R2 | Race | P1 | PROTOTYPE | Résolution secteur, orchestration, dés et relances | DONE — PR #67 fusionnée ; EXPERIMENTAL |
| E0 | E | P0 | DOCUMENTATION | Alignement transversal GDD / plan / snapshot / README / références | IN PROGRESS |
| E1 | E | P1 | DESIGN+TECH | Table physiologique Training → Race | BLOCKED — pause |
| E2 | E | P1 | DESIGN+TECH | Mapping de l'AS | BLOCKED — pause |
| E3 | E | P1 | DESIGN+TECH | Construction de `S0` | BLOCKED — pause |
| E4 | E | P1 | DESIGN+TECH | Fatigue résiduelle → palier d'affûtage | BLOCKED — pause |
| E5 | E | P1 | ANALYSE | Cohérence des échelles Race | BLOCKED — pause |
| F1–F5 | F | P1 | TEST / SIM | Boucle end-to-end et diagnostics | LATER — dépend de E |
| G1 | G | P1/P2 | ANALYSE | Solver / oracle Race | LATER |
| H1 | H | P1/P2 | BALANCE | Calibration séquentielle | LATER |
| I1 | I | P2 | DESIGN | Choix joueur / fatigue | LATER |

## 6. Prochain chantier recommandé

**B1 TERMINÉ — PR #38 :** catalogue déclaratif et adaptations fixes génériques.

**B2 — coût énergétique distinct du RPE.** Les séances Seuil/VMA portent maintenant un coût énergétique fixe et un RPE indépendant. Le coût est payé sur l'énergie allouée ; le RPE pilote l'entrée dans le test de risque/bust. Les valeurs du catalogue sont des fixtures D1-S4 expérimentales, non calibrées.

**B3 EN COURS — allocation directe des dés aux séances.** Remplacer la partition EF/Qualité par une composition où chaque dé conservé finance une occurrence du catalogue. Socle EF/Seuil/VMA, répétition EF ouverte, limites de répétition spécifiques par entrée. Aucun combo. Les fixtures de coût, RPE, adaptations et fatigue r## 6. Prochain chantier recommandé

**Maintenant :** terminer E0, la consolidation documentaire. Cette PR ne doit modifier aucun code, aucun test ni aucune sortie de simulation.

**Ensuite :** faire une revue utilisateur des documents synchronisés. La reprise de l'implémentation ne sera pas implicite. Le prochain chantier technique, lorsqu'il sera autorisé, devra commencer par un audit ciblé des états Training B et des entrées Race nécessaires (table physiologique, AS, `S0`, pool de dés, affûtage), puis proposer un mapping sans inventer les valeurs manquantes.

