# Run It — GDD V2 consolidé

**Mise à jour documentaire : 12 novembre 2026.** Le jalon historique `Integrated V2 baseline` du 29 septembre reste une référence de l'état antérieur, pas une description complète de Race V2. Le présent GDD décrit les décisions de design CURRENT, les mécanismes EXPERIMENTAL et les questions OPEN. `CURRENT_STATE.md` décrit l'état du prototype ; `DOCUMENTATION_AUDIT.md` explique les remplacements du GDD antérieur. Le code n'établit pas à lui seul une règle de design.

## 1. Concept

Run It est un jeu tactique de préparation à la course. Les joueurs construisent leur pool de dés, composent des séances sous contraintes d'énergie et de risque, développent leur forme et gèrent leur fatigue. La course finale donne un sens aux décisions de préparation. Training B est la cible de développement validée. Race V2 dispose désormais d'un prototype multi-secteur avec dés et relances ; le raccordement complet au Training et l'équilibrage restent ouverts ou expérimentaux.

> **Évolution de trajectoire — 7 novembre 2026 :** le joueur a validé Training B comme cible de développement, avec possibilité d'extensions ultérieures vers C. Le modèle Training CURRENT décrit dans les sections 2 à 6 ci-dessous est conservé comme référence **HISTORICAL / RETIRED TARGET** ; il ne constitue plus la base des nouvelles règles ou implémentations. Les décisions détaillées de Training B seront promues dans ce GDD au fur et à mesure de leur validation.

## 2. Dés et tour — HISTORICAL (ancien Training CURRENT)

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

## 3. Séances et progression — HISTORICAL (ancien Training CURRENT)

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

## 4. Risque et bust — HISTORICAL (ancien Training CURRENT)

### B0. Test

Une qualité est risquée exactement quand `RPE séance > RPE Max`, avec `k = RPE séance − RPE Max`. On lance le meilleur dé du **pool persistant entier** (actif ou en réserve) et compare sa **face brute** : bust si `face ≤ k`. Les risques sont testés dans l'ordre prévu ; le premier bust interrompt les tests ultérieurs. Les séances sûres ne demandent pas de test. Le seuil CURRENT est `k`, avec modulation neutre : TN, dépense et fatigue persistante n'ajoutent aucun modificateur. Une modulation future reste EXPERIMENTAL.

### B1. Conséquences et redistribution

La qualité busted compte parmi les sept séances et consomme son slot D99. Son énergie est perdue ; elle ne produit ni CTL, ni progression, ni surcharge qualitative S. Les qualités risquées prévues après elle sont annulées comme qualités et ne sont plus testées ; leurs slots D99 sont perdus, elles ne produisent ni CTL, ni progression, ni S. Leur énergie planifiée n'est pas automatiquement perdue.

**DESIGN CURRENT :** le joueur choisit comment réaffecter cette énergie en EF accessibles, dans la limite de l'énergie récupérable, de l'accès RPE et des places disponibles jusqu'à sept séances comptées. Une qualité annulée ne réserve pas une place. Les séances sûres prévues restent réalisées, même après le bust. Aucune nouvelle qualité ne remplace celles annulées.

**IMPLEMENTATION :** le moteur expose les options de redistribution puis valide le choix explicite du joueur, y compris un choix vide, partiel, multiple ou répétant une EF autorisée. Il ne sélectionne pas lui-même les EF. Une éventuelle interface utilisateur reste un chantier distinct de cette frontière de règle, qui est implémentée.

La **dépense réellement réalisée** est la somme des coûts des séances réussies après bust et éventuelle redistribution. L'énergie de la séance busted est perdue mais ne devient ni CTL ni charge réalisée pour Fatigue V1 ; l'énergie simplement non dépensée n'est pas réalisée non plus.

### B2. Blessure et surentraînement

