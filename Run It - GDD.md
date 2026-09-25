# Run It — GDD V2 consolidé

**24 septembre 2026 · référence technique : `main`, commit `e0c3680bb90a6276f907340acedf3091d7eb71bf`.** Le présent GDD décrit les décisions de design CURRENT, les mécanismes EXPERIMENTAL et les questions OPEN. `CURRENT_STATE.md` décrit l'état du prototype ; `DOCUMENTATION_AUDIT.md` explique les remplacements du GDD antérieur. Le code n'établit pas à lui seul une règle de design.

## 1. Concept

Run It est un jeu tactique de préparation à la course. Les joueurs construisent leur pool de dés, composent des séances sous contraintes d'énergie et de risque, développent leur forme et gèrent leur fatigue. La course finale doit donner un sens aux décisions de préparation ; son système exact reste OPEN.

## 2. Dés et tour — CURRENT

### D0–D3. Pool et actions

- Pool persistant initial : `4d6`. Progression : `4d6 → 5d6 → 6d6` ; ajout d'un d6 aux seuils de CTL cumulé 50 et 100. Un gain obtenu pendant un tour devient utilisable au tour suivant.
- Normalement, `n` dés dans le pool donnent `n − 1` dés actifs ; un motif D99 favorable ou l'action d'ajouter peut faire entrer le dé de réserve dans le lancer final. Choix du lancer : conserver, relancer, ajouter, ajouter et relancer. Une politique automatique de simulation ne fixe pas le choix du joueur.
- Le lancer final détermine le budget d'énergie, RPE Max et le plafond D99. L'énergie est la somme des valeurs retenues, sans plafond TN. Le dé à écarter est actuellement choisi automatiquement ; le choix stratégique par le joueur reste une évolution future.

### D4. Dés améliorés

Une amélioration après chaque tranche de quatre qualités réussies, au maximum quatre améliorations sur tout le pool. Chaque amélioration fait avancer un dé d'un cran : `d6 → d8 → d10 → d12`. Le choix du dé est, en design, celui du joueur ; le prototype utilise une politique automatique.

**OPEN — DOCUMENTATION CONFLICT :** le GDD précédent attribuait aux d8/d10/d12 des bonus permanents `+1/+2/+3` ; le prototype configure `0/0/0`. La décision définitive sur ces bonus n'est pas déduite du code. Les anciennes moyennes calculées avec bonus ne sont pas des références CURRENT.

### D5–D6. Récupération et dé conservé

Il n'y a pas de partage des dés d'action entre énergie et ressource de récupération. La récupération est intégrée au calcul de fatigue après les séances. La conservation d'un dé d'un tour à l'autre (« save a die ») reste FUTURE / EXPERIMENTAL.

### D99. Motifs

Les motifs du **lancer final** sont déterminés par les faces brutes. Ils fixent **avant la composition** un plafond de qualités planifiables ; SL en consomme un slot. Certains motifs permettent aussi de retenir le dé de réserve. Dans la table, les nombres indiquent les tailles des groupes de faces identiques.

| Dés du lancer final | Motif | Plafond de qualités | Bonus de réserve |
|---|---|---:|---|
| 3 | `1+1+1` | 1 | non |
| 3 | `2+1`, `3` | 2 | non |
| 4 | `1+1+1+1` | 1 | non |
| 4 | `2+1+1` | 2 | non |
| 4 | `3+1`, `2+2` | 2 | oui |
| 4 | `4` | 3 | oui |
| 5 | `1+1+1+1+1` | 1 | non |
| 5 | `2+1+1+1` | 2 | non |
| 5 | `2+2+1`, `3+1+1` | 2 | oui |
| 5 | `3+2`, `4+1`, `5` | 3 | oui |
| 6 | `1+1+1+1+1+1` | 1 | non |
| 6 | `2+1+1+1+1` | 2 | non |
| 6 | `2+2+1+1`, `3+1+1+1` | 2 | oui |
| 6 | `3+2+1`, `2+2+2`, `4+1+1`, `4+2`, `3+3`, `5+1`, `6` | 3 | oui |

Les lignes à trois dés reproduisent l'extrapolation du prototype ; leur statut de design demeure **OPEN / IMPLEMENTATION POLICY**, comme expliqué dans le registre. Les lignes à quatre, cinq et six dés décrivent les effets D99 courants.

Un slot D99 est consommé dès qu'une qualité est planifiée, même si elle bust ou est annulée après un bust. Aucun remboursement ni replanification de qualité. Le plafond ne garantit pas que toutes les qualités seront réalisées. Les anciennes tables de probabilités du GDD ne sont pas utilisables telles quelles pour l'équilibrage CURRENT ; elles devront être recalculées pour les pools et règles étudiés.

