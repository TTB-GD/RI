# Race V2 — document de conception

**Version :** V2 — précisions sur la conversion, la soutenabilité et les plafonds (12 novembre 2026)  
**Statut :** décisions de conception retenues ; calibrations expérimentales  
**Périmètre :** profil physiologique, dépense, soutenabilité, forme du jour, groupes, dés et relances.

> Ce document consolide les décisions de conception prises dans la discussion. Il ne décrit pas l'état actuel de l'implémentation. Les règles marquées comme retenues sont des arbitrages de design ; les valeurs signalées comme expérimentales restent à tester.

## 1. Philosophie générale

La course exploite le potentiel construit pendant le Training.

Le Training prépare :
- le profil physiologique du joueur ;
- ses capacités EF, Seuil et VMA ;
- sa soutenabilité ;
- son pool de dés ;
- son état de fatigue et d'affûtage.

La Race met ces éléments à l'épreuve :
- choix de l'énergie mobilisée ;
- gestion de la soutenabilité ;
- adaptation à la forme du jour ;
- exploitation de l'aspiration ;
- gestion des relances de dés.

L'objectif n'est pas de simuler fidèlement la physiologie réelle, mais de produire des décisions tactiques intéressantes : tenir une allure, forcer, ralentir, profiter d'un groupe ou tenter de revenir sur les concurrents.

Les règles fondamentales doivent rester communes aux courses de 5 km, 10 km, semi-marathon et marathon.

## 2. Profil physiologique et allure spécifique

### 2.1. Courbe physiologique

Le profil physiologique comporte trois points de référence permanents :
- EF ;
- Seuil ;
- VMA.

Chaque point possède deux coordonnées : une énergie et une vitesse.

Les deux axes doivent respecter le même ordre :

**EF < Seuil < VMA**

La courbe représente la conversion de l'énergie mobilisée en vitesse. Elle est définie uniquement par des couples de valeurs entières `(énergie, vitesse)` : chaque niveau entier d'énergie possède une vitesse entière correspondante. La conversion se fait par lecture directe de la courbe, sans interpolation ni arrondi.

EF est le plancher de vitesse et VMA le plafond de vitesse. La courbe n'est pas prolongée au-delà de ces bornes. La dégradation de la soutenabilité entraîne un déplacement horizontal de la courbe vers la droite ; elle ne modifie ni sa forme ni sa pente.

### 2.2. Allure spécifique (AS)

L'AS est un point supplémentaire associé à la course préparée. Elle est connue dès le début du Training : les joueurs préparent leur physiologie en fonction du scénario de course.

Positionnement indicatif retenu :
- AS42 et AS21 : entre EF et Seuil ;
- AS10 : proche du Seuil, éventuellement légèrement au-dessus ;
- AS5 : peut approcher VMA.

VMA constitue le seul plafond de progression de l'AS5.

Lorsque l'AS atteint son plafond physiologique, sa progression propre sature. Il faut alors développer le point physiologique supérieur pour recréer de la marge.

L'AS n'est donc pas un quatrième point permanent de la courbe de base.

## 3. Dépense d'énergie et conversion en vitesse

### 3.1. Choix de l'énergie

À chaque secteur, le joueur lance l'intégralité de son pool, effectue ses éventuelles relances, puis choisit librement le sous-ensemble de dés qu'il souhaite dépenser. Il peut choisir de ne dépenser aucun dé ; dans ce cas, le secteur ne produit aucun point.

La somme des dés sélectionnés peut dépasser VMA : l'énergie réellement dépensée est alors écrêtée à VMA. VMA constitue le plafond de dépense physiologique. Les dés non sélectionnés ne sont pas conservés : l'intégralité du pool est relancée au secteur suivant.

### 3.2. Conversion

La conversion énergie → vitesse utilise une énergie de conversion calculée après application du bonus de groupe et de la difficulté du terrain :

`E_conversion = E_dépensée + B_groupe − D_terrain`

Avec :
- `E_dépensée` : énergie réellement dépensée, plafonnée à VMA ;
- `B_groupe` : bonus virtuel d'aspiration (0 ou +1) ;
- `D_terrain` : difficulté entière signée du secteur (positive en montée, nulle sur le plat, négative en descente).

Le terrain modifie la conversion, jamais la dépense réelle. Il ne se substitue pas à l'énergie : sans énergie dépensée, aucune conversion n'est effectuée, le secteur ne produit aucune vitesse et le terrain ne crée pas d'énergie. Le plancher EF ne s'applique qu'à une conversion effectivement engagée avec une dépense positive.