Le bust décrit ici une annulation de séance, sans conséquence de blessure persistante automatiquement validée. Blessures et effets définitifs du surentraînement restent FUTURE / OPEN. Un retrait temporaire d'un dé a été exercé dans des expériences de Fatigue V1, sans valider les anciens seuils, tables ou modificateurs de risque du GDD ; le risque CURRENT n'est pas modifié par le surentraînement.

## 5. SL — HISTORICAL (ancien Training CURRENT), seuils de course OPEN

SL est une préparation spécifique à la course ; elle n'est pas intrinsèquement supérieure à une autre qualité dans une utilité générique. Les seuils de SL nécessaires à la course restent OPEN. **IMPLEMENTATION / POLICY GAP :** le sélecteur automatique du prototype lui accorde encore une priorité spéciale, antérieure à cette clarification. Le maintien ou la suppression de cette priorité requiert un arbitrage ultérieur.

## 6. Politiques joueur et expériences — HISTORICAL / EXPERIMENTAL

**P0** est une baseline technique conservatrice, ni joueur humain standard, ni référence de design, ni stratégie optimale. Le **Standard Training Player** est EXPERIMENTAL. Ces noms de politiques ne désignent pas les anciennes rubriques P0–P4 du GDD. Le sélecteur pondéré, ses poids et ses choix gloutons sont des politiques techniques, pas des préférences imposées au joueur.

Les anciennes campagnes Fatigue V1, Overtraining Capacity, P0 et Standard Player antérieures aux corrections de D99, répétitions, bust, accès au risque et rôle de SL sont **HISTORICAL ONLY** pour leurs chiffres. Leurs observations gardent une valeur de traçabilité ; elles ne constituent pas une baseline d'équilibrage CURRENT.

## 7. Race V2 — règles validées, prototype expérimental, intégration Training OPEN

La conception Race V2 est consolidée dans [`docs/game-design/RACE_V2_DESIGN.md`](docs/game-design/RACE_V2_DESIGN.md), qui constitue la spécification détaillée des décisions validées le 12 novembre 2026. Le présent GDD en fixe le statut et les principes normatifs.

**Statut à distinguer :**
- **DECISION VALIDATED :** règles décrites ci-dessous et dans la spécification détaillée.
- **PROTOTYPE / EXPERIMENTAL :** orchestration multi-secteur et décisions de dés présentes dans `experiments/current/race_v2_prototype/`. Leur présence dans le code ne constitue pas une validation d'équilibrage ni une intégration à une partie complète.
- **IMPLEMENTATION GAP :** préparation complète du profil Race à partir d'un état Training réel, notamment la construction de la table physiologique et de `S0`, ainsi que le calcul automatique du palier d'affûtage.
- **EXPERIMENTAL CALIBRATION :** paramètres de déplacement de courbe, distributions de forme, terrain et capital de relance. Les règles de calcul sont décidées ; leur équilibre n'est pas démontré.

### 7.1 Profil physiologique et allure spécifique

Le profil possède trois repères permanents EF, Seuil et VMA. Chacun a une coordonnée d'énergie et une coordonnée de vitesse, avec un ordre strictement croissant sur les deux axes : `EF < Seuil < VMA`.

La courbe de conversion est une table explicite de couples entiers `(énergie, vitesse)`, indexée par chaque niveau entier d'énergie. La Race effectue une lecture directe : aucune interpolation ni extrapolation n'est autorisée. EF est le plancher de vitesse et VMA le plafond d'énergie et de vitesse. Une VMA élevée est un plafond, pas une vitesse garantie.

L'AS est propre à la course préparée et connue dès le début du Training. AS42/AS21 se situent entre EF et Seuil ; AS10 près du Seuil, éventuellement légèrement au-dessus ; AS5 peut approcher VMA. VMA est le seul plafond de progression de l'AS5. L'AS n'est pas un quatrième repère permanent.

### 7.2 Dépense, terrain et conversion