## 3. Séances et progression — CURRENT

### S0. Catalogue

Le catalogue contient EF, Seuil, VMA, Force, Spec et SL. Le RPE est le coût en énergie de la séance. Seuil, VMA, Force, Spec et SL sont des qualités ; EF ne l'est pas. Les prérequis forment un graphe explicite, y compris ses embranchements : aucune progression n'est inférée du nom d'une séance.

Une séance **débloquée** satisfait son seuil normal de prérequis. Une qualité verrouillée devient **tentable** si l'un de ses prédécesseurs directs est normalement débloqué et a été réussi au moins une fois. Ce droit de tentative ne modifie pas le seuil normal. Exemple : Spec6 disponible et réussie zéro fois ne permet pas Spec7 ; une réussite rend Spec7 tentable ; deux la débloquent normalement. Spec8 ne devient pas tentable par ce seul fait. L'anticipation ne concerne pas les EF.

### S1. Composition du programme

- La somme des coûts des séances planifiées ne dépasse pas le budget d'énergie ; au plus **sept séances comptées** dans le tour.
- EF est librement répétable dans la limite des autres contraintes. Une entrée précise de qualité ne peut figurer qu'une fois dans le tour.
- `qualités ≤ EF` **dans le même tour**, et `qualités ≤ plafond D99`. Une EF des tours précédents n'ouvre pas un slot de qualité du tour actuel.
- SL est une qualité : elle consomme un slot D99, est unique et reste limitée à **une SL par tour**.

Les anciennes cibles chiffrées de qualités par partie, calculées sous des règles différentes, demandent une nouvelle étude.

### S2. RPE Max et accès volontaire au risque

RPE Max délimite la **zone sûre du tour**, pas un plafond absolu pour les qualités. Choisir une qualité tentable de RPE supérieur engage le risque sans coût ni déclaration supplémentaire. Une EF supérieure à RPE Max reste interdite. L'accès au catalogue interdit les sauts de progression ; aucun plafond arbitraire `RPE Max + x` n'est ajouté. Une qualité dont `k = RPE − RPE Max` atteint la taille du meilleur dé du pool persistant est exclue, car le bust serait certain.

### S3. Ordre du tour et progression

Le programme est composé, puis les risques sont testés dans l'ordre, puis le bust et les séances sont résolus, puis CTL et fatigue sont calculés sur la charge effectivement réalisée. Le CTL du tour est la somme des RPE des séances **réussies** après résolution et éventuelle redistribution EF. Seules les séances réussies contribuent aux prérequis ; seules les qualités réussies comptent vers les améliorations de dés. Les ajouts et améliorations acquis deviennent disponibles au tour suivant.

## 4. Risque et bust — CURRENT

### B0. Test

Une qualité est risquée exactement quand `RPE séance > RPE Max`, avec `k = RPE séance − RPE Max`. On lance le meilleur dé du **pool persistant entier** (actif ou en réserve) et compare sa **face brute** : bust si `face ≤ k`. Les risques sont testés dans l'ordre prévu ; le premier bust interrompt les tests ultérieurs. Les séances sûres ne demandent pas de test. Le seuil CURRENT est `k`, avec modulation neutre : TN, dépense et fatigue persistante n'ajoutent aucun modificateur. Une modulation future reste EXPERIMENTAL.

### B1. Conséquences et redistribution

La qualité busted compte parmi les sept séances et consomme son slot D99. Son énergie est perdue ; elle ne produit ni CTL, ni progression, ni surcharge qualitative S. Les qualités risquées prévues après elle sont annulées comme qualités et ne sont plus testées ; leurs slots D99 sont perdus, elles ne produisent ni CTL, ni progression, ni S. Leur énergie planifiée n'est pas automatiquement perdue.

**DESIGN CURRENT :** le joueur choisit comment réaffecter cette énergie en EF accessibles, dans la limite de l'énergie récupérable, de l'accès RPE et des places disponibles jusqu'à sept séances comptées. Une qualité annulée ne réserve pas une place. Les séances sûres prévues restent réalisées, même après le bust. Aucune nouvelle qualité ne remplace celles annulées.

**IMPLEMENTATION GAP :** le prototype redistribue aujourd'hui automatiquement et de façon gloutonne vers les EF. L'interface du choix joueur reste à spécifier et à implémenter ; le présent GDD n'en décide pas l'algorithme.

La **dépense réellement réalisée** est la somme des coûts des séances réussies après bust et éventuelle redistribution. L'énergie de la séance busted est perdue mais ne devient ni CTL ni charge réalisée pour Fatigue V1 ; l'énergie simplement non dépensée n'est pas réalisée non plus.

