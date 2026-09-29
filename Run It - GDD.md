# Run It — GDD V2 consolidé

**29 septembre 2026 · jalon technique : `Integrated V2 baseline` (commit/PR de référence consigné à la clôture).** Le présent GDD décrit les décisions de design CURRENT, les mécanismes EXPERIMENTAL et les questions OPEN. `CURRENT_STATE.md` décrit l'état du prototype ; `DOCUMENTATION_AUDIT.md` explique les remplacements du GDD antérieur. Le code n'établit pas à lui seul une règle de design.

## 1. Concept

Run It est un jeu tactique de préparation à la course. Les joueurs construisent leur pool de dés, composent des séances sous contraintes d'énergie et de risque, développent leur forme et gèrent leur fatigue. La course finale donne un sens aux décisions de préparation. Son noyau physiologique Race V2 est intégré ; son orchestration complète et son équilibrage restent partiellement OPEN ou EXPERIMENTAL selon les éléments ci-dessous.

## 2. Dés et tour — CURRENT

### D0–D3. Pool et actions

- Pool persistant initial : `4d6`. Progression : `4d6 → 5d6 → 6d6` ; ajout d'un d6 aux seuils de CTL cumulé 50 et 100. Un gain obtenu pendant un tour devient utilisable au tour suivant.
- Normalement, `n` dés dans le pool donnent `n − 1` dés actifs ; un motif D99 favorable ou l'action d'ajouter peut faire entrer le dé de réserve dans le lancer final. Choix du lancer : conserver, relancer, ajouter, ajouter et relancer. Une politique automatique de simulation ne fixe pas le choix du joueur.
- Le lancer final détermine le budget d'énergie, RPE Max et le plafond D99. L'énergie est la somme des valeurs retenues, sans plafond TN. Le dé à écarter est actuellement choisi automatiquement ; le choix stratégique par le joueur reste une évolution future.

### D4. Dés améliorés

Une amélioration après chaque tranche de quatre qualités réussies, au maximum quatre améliorations sur tout le pool. Chaque amélioration fait avancer un dé d'un cran : `d6 → d8 → d10 → d12`. Le choix du dé est, en design, celui du joueur ; le prototype utilise une politique automatique.

**CURRENT :** les d8/d10/d12 n'ajoutent aucun bonus permanent (`0/0/0`). Les anciens bonus `+1/+2/+3` sont **HISTORICAL** ; les moyennes calculées avec ces bonus ne sont pas des références CURRENT.

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

Le catalogue d'entraînement actuellement codé contient EF, Seuil, VMA, Force, des entrées Spec existantes et SL. Le RPE est le coût en énergie de la séance. **IMPLEMENTATION GAP :** ces entrées Spec du prototype ne définissent pas le mécanisme SPEC V2, qui reste OPEN et absent de Race V2. Seuil, VMA, Force, Spec et SL sont des qualités ; EF ne l'est pas. Les prérequis forment un graphe explicite, y compris ses embranchements : aucune progression n'est inférée du nom d'une séance.

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

**IMPLEMENTATION :** le moteur expose les options de redistribution puis valide le choix explicite du joueur, y compris un choix vide, partiel, multiple ou répétant une EF autorisée. Il ne sélectionne pas lui-même les EF. Une éventuelle interface utilisateur reste un chantier distinct de cette frontière de règle, qui est implémentée.

La **dépense réellement réalisée** est la somme des coûts des séances réussies après bust et éventuelle redistribution. L'énergie de la séance busted est perdue mais ne devient ni CTL ni charge réalisée pour Fatigue V1 ; l'énergie simplement non dépensée n'est pas réalisée non plus.

### B2. Blessure et surentraînement

Le bust décrit ici une annulation de séance, sans conséquence de blessure persistante automatiquement validée. Blessures et effets définitifs du surentraînement restent FUTURE / OPEN. Un retrait temporaire d'un dé a été exercé dans des expériences de Fatigue V1, sans valider les anciens seuils, tables ou modificateurs de risque du GDD ; le risque CURRENT n'est pas modifié par le surentraînement.