À chaque secteur, le joueur lance tout son pool, effectue ses relances éventuelles, puis choisit librement les dés dépensés. La sélection vide est légale. Si aucun dé n'est dépensé, le secteur ne produit ni vitesse ni point : ni EF, ni terrain, ni aspiration ne créent une dépense ou une vitesse gratuite.

La somme des dés sélectionnés est la dépense réelle, écrêtée à VMA. La conversion utilise ensuite :

`E_conversion = E_dépensée + B_groupe − D_terrain`

- `B_groupe` vaut 0 ou +1 et représente une énergie virtuelle d'aspiration.
- `D_terrain` est un entier signé : positif en montée, nul sur le plat, négatif en descente.
- terrain et aspiration modifient uniquement la conversion, jamais la dépense réelle ni la consommation de soutenabilité.
- après application de ces modificateurs, l'énergie de conversion est plafonnée à VMA ; la vitesse est plafonnée à la vitesse VMA.

Pour toute dépense positive, le plancher EF s'applique même si la courbe dégradée ne permet plus de l'atteindre avec l'énergie disponible. Il ne s'applique jamais à une sélection vide.

### 7.3 Soutenabilité

La soutenabilité de départ est un crédit `S0` préparé par le Training. `F` est la somme des valeurs des cartes de forme révélées et `C` la consommation cumulée des secteurs résolus.

`X = S0 + F − C`

`D = max(0, C − (S0 + F))`

`R = max(0, (S0 + F) − C)`

La soutenabilité n'a pas de plancher à zéro. La dégradation `D` est recalculée à partir des cumuls ; elle peut donc diminuer si une carte positive est révélée. La réserve `R` absorbe les consommations avant dégradation. Une carte révélée au début d'un secteur agit immédiatement sur ce secteur. La consommation du secteur est calculée à sa fin et ne modifie que les secteurs suivants.

La consommation dépend de la dépense réelle avant terrain et aspiration :
- dépense inférieure à AS−1 : 0 ;
- dépense comprise entre AS−1 et AS+1 inclus : 1 ;
- dépense supérieure à AS+1 : 2.

La dégradation décale horizontalement la courbe vers la droite sans en changer la forme ni la pente. Le modèle initial d'une graduation par point de dégradation est **EXPERIMENTAL** et doit être calibré. Une carte positive peut restaurer la courbe jusqu'à sa position initiale, jamais au-delà. La réserve restante en fin de course est perdue ; le bilan final n'affecte ni le résultat ni le Training suivant.

### 7.4 Forme du jour

Avant la course, le joueur lance trois dés à six faces dédiés et utilise leur somme pour déterminer un niveau : Difficile (3–5), Moyenne (6–8), Bonne (9–12), Excellente (13–15), Exceptionnelle (16–18). Ce niveau définit une recette de trois cartes issues de quatre paquets catégoriels (Excellent, Bon, Moyen, Mauvais). Les cartes sont mélangées face cachée ; le joueur connaît les catégories mais ni les valeurs ni l'ordre.

Les distributions des paquets sont celles de la spécification Race V2 et restent des paramètres **EXPERIMENTAL**. Les cartes sont révélées au début des secteurs suivants : 5 km : 2/4/6 ; 10 km : 3/6/9 ; semi : 4/8/12 ; marathon : 4/8/12. Les cartes non révélées sont retournées après le dernier secteur à titre informatif seulement.

### 7.5 Groupes et aspiration

Après chaque secteur, les joueurs sont classés par score cumulatif, somme des vitesses entières obtenues. Un nouveau groupe commence lorsque l'écart entre deux scores consécutifs est strictement supérieur à 1. Le regroupement suit donc les écarts entre voisins, pas l'écart au leader.

