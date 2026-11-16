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

**DESIGN UPDATE — 2026-11-16.** Le GDD V3 remplace le modèle physiologique Race énergie–vitesse par le modèle énergie–soutenabilité : l'énergie dépensée devient le score et la soutenabilité le coût de maintien. `docs/game-design/RACE_V2_DESIGN.md` reste une référence historique détaillée pour l'ancien modèle et les mécaniques tactiques qui devront être réexaminées. Le GDD est l'autorité pour le modèle actif.

**PROTOTYPE / EXPERIMENTAL — PR #67 fusionnée.** `experiments/current/race_v2_prototype/` orchestre une course multi-secteur avec forme du jour, cartes, groupes, aspiration, pool complet de dés, relances individuelles, sélection libre et capital global de relance. Le prototype ne constitue pas une boucle jouable complète et ne valide pas l'équilibrage.

**IMPLEMENTATION GAP — Training → Race.** Les entrées Race sont encore explicites : profil énergétique EF / Seuil / VMA, courbe énergie–soutenabilité, crédit initial `S0`, pool de dés et palier d'affûtage. Leur dérivation déterministe depuis un état Training B réel reste à spécifier et intégrer. L'AS comme entrée obligatoire et la table énergie → vitesse sont supersédées. Le mapping fatigue résiduelle → palier d'affûtage n'est pas implémenté.

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

**E0 — DOCUMENTATION : DONE par la consolidation GDD V3 et la mise à jour des références de gouvernance.** Le snapshot CURRENT_STATE reste daté du 12 novembre et décrit volontairement le code de cette date.

Après clôture documentaire, les points techniques encore ouverts sont :
- **E1 — Profil énergétique :** définir les coordonnées énergétiques EF / Seuil / VMA à partir de l'état Training B.
- **E2 — Courbe énergie–soutenabilité :** définir sa construction et son évolution à partir des adaptations intensives / extensives. L'AS comme entrée obligatoire de Race est supersédée.
- **E3 — Crédit initial :** définir la construction de `S0` depuis Training B, sans réintroduire l'ancien modèle de réserve fondé sur CTL.
- **E4 — Affûtage :** déterminer le palier depuis la fatigue résiduelle et le plus haut dé, puis vérifier sa cohérence avec Training B.
- **E5 — Validation de l'échelle :** vérifier la cohérence des plages de dépense, des consommations issues de la courbe énergie–soutenabilité et du solde de soutenabilité.

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
| R1 | Race | P0 | DESIGN | Consolider l'ancienne Race V2 énergie–vitesse | DONE — HISTORICAL, 2026-11-12 |
| R2 | Race | P1 | PROTOTYPE | Résolution secteur, orchestration, dés et relances | DONE — PR #67 fusionnée ; EXPERIMENTAL |
| E0 | E | P0 | DOCUMENTATION | Alignement transversal GDD / plan / snapshot / README / références | DONE — GDD V3 |
| E1 | E | P1 | DESIGN+TECH | Profil énergétique EF / Seuil / VMA Training → Race | BLOCKED — pause |
| E2 | E | P1 | DESIGN+TECH | Courbe énergie–soutenabilité | BLOCKED — pause |
| E3 | E | P1 | DESIGN+TECH | Construction de `S0` | BLOCKED — pause |
| E4 | E | P1 | DESIGN+TECH | Fatigue résiduelle → palier d'affûtage | BLOCKED — pause |
| E5 | E | P1 | ANALYSE | Cohérence dépense / soutenabilité Race | BLOCKED — pause |
| F1–F5 | F | P1 | TEST / SIM | Boucle end-to-end et diagnostics | LATER — dépend de E |
| G1 | G | P1/P2 | ANALYSE | Solver / oracle Race | LATER |
| H1 | H | P1/P2 | BALANCE | Calibration séquentielle | LATER |
| I1 | I | P2 | DESIGN | Choix joueur / fatigue | LATER |

## 6. Prochain chantier recommandé

**Maintenant :** revue utilisateur du GDD V3 et des références documentaires alignées. La consolidation E0 est terminée ; aucun code, test, harness ou résultat de simulation n'est modifié par cette étape.

**Ensuite :** la reprise du travail de conception ou d'implémentation nécessite une instruction explicite. Le premier chantier de fond devra formaliser le profil énergétique EF / Seuil / VMA, la courbe énergie–soutenabilité et la construction de S0, puis vérifier le lien entre fatigue résiduelle et affûtage. Les paramètres manquants doivent rester OPEN plutôt que recevoir des valeurs arbitraires.

La pause d'implémentation après PR #67 reste en vigueur. La présente mise à jour documentaire ne la lève pas.