Après application du groupe et du terrain, l'énergie de conversion est plafonnée à VMA. Les bonus ne permettent donc pas de dépasser le plafond énergétique de VMA. La vitesse produite est elle aussi plafonnée à la vitesse du point VMA.

Les bonus de groupe et les corrections de terrain n'ont aucun effet sur la consommation de soutenabilité.

### 3.3. Consommation de soutenabilité

La consommation est calculée à partir de l'énergie réellement dépensée, avant application du bonus de groupe et des corrections de terrain.

Elle dépend de l'écart entre la dépense et l'AS :

| Dépense réelle par rapport à AS | Consommation de soutenabilité |
|---|---:|
| Inférieure à AS − 1 | 0 |
| De AS − 1 à AS + 1 inclus | 1 |
| Supérieure à AS + 1 | 2 |

La consommation est calculée indépendamment pour chaque secteur. Il n'y a pas de report de dépassement d'un secteur vers le suivant.

Le bonus d'aspiration et les corrections de terrain n'entraînent aucune consommation supplémentaire.

## 4. Soutenabilité et dégradation de la courbe

### 4.1. Principe

La soutenabilité est construite pendant le Training. Elle représente la capacité du joueur à maintenir son effort sans dégradation de son profil de conversion.

On distingue :
- la soutenabilité initiale, préparée pendant le Training (`S0`) ;
- les effets cumulés des cartes de forme déjà révélées (`F`) ;
- la consommation cumulée des secteurs déjà résolus (`C`).

La soutenabilité peut devenir négative. Il n'existe pas de plancher à zéro. La dégradation est recalculée à chaque fin de secteur à partir des cumuls `F` et `C` ; elle n'est pas une perte irréversible appliquée séparément à chaque tour.

### 4.2. Bilan de soutenabilité

Le bilan net est :

`X = F − C`

La dégradation courante et la réserve sont :

- `D = max(0, C − F)` ;
- `R = max(0, F − C)`.

La variation par rapport à l'état initial est donc `Δ = C − F`. Une carte positive révélée peut réduire une dégradation déjà présente et restaurer la courbe, sans jamais la déplacer à gauche de sa position initiale.

Le principe retenu est qu'une perte de soutenabilité déplace horizontalement la courbe vers la droite : il faut davantage d'énergie de conversion pour produire une même vitesse. Le modèle de départ est d'une graduation entière par point de soutenabilité perdu. Le rapport exact et l'éventuelle utilisation de paliers pour adoucir la pénalité restent à tester.

### 4.3. Déplacement de la courbe

- Le déplacement horizontal ne modifie pas la forme ni la pente de la courbe.
- Les points physiologiques de référence EF, Seuil et VMA restent fixes ; c'est la conversion énergie → vitesse qui est pénalisée.
- Le modèle initial est un déplacement d'une graduation entière par point de dégradation ; des paliers moins sensibles pourront être évalués par test.
- La courbe ne peut jamais être déplacée vers la gauche au-delà de sa position initiale.
- Une carte positive peut compenser une consommation antérieure et restaurer une courbe déjà dégradée, mais ne peut pas améliorer la physiologie préparée au Training ni déplacer la courbe à gauche de sa position initiale.
- Après dégradation, si l'énergie de conversion ne permet plus d'atteindre EF sur la courbe déplacée, la vitesse est ramenée au plancher EF. Cette règle n'ajoute aucune pénalité énergétique.

### 4.4. Réserve de soutenabilité

Les effets positifs des cartes peuvent compenser les consommations antérieures. Si leur cumul dépasse les consommations et ramène la courbe à sa position initiale, l'excédent positif est placé en réserve.

La réserve est consommée automatiquement lors des dépenses ultérieures, avant que la courbe ne soit dégradée. Une carte positive révélée en cours de course agit immédiatement : elle peut donc restaurer la courbe pour le secteur où elle est révélée.

Le fonctionnement peut être représenté ainsi :

- Dégradation de courbe : `max(0, C − F)`
- Réserve : `max(0, F − C)`

Ainsi :
- une réserve protège contre les consommations futures ;
- une consommation absorbe d'abord la réserve ;
- une fois la réserve épuisée, la courbe se déplace vers la droite ;
- aucun excédent positif ne permet de dépasser la position physiologique initiale.