## 5. SL — direction CURRENT, seuils de course OPEN

SL est une préparation spécifique à la course ; elle n'est pas intrinsèquement supérieure à une autre qualité dans une utilité générique. Les seuils de SL nécessaires à la course restent OPEN. **IMPLEMENTATION / POLICY GAP :** le sélecteur automatique du prototype lui accorde encore une priorité spéciale, antérieure à cette clarification. Le maintien ou la suppression de cette priorité requiert un arbitrage ultérieur.

## 6. Politiques joueur et expériences

**P0** est une baseline technique conservatrice, ni joueur humain standard, ni référence de design, ni stratégie optimale. Le **Standard Training Player** est EXPERIMENTAL. Ces noms de politiques ne désignent pas les anciennes rubriques P0–P4 du GDD. Le sélecteur pondéré, ses poids et ses choix gloutons sont des politiques techniques, pas des préférences imposées au joueur.

Les anciennes campagnes Fatigue V1, Overtraining Capacity, P0 et Standard Player antérieures aux corrections de D99, répétitions, bust, accès au risque et rôle de SL sont **HISTORICAL ONLY** pour leurs chiffres. Leurs observations gardent une valeur de traçabilité ; elles ne constituent pas une baseline d'équilibrage CURRENT.

## 7. Course V2 — noyau intégré, calibration expérimentale, questions OPEN

### 7.1 Profil physiologique — BASE V2 INTÉGRÉE

Le passage futur du Training vers la course utilise un `PhysiologyProfile(EF, Seuil, VMA)` avec l'invariant strict `EF < Seuil < VMA` :

- **EF** est l'origine de coût : `C(EF) = 0` ;
- **Seuil** est le changement de régime de la courbe énergétique ;
- **VMA** est la borne haute physiologique du domaine intégré.

Aucune contrainte supplémentaire sur `VMA − EF` n'est posée et `C(VMA)` n'est pas normalisé dans une enveloppe fixe. Une Charge sous EF est explicitement hors domaine, sans clamp silencieux. La légalité et le coût d'une Charge supérieure à VMA sont **OPEN** : l'implémentation signale ce cas et ne transforme pas VMA en plafond de Production.

La courbe native intégrée est :

```text
C(x) = 2 × (x − EF)                                si x ≤ Seuil
C(x) = 2 × (Seuil − EF) + 3 × (x − Seuil)         si x > Seuil
```

Sa structure (origine EF, rupture Seuil, borne VMA) est intégrée. Les pentes `2 / 3` sont une **CALIBRATION EXPERIMENTAL**, pas un équilibrage CURRENT définitif.

### 7.2 Résolution locale Race V2 — CURRENT / INTÉGRÉ

Pour un segment dans le domaine physiologique :

```text
Charge = Production + Difficulty
Cost = C(Charge)
Score += Production
Reserve -= Cost
```

Difficulty ne donne aucun score, ne retire jamais directement de Réserve et ne possède aucun état persistant propre. Le noyau intégré expose cette résolution pure. La construction de la Réserve, Form, les politiques de choix, les longueurs et objectifs de course, la conversion complète du Training et le rôle concret de SL restent **EXPERIMENTAL** ou **OPEN** ; les tables Curve A/B/C sont conservées uniquement pour reproduire les expériences historiques.

### 7.3 SPEC et anciens concepts — OPEN / EXPERIMENTAL / HISTORICAL

**SPEC = OPEN — NOT IMPLEMENTED** dans le chemin V2 intégré. SPEC Position, SPEC Efficacité et AS42/AS21/AS10/AS5 ne sont pas des règles actives de coût. Les expériences qui les étudient demeurent des sondes **EXPERIMENTAL** relatives à une question OPEN, pas la baseline et pas une piste déclarée abandonnée. Les anciennes esquisses Mental / Pacing / Physique, objectifs secrets, personnages et manipulations sont **HISTORICAL** et ne spécifient pas Race V2.

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