### B2. Blessure et surentraînement

Le bust décrit ici une annulation de séance, sans conséquence de blessure persistante automatiquement validée. Blessures et effets définitifs du surentraînement restent FUTURE / OPEN. Un retrait temporaire d'un dé a été exercé dans des expériences de Fatigue V1, sans valider les anciens seuils, tables ou modificateurs de risque du GDD ; le risque CURRENT n'est pas modifié par le surentraînement.

## 5. SL — direction CURRENT, seuils de course OPEN

SL est une préparation spécifique à la course ; elle n'est pas intrinsèquement supérieure à une autre qualité dans une utilité générique. Les seuils de SL nécessaires à la course restent OPEN. **IMPLEMENTATION / POLICY GAP :** le sélecteur automatique du prototype lui accorde encore une priorité spéciale, antérieure à cette clarification. Le maintien ou la suppression de cette priorité requiert un arbitrage ultérieur.

## 6. Politiques joueur et expériences

**P0** est une baseline technique conservatrice, ni joueur humain standard, ni référence de design, ni stratégie optimale. Le **Standard Training Player** est EXPERIMENTAL. Ces noms de politiques ne désignent pas les anciennes rubriques P0–P4 du GDD. Le sélecteur pondéré, ses poids et ses choix gloutons sont des politiques techniques, pas des préférences imposées au joueur.

Les anciennes campagnes Fatigue V1, Overtraining Capacity, P0 et Standard Player antérieures aux corrections de D99, répétitions, bust, accès au risque et rôle de SL sont **HISTORICAL ONLY** pour leurs chiffres. Leurs observations gardent une valeur de traçabilité ; elles ne constituent pas une baseline d'équilibrage CURRENT.

## 7. Course et personnages — OPEN / FUTURE

La boucle minimale à définir est **entraînement → progression, fatigue et SL → course → résultat**. Les anciennes esquisses de mental, pacing, physique, plan d'entraînement, objectifs secrets, personnages, manipulations et nombre de phases ne spécifient pas un système CURRENT complet. Elles restent des pistes historiques consultables dans la version antérieure du GDD ; leurs seuils, formules et conséquences exigent un arbitrage. Aucun système de course n'est décidé dans cette consolidation.

## 8. Fatigue V1 — EXPERIMENTAL

### 8.1–8.4. Statut et ordre de calcul

Fatigue V1 est une mécanique testable dont l'équilibrage final reste ouvert. Elle distingue `Q` (surcharge quantitative), `Recovery` (récupération) et `S` (surcharge qualitative). On résout le programme, le premier bust et l'éventuelle redistribution EF **avant** de calculer la dépense `E = somme des RPE des séances réussies`, puis `Δ = E − TN`. Les qualités busted ou annulées ne contribuent pas à `S`.

### 8.5. Q — surcharge quantitative

| `Δ` | `Q` |
|---:|---:|
| `≤ 0` | 0 |
| `+1` | +1 |
| `+2` | +2 |
| `+3` | +3 |
| `+4` | +5 |
| `+5` | +8 |
| `≥ +6` | +13 |

### 8.6. Recovery — récupération

| `Δ` | `Recovery` |
|---:|---:|
| `≥ −1` | 0 |
| `−2` | −1 |
| `−3` | −2 |
| `−4` | −3 |
| `≤ −5` | −4 |

### 8.7–8.11. S, dette et limites

Pour chaque qualité risquée **réussie**, `S` augmente de `RPE − RPE Max`. Ces dépassements s'additionnent pendant le tour. Une séance busted et une qualité risquée ultérieure annulée donnent chacune `S = 0`.

`fatigue brute suivante = fatigue actuelle + Q + S + Recovery`

`fatigue suivante = max(−taille du meilleur dé persistant, fatigue brute suivante)`.

Les tables, la borne négative et la dette sont des paramètres **expérimentaux**, pas un équilibrage final. Le calcul de fatigue de la production ne constitue pas une implémentation complète de cette dette persistante. L'expression « fatigue négative = affûtage » reste une interprétation à valider, pas un bénéfice mécanique CURRENT.

### 8.12–8.14. Politiques, cible et décision

P0 caractérise une baseline technique conservatrice. Standard Training Player reste un outil EXPERIMENTAL ; ses chiffres antérieurs aux corrections de composition et de bust ne démontrent aucun régime joueur standard. Le régime de fatigue souhaité, l'équilibre Q/S/Recovery, la fréquence de surentraînement, la sévérité finale et les effets de la fatigue sur les choix du joueur demeurent OPEN. Une nouvelle observation sous les règles consolidées doit précéder tout arbitrage d'équilibrage.