À la fin de la course, la réserve restante est perdue. Elle n'a aucun effet sur le Training suivant. Elle indique simplement qu'une marge de soutenabilité existait encore pendant la course.

## 5. Forme du jour

### 5.1. Principe

La forme du jour est une variabilité externe à la progression physiologique.

Elle est déterminée par trois dés à six faces dédiés, indépendants du pool d'entraînement.

Le joueur lance les 3d6 une fois avant la course. Il utilise uniquement la somme des dés. La distribution en cloche est considérée suffisante pour la conception actuelle.

### 5.2. Table de forme du jour

| Somme des 3d6 | Niveau de forme | Probabilité exacte |
|---:|---|---:|
| 3–5 | Difficile | 4,63 % |
| 6–8 | Moyenne | 21,30 % |
| 9–12 | Bonne | 48,15 % |
| 13–15 | Excellente | 21,30 % |
| 16–18 | Exceptionnelle | 4,63 % |

Les probabilités sont calculées sur les 216 combinaisons possibles de trois dés à six faces.

### 5.3. Recette des cartes

Le niveau de forme détermine la composition de trois cartes :

| Forme | Composition |
|---|---|
| Exceptionnelle | Excellent, Excellent, Bon |
| Excellente | Excellent, Bon, Bon |
| Bonne | Bon, Bon, Moyen |
| Moyenne | Bon, Moyen, Mauvais |
| Difficile | Moyen, Mauvais, Mauvais |

Le joueur tire les trois cartes correspondant à cette recette. Il connaît leur catégorie, mais pas leur valeur.

### 5.4. Composition des paquets

Chaque catégorie comporte 15 cartes.

| Catégorie | +2 | +1 | 0 | −1 | −2 |
|---|---:|---:|---:|---:|---:|
| Excellent | 3 | 8 | 4 | 0 | 0 |
| Bon | 2 | 5 | 6 | 2 | 0 |
| Moyen | 0 | 2 | 8 | 5 | 0 |
| Mauvais | 0 | 0 | 3 | 7 | 5 |

La valeur de la carte modifie directement le bilan de soutenabilité.

Espérance de chaque catégorie :
- Excellent : +0,933 ;
- Bon : +0,467 ;
- Moyen : −0,200 ;
- Mauvais : −1,133.

Ces distributions et leurs effets restent des paramètres expérimentaux à tester.

### 5.5. Ordre et information disponible

Les trois cartes sont mélangées face cachée. Leur catégorie reste identifiable (par exemple au dos de la carte), mais leur valeur et leur ordre de révélation sont inconnus.

Le joueur :
- connaît la composition de sa recette ;
- ne connaît pas les valeurs des cartes ;
- ne connaît pas leur ordre de révélation.

L'incertitude porte donc sur la valeur exacte et le moment où chaque effet interviendra.

### 5.6. Calendrier de révélation

Les cartes sont révélées progressivement, au début du secteur indiqué, avant le choix de l'énergie.

| Course | Nombre de secteurs | Révélations |
|---|---:|---|
| 5 km | 7 | 2, 4, 6 |
| 10 km | 10 | 3, 6, 9 |
| Semi-marathon | 13 | 4, 8, 12 |
| Marathon | 16 | 4, 8, 12 |

Une carte révélée au début d'un secteur applique immédiatement son effet à la soutenabilité et peut restaurer la courbe pour ce même secteur. Son effet reste permanent jusqu'à la fin de la course. Toute carte qui resterait non révélée à la fin de la course est retournée après la résolution du dernier secteur, à titre informatif uniquement : elle ne modifie ni la course terminée ni son résultat.

## 6. Effet de groupe et aspiration

### 6.1. Constitution des groupes

À la fin de chaque secteur, les joueurs sont classés selon leur score cumulatif de course, par ordre décroissant. Le score est simplement la somme des vitesses entières obtenues dans les secteurs déjà parcourus.

Les joueurs sont regroupés selon les écarts successifs entre scores consécutifs. Un nouveau groupe est créé lorsque l'écart entre deux joueurs consécutifs est strictement supérieur à 1. Les écarts sont évalués entre voisins dans le classement, et non par rapport au premier joueur du groupe.

Exemples :

| Scores classés | Groupes |
|---|---|
| 45, 44, 44, 43 | Groupe 1 |
| 40, 39 | Groupe 2 |
| 35 | Groupe 3 |
| 10, 9, 8 | Groupe 1 (un seul groupe) |
| 10, 10, 9, 8 | Groupe 1 ; les deux joueurs à 10 sont lièvres |
| 10, 9, 7 | Groupe 1 : 10 et 9 ; Groupe 2 : 7 |
| 10, 8, 7 | Groupe 1 : 10 ; Groupe 2 : 8 et 7 |