Dans chaque groupe, le ou les joueurs en tête sont lièvres ; les autres bénéficient de +1 énergie virtuelle au secteur suivant. En cas d'égalité en tête, tous les joueurs concernés sont lièvres. Un joueur seul n'a aucun bonus. Les statuts et le bonus sont connus avant le choix des dés du secteur concerné. Les groupes sont recalculés après chaque secteur ; le bonus ne s'accumule pas et n'affecte pas la soutenabilité.

Au premier secteur, tous les scores sont nuls : tous les joueurs sont co-lièvres et personne ne reçoit d'aspiration.

### 7.6 Dés et capital de relance

Chaque secteur commence par le lancer de l'intégralité du pool. Les dés peuvent être relancés individuellement, un à la fois ; chaque relance remplace le résultat précédent et consomme une unité du capital global. Un même dé peut être relancé plusieurs fois si le capital le permet. Il n'y a pas de relance après la sélection des dés dépensés. Les dés non sélectionnés ne sont pas conservés et seront relancés au secteur suivant. L'action Add n'existe pas en Race.

Le capital de référence sur 5 km dépend du plus haut dé : D6 = 1, D8 = 2, D10 = 3, D12 = 4. Pour une course de `N` secteurs :

`R = ceil(Rmax_5km × (N / 7) × P_affûtage)`

`P_affûtage` vaut 0, 0,25, 0,50, 0,75 ou 1 selon le palier d'affûtage 0 à 4. Le capital est global, sans régénération ; le reliquat est perdu à l'arrivée.

Le palier d'affûtage dépend de la fatigue résiduelle du Training. Les seuils de saturation négative et de surentraînement positive sont fonction du plus haut dé ; les seuils intermédiaires et les valeurs détaillées figurent dans la spécification Race V2. Entre deux seuils, le palier inférieur s'applique. **IMPLEMENTATION GAP :** le prototype reçoit encore directement `affutage_level` ; le calcul automatique à partir de la fatigue Training n'est pas intégré.

### 7.7 Ordre de résolution d'un secteur

1. Révéler les cartes prévues et actualiser `F`, `D` et `R`.
2. Afficher le statut de groupe et le bonus, déterminés après le secteur précédent.
3. Lancer tous les dés ; effectuer les relances individuelles.
4. Choisir librement le sous-ensemble dépensé, éventuellement vide.
5. Écrêter la dépense réelle à VMA. Si elle est nulle, produire zéro vitesse ; sinon calculer l'énergie de conversion avec terrain et aspiration, puis appliquer le plafond VMA.
6. Lire la vitesse entière dans la table physiologique, avec dégradation de courbe, plancher EF et plafond VMA.
7. Ajouter la vitesse au score cumulatif.
8. Calculer la consommation de soutenabilité à partir de la dépense réelle et de l'AS ; l'effet est reporté au secteur suivant.
9. Recalculer les groupes pour le secteur suivant.

Après le dernier secteur, la consommation est tout de même enregistrée et les cartes restantes sont révélées pour information. Ni la réserve finale ni la dégradation finale ne modifient le résultat ou le Training suivant.

### 7.8 Statut de l'implémentation et limites

Le prototype `experiments/current/race_v2_prototype/` comprend le résolveur de secteur, l'orchestration multi-secteur, la forme du jour, les cartes, les groupes, les dés, les relances et la validation des décisions en deux phases. Il reste un prototype expérimental isolé.

Le profil physiologique est fourni explicitement sous forme de table entière. `specific_pace`, `initial_credit`, le pool de dés et le palier d'affûtage sont également fournis dans la configuration. Il n'existe pas encore de conversion complète d'un état Training B vers cette configuration. En particulier, le calcul de `S0`, la production de la table physiologique à partir du profil Training et le calcul du palier d'affûtage restent des frontières d'intégration ouvertes.

La formule d'une graduation de dégradation par point, les distributions de forme, les paramètres de terrain, le capital de relance et leur impact sur la durée/les décisions doivent être testés. Aucune campagne de simulation ne constitue à elle seule une validation du design humain.

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