Dans le cas `10, 9, 8`, chaque écart adjacent vaut exactement 1 : les trois joueurs restent donc dans le même groupe. Le joueur à 10 est le lièvre ; les joueurs à 9 et 8 bénéficient de l'aspiration.

### 6.2. Lièvres et bénéficiaires

Le score de course est simplement la somme des vitesses entières obtenues dans les secteurs déjà parcourus. Il sert à classer les joueurs et à constituer les groupes ; aucun indicateur de score distinct n'est utilisé.

Dans chaque groupe :
- le ou les joueurs ayant le score cumulatif le plus élevé sont les lièvres ;
- tous les autres joueurs, dont le score est inférieur, bénéficient de l'aspiration ;
- en cas d'égalité en tête, tous les joueurs concernés sont lièvres.

Un joueur seul ne bénéficie d'aucun bonus.

### 6.3. Bonus d'aspiration

Chaque bénéficiaire reçoit +1 énergie virtuelle pour le secteur en cours. Le statut de chaque joueur (lièvre ou bénéficiaire de l'aspiration) et la présence ou non du bonus sont connus avant son choix de dés. Ce bonus est déterminé à partir des groupes issus du classement cumulatif du secteur précédent ; il est donc déjà établi au début du secteur où il s'applique.

Cette énergie :
- est ajoutée après le choix des dés ;
- est utilisée uniquement pour la conversion énergie → vitesse ;
- ne constitue pas une dépense réelle ;
- ne consomme aucune soutenabilité ;
- ne modifie aucun autre élément du score ou de la course.

L'énergie de conversion reste plafonnée à VMA après application du bonus. Le bonus ne permet donc de dépasser ni le plafond énergétique de VMA ni la vitesse maximale associée à VMA.

### 6.4. Renouvellement

Les groupes sont recalculés à la fin de chaque secteur, après actualisation des scores cumulatifs. Le statut et le bonus ainsi déterminés sont ceux du secteur suivant :
- le bonus ne s'accumule pas ;
- il peut être gagné ou perdu d'un secteur à l'autre ;
- il est connu avant le choix des dés du secteur où il s'applique.

Avant le premier secteur, tous les joueurs ont un score cumulatif initial de 0. Ils forment donc un seul groupe et sont tous co-lièvres ; aucun joueur ne reçoit d'aspiration au premier secteur.

Cette mécanique doit permettre :
- de mener un groupe ;
- de rester dans un groupe pour bénéficier de l'aspiration ;
- de tenter de revenir sur un groupe ;
- de provoquer une échappée ;
- de ralentir volontairement pour masquer ses intentions.

## 7. Dés et relances pendant la Race

### 7.1. Lancer et choix des dés

Le joueur lance l'intégralité de son pool pour le secteur. Après les éventuelles relances, il choisit librement le sous-ensemble final de dés qu'il dépense, y compris le sous-ensemble vide. S'il ne dépense aucun dé, il ne marque aucun point pour ce secteur. Les dés non dépensés sont relancés avec le reste du pool au secteur suivant.

### 7.2. Relances

- Le joueur peut relancer des dés individuellement.
- Chaque relance remplace définitivement le résultat précédent du dé concerné pour le tour en cours.
- Les relances se font une par une.
- Le joueur choisit ensuite librement le sous-ensemble final de dés à dépenser.
- Il n'y a aucune relance après le choix du sous-ensemble.
- L'action Add est supprimée en Race : le choix libre du sous-ensemble permet déjà d'ajuster la dépense.

### 7.3. Capital de relance

Les relances constituent un capital global pour toute la course.

Chaque dé relancé consomme une unité de ce capital :
- pas de régénération entre les secteurs ;
- les relances non utilisées sont perdues à l'arrivée.

Le capital maximal de référence sur 5 km dépend du plus haut dé du pool :

| Plus haut dé | Capital maximal 5 km |
|---|---:|
| D6 | 1 |
| D8 | 2 |
| D10 | 3 |
| D12 | 4 |

Le capital est ensuite proportionnel au nombre de secteurs de la course.

| Course | Secteurs | Facteur |
|---|---:|---:|
| 5 km | 7 | 7/7 |
| 10 km | 10 | 10/7 |
| Semi-marathon | 13 | 13/7 |
| Marathon | 16 | 16/7 |

### 7.4. Affûtage et fatigue

Le niveau d'affûtage dépend de la fatigue résiduelle à la fin du Training.

La zone de surentraînement commence lorsque la fatigue atteint la valeur du plus haut dé. À l'opposé, la saturation de l'affûtage est atteinte à la valeur négative du plus haut dé.

Les seuils validés sont :

| Plus haut dé | 0 % | 25 % | 50 % | 75 % | 100 % |
|---|---:|---:|---:|---:|---:|
| D6 | 0 | −2 | −3 | −4 | −6 |
| D8 | 0 | −2 | −4 | −6 | −8 |
| D10 | 0 | −4 | −6 | −8 | −10 |
| D12 | 0 | −6 | −8 | −10 | −12 |

Les seuils intermédiaires débloquent le niveau correspondant. Entre deux seuils, le niveau inférieur s'applique.

### 7.5. Calcul du capital effectif

Le capital de relance est calculé ainsi :

`R = ceil(Rmax_5km × (N / 7) × P_affûtage)`

Avec :
- `Rmax_5km` : capital maximal associé au plus haut dé ;
- `N` : nombre de secteurs de la course ;
- `P_affûtage` : coefficient de 0, 0,25, 0,50, 0,75 ou 1 ;
- `ceil` : arrondi à l'entier supérieur, appliqué après le calcul complet.

## 8. Déroulement synthétique d'un secteur

Pour chaque secteur :

1. Révéler, le cas échéant, la carte de forme prévue au début de ce secteur.
2. Ajouter immédiatement sa valeur aux effets cumulés `F` et actualiser la dégradation/réserve. Cette éventuelle restauration de la courbe est applicable dès ce secteur.
3. Afficher le statut de groupe du joueur et son éventuel bonus d'aspiration, déterminés à la fin du secteur précédent. Le profil de terrain du secteur est connu depuis le début de la course.
4. Lancer l'intégralité du pool de dés.
5. Effectuer les éventuelles relances individuelles disponibles.
6. Choisir librement les dés à dépenser, éventuellement aucun.
7. Calculer l'énergie réellement dépensée : somme des dés sélectionnés, écrêtée à VMA.
8. Si l'énergie réellement dépensée est nulle, ne produire aucune vitesse. Sinon, calculer l'énergie de conversion (`E_dépensée + B_groupe − D_terrain`), puis la plafonner à VMA.
9. Appliquer à cette conversion la courbe de soutenabilité en vigueur au début du secteur, lire la vitesse entière correspondante et respecter le plancher EF et le plafond de vitesse VMA.
10. Ajouter la vitesse entière obtenue au score cumulatif.
11. En fin de secteur, calculer la consommation de soutenabilité à partir de l'énergie réellement dépensée et de l'AS, sans tenir compte du bonus de groupe ni du terrain.
12. Mettre à jour la consommation cumulée `C`, puis recalculer `D = max(0, C − F)` et `R = max(0, F − C)`. Cette nouvelle dégradation ou réserve sert de base au secteur suivant ; la consommation de ce secteur ne dégrade donc pas rétroactivement sa propre conversion.
13. Recalculer les groupes à partir des scores cumulatifs actualisés. Les statuts et bonus ainsi obtenus s'appliquent au secteur suivant.

Après la résolution du dernier secteur, retourner à titre informatif toute carte qui serait encore face cachée. La consommation du dernier secteur est bien comptabilisée, même si elle ne peut plus affecter une conversion ultérieure.

## 9. Décisions consolidées et statut

| Élément | Décision | Statut |
|---|---|---|
| Profil physiologique | EF, Seuil, VMA sur deux axes | Retenu |
| Courbe de conversion | Couples énergie/vitesse entiers, lecture directe sans interpolation | Retenu |
| Plancher de vitesse | EF, même après dégradation | Retenu |
| Plafond énergétique | VMA après bonus de groupe et terrain | Retenu |
| Plafond de vitesse | Vitesse associée au point VMA | Retenu |
| Terrain | Difficulté entière signée, appliquée à la conversion uniquement | Retenu |
| Énergie nulle | Aucune conversion ni point ; le terrain et l'aspiration ne créent pas d'énergie | Retenu |
| Choix des dés | Sous-ensemble libre, y compris aucun dé | Retenu |
| Dépense supérieure à VMA | Écrêtage de l'énergie réellement dépensée à VMA | Retenu |
| Dés non dépensés | Relancés au secteur suivant avec le pool complet | Retenu |
| Score de course | Somme des vitesses entières des secteurs | Retenu |
| AS | Point propre à la course préparée | Retenu |
| Plafond de dépense | VMA | Retenu |
| Consommation de soutenabilité | Trois niveaux selon l'écart à AS | Retenu |
| Dégradation de courbe | Décalage horizontal entier vers la droite | Retenu |
| Plancher de soutenabilité | Aucun | Retenu |
| Réserve positive | Compense les consommations futures et peut restaurer une courbe dégradée | Retenu |
| Actualisation de soutenabilité | Consommation calculée en fin de secteur, effet sur le secteur suivant | Retenu |
| Cartes positives | Effet immédiat au début du secteur de révélation | Retenu |
| Bilan final de soutenabilité | Information de conception sans effet sur le résultat ni le Training suivant | Retenu |
| Cartes non révélées | Retournées après la course à titre informatif | Retenu |
| Fin de course | Réserve restante perdue | Retenu |
| Forme du jour | 3d6 dédiés | Retenu |
| Nombre de niveaux de forme | Cinq | Retenu |
| Cartes de forme | Trois cartes selon une recette | Retenu |
| Valeur des cartes | Cachée | Retenu |
| Ordre des cartes | Mélangé face cachée | Retenu |
| Révélation | Progressive, au début des secteurs indiqués | Retenu |
| Effet des cartes | Permanent jusqu'à l'arrivée | Retenu |
| Constitution des groupes | Écart successif strictement supérieur à 1 | Retenu |
| Actualisation des groupes | Fin de chaque secteur, à partir des scores cumulés actualisés | Retenu |
| Information de groupe | Statut exact et bonus connus avant le choix des dés | Retenu |
| Lièvres | Joueur(s) en tête du groupe | Retenu |
| Aspiration | +1 énergie virtuelle | Retenu |
| Effet de l'aspiration | Conversion uniquement, bonus applicable au secteur en cours | Retenu |
| Relances | Capital global consommé dé par dé | Retenu |
| Calcul du capital | Proportionnel au nombre de secteurs, arrondi supérieur | Retenu |
| Affûtage | Seuils selon le plus haut dé | Retenu |

## 10. Points restant à calibrer ou à préciser

Ces points ne remettent pas en cause les décisions déjà retenues. Ils nécessitent des tests ou une formalisation ultérieure.

1. **Soutenabilité initiale :** préciser complètement sa construction pendant le Training, notamment la contribution des adaptations EF et des qualités spécifiques.
2. **Courbe physiologique :** déterminer les valeurs numériques et le support de jeu permettant son déplacement horizontal.
3. **Terrain :** calibrer les corrections de conversion selon les secteurs.
4. **Forme du jour :** tester l'équilibre entre les cinq niveaux, les recettes et les distributions des paquets.
5. **Aspiration :** vérifier que le bonus récurrent de +1 produit un effet tactique intéressant sans devenir dominant.
6. **Décalage de soutenabilité :** tester le modèle d'une graduation par point et des variantes par paliers pour calibrer la sévérité de la pénalité.
7. **Capital de relance :** tester les effets de l'arrondi supérieur, notamment sur les petites courses et les faibles niveaux d'affûtage.
8. **Conversion entière :** définir et tester la table de couples énergie/vitesse entiers pour chaque profil physiologique.
9. **Durée et fluidité :** vérifier que le nombre de secteurs et les décisions par secteur restent compatibles avec la durée de jeu visée.


## 11. Relation avec les documents et modèles antérieurs

Ce document consolide le modèle de soutenabilité et les règles de course arbitrés le 12 novembre 2026.

Il remplace, comme référence de conception pour la soutenabilité en Race, l'ancienne formule de réserve énergétique de `RACE_RESERVE_DESIGN.md` (PR #59), qui reposait sur les investissements EF / Seuil / VMA et une réserve de préparation calculée avant la course.

Les compteurs d'énergie investie pendant le Training restent des données distinctes et peuvent conserver une utilité pour d'autres analyses. Cette consolidation ne modifie ni le code ni les tests existants.

---

**Principe de conception à préserver :** la Race doit mettre en tension le potentiel préparé pendant le Training, la dépense réellement consentie, la soutenabilité restante et les opportunités tactiques. Les mécanismes de forme du jour et d'aspiration doivent enrichir ces arbitrages sans remplacer le cœur de la conversion physiologique.
