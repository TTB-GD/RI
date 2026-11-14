# Profils de référence — vitesses physiologiques et allures spécifiques

**Statut :** références de calibrage proposées ; les profils P8–P15 en unités internes doublées sont la nouvelle base de travail, en remplacement de leur ancienne représentation entière en km/h.  
**Date :** 12 novembre 2026  
**Référentiel :** Jack Daniels, *Daniels' Running Formula*, 4e édition ; équivalences de performance VDOT et tables d'intensité.

## 1. Objet

Ce document conserve cinq profils de référence permettant de donner des ordres de grandeur crédibles :
- aux vitesses physiologiques EF, Seuil et VMA ;
- aux allures spécifiques de course AS42, AS21, AS10 et AS5.

Ces profils servent de points d'ancrage pour le travail de conception et les simulations. Ils ne constituent ni des profils de joueurs obligatoires, ni une formule de progression, ni une validation définitive des bornes du système.

## 2. Méthode de construction

Les profils sont espacés de dix points de VDOT : 30, 40, 50, 60 et 70.

### 2.1. Points physiologiques EF, Seuil et VMA

Le référentiel Daniels fournit :
- une plage d'allure E (Easy) ;
- une allure T (Threshold) ;
- une allure I (Interval), prescrite pour des répétitions de 3 à 5 minutes.

Pour obtenir un point EF unique, la valeur retenue est le milieu arithmétique de la plage E, exprimée en secondes par kilomètre. Ce choix est une convention de modélisation : l'EF réelle est une plage, et le milieu ne prétend pas représenter une intensité physiologique universelle.

Le Seuil reprend l'allure T. La vitesse I est utilisée comme approximation opérationnelle de la VMA. Cette équivalence est indicative : l'allure I de Daniels et la VMA mesurée en laboratoire ou sur le terrain ne sont pas strictement identiques.

### 2.2. Allures spécifiques AS42, AS21, AS10 et AS5

Les allures spécifiques sont dérivées des performances équivalentes prédites par le modèle VDOT de Daniels pour un même niveau de performance :
- AS42 : allure marathon ;
- AS21 : allure semi-marathon ;
- AS10 : allure 10 km ;
- AS5 : allure 5 km.

Il s'agit d'équivalences théoriques entre distances, pas d'une garantie de performance. Elles supposent notamment une endurance suffisante pour exprimer le potentiel sur marathon. En pratique, un coureur peut présenter un profil moins homogène entre distances, notamment si son endurance spécifique est moins développée.

Conversion d'une allure en vitesse :

`v (km/h) = distance (km) / durée (h)`

Les vitesses physiques sont arrondies au dixième de km/h pour la lisibilité. Les temps de course sources sont conservés ci-dessous afin de permettre de retrouver les conversions. Pour les profils de jeu, une convention distincte est adoptée en section 3.5 : l'unité interne de vitesse vaut 0,5 km/h.

## 3. Profils proposés

| Profil indicatif | VDOT | EF (km/h) | Seuil (km/h) | VMA approx. (km/h) |
|---|---:|---:|---:|---:|
| Débutant / faible niveau de performance | 30 | 7,6 | 9,4 | 10,1 |
| Récréatif régulier | 40 | 9,5 | 11,8 | 12,9 |
| Entraîné | 50 | 11,4 | 14,1 | 15,3 |
| Confirmé | 60 | 13,2 | 16,4 | 17,7 |
| Très performant | 70 | 15,0 | 18,6 | 20,1 |

### 3.1. Allures sources des points physiologiques

| VDOT | Plage E Daniels (min/km) | Point EF retenu (min/km) | T (min/km) | I (min/km) |
|---:|---:|---:|---:|---:|
| 30 | 7:27–8:14 | 7:50,5 | 6:24 | 5:55 |
| 40 | 5:56–6:38 | 6:17 | 5:06 | 4:40 |
| 50 | 4:56–5:34 | 5:15 | 4:15 | 3:55 |
| 60 | 4:15–4:49 | 4:32 | 3:40 | 3:23 |
| 70 | 3:44–4:15 | 3:59,5 | 3:14 | 2:59 |

### 3.2. Allures spécifiques de course proposées

| Profil | VDOT | AS42 (km/h) | AS21 (km/h) | AS10 (km/h) | AS5 (km/h) |
|---|---:|---:|---:|---:|---:|
| Débutant / faible niveau de performance | 30 | 8,7 | 9,0 | 9,4 | 9,8 |
| Récréatif régulier | 40 | 11,0 | 11,4 | 12,0 | 12,4 |
| Entraîné | 50 | 13,3 | 13,8 | 14,5 | 15,1 |
| Confirmé | 60 | 15,5 | 16,1 | 17,0 | 17,6 |
| Très performant | 70 | 17,5 | 18,5 | 19,4 | 20,1 |

### 3.3. Performances équivalentes utilisées pour les AS

| VDOT | 5 km | 10 km | Semi-marathon | Marathon |
|---:|---:|---:|---:|---:|
| 30 | 30:41 | 1:03:49 | 2:21:17 | 4:49:49 |
| 40 | 24:06 | 50:01 | 1:50:54 | 3:49:37 |
| 50 | 19:56 | 41:20 | 1:31:31 | 3:10:40 |
| 60 | 17:03 | 35:22 | 1:18:09 | 2:43:22 |
| 70 | 14:56 | 31:01 | 1:08:23 | 2:23:13 |


## 3.4. Profils de départ proposés pour le jeu

Pour disposer d'une gamme de départ simple et directement exploitable, huit profils sont proposés avec une EF entière de 8 à 15 km/h, par pas de 1 km/h.

Les valeurs sont construites à partir des cinq profils VDOT de référence :
1. interpolation linéaire, colonne par colonne, entre les points VDOT encadrant la valeur EF recherchée ;
2. arrondi aux km/h entiers ;
3. choix de l'arrondi qui minimise l'écart global aux valeurs interpolées, sous contraintes physiologiques.

Les contraintes conservées sont :
- ordre strict des trois points physiologiques : `EF < Seuil < VMA` ;
- les allures spécifiques restent non décroissantes : `AS42 ≤ AS21 ≤ AS10 ≤ AS5` ;
- AS42 et AS21 restent entre EF et Seuil ; AS10 est proche du Seuil ; AS5 approche VMA.

Avec une granularité entière, plusieurs AS peuvent donc avoir la même valeur. C'est préférable à forcer artificiellement un écart d'au moins 1 km/h entre chaque allure, ce qui déformerait fortement les performances équivalentes, surtout pour les profils bas. Les valeurs restent des paramètres de départ de jeu, non des mesures physiologiques individuelles.

| Profil de départ | EF | AS42 | AS21 | Seuil | AS10 | AS5 | VMA |
|---|---:|---:|---:|---:|---:|---:|---:|
| P8 | 8 | 9 | 10 | 10 | 10 | 10 | 11 |
| P9 | 9 | 10 | 11 | 11 | 11 | 12 | 12 |
| P10 | 10 | 12 | 12 | 12 | 13 | 13 | 14 |
| P11 | 11 | 13 | 13 | 14 | 14 | 15 | 15 |
| P12 | 12 | 14 | 15 | 15 | 15 | 16 | 16 |
| P13 | 13 | 15 | 16 | 16 | 17 | 17 | 17 |
| P14 | 14 | 16 | 17 | 17 | 18 | 19 | 19 |
| P15 | 15 | 17 | 18 | 19 | 19 | 20 | 20 |

Toutes les valeurs sont en km/h. Les profils P8 à P15 constituent la proposition de gamme de départ pour le jeu. Ils ne remplacent pas les références VDOT décimales des sections précédentes, qui restent conservées comme base de calcul et de traçabilité.


### 3.5. Nouvelle échelle interne de vitesse — convention retenue

**Statut : décision de conception retenue le 14 novembre 2026.** La vitesse n'est plus représentée dans les calculs du jeu par une valeur en km/h. Toutes les coordonnées de vitesse physiologique et les vitesses utilisées par Race sont exprimées dans une unité interne entière valant **0,5 km/h**.

La conversion de référence est :

- vitesse physique (km/h) = valeur interne / 2 ;
- valeur interne = vitesse physique × 2, arrondie à l'entier selon la méthode précisée ci-dessous lorsqu'une valeur source n'est pas exactement représentable.

Cette convention est une mise à l'échelle de l'axe vitesse. Elle ne modifie pas, à elle seule, les règles de progression, les coordonnées d'énergie, les dés, les coûts, la fatigue ou la soutenabilité.

#### 3.5.1. Pourquoi une échelle doublée

La granularité précédente de 1 km/h produisait des incréments trop grossiers au regard des écarts physiologiques observés dans les références. Une granularité de 0,5 km/h permet de représenter des évolutions plus progressives.

Deux solutions étaient possibles : conserver des vitesses physiques décimales dans les calculs, ou abandonner l'unité km/h dans le moteur et doubler toutes les coordonnées de vitesse. La seconde est retenue afin de conserver des calculs entiers de bout en bout et d'éviter une conversion avec arrondi entre Training et Race.

**Conséquence structurante :** il n'existe plus de conversion avec perte de précision entre les coordonnées physiologiques et les vitesses Race. Les deux utilisent la même unité interne entière. Les km/h restent une unité de référence documentaire et, si souhaité, d'affichage externe.

#### 3.5.2. Références VDOT converties

Les valeurs physiques de la section 3 sont conservées comme références documentaires. Leur conversion dans l'échelle interne donne :

| VDOT | EF interne | Seuil interne | VMA interne |
|---:|---:|---:|---:|
| 30 | 15,2 | 18,8 | 20,2 |
| 40 | 19,0 | 23,6 | 25,8 |
| 50 | 22,8 | 28,2 | 30,6 |
| 60 | 26,4 | 32,8 | 35,4 |
| 70 | 30,0 | 37,2 | 40,2 |

Les allures spécifiques converties sont :

| VDOT | AS42 interne | AS21 interne | AS10 interne | AS5 interne |
|---:|---:|---:|---:|---:|
| 30 | 17,4 | 18,0 | 18,8 | 19,6 |
| 40 | 22,0 | 22,8 | 24,0 | 24,8 |
| 50 | 26,6 | 27,6 | 29,0 | 30,2 |
| 60 | 31,0 | 32,2 | 34,0 | 35,2 |
| 70 | 35,0 | 37,0 | 38,8 | 40,2 |

Les valeurs des tables sont des entiers ou des décimales de référence. Les valeurs internes de jeu utilisées dans les profils doivent être des entiers. Les références VDOT décimales sont conservées pour la traçabilité et ne sont pas directement des profils de joueur.

#### 3.5.3. Méthode de construction des nouveaux profils P8–P15

Les huit profils conservent les mêmes niveaux de départ EF physiques que la gamme précédente : 8 à 15 km/h par pas de 1 km/h. En unités internes, EF vaut donc respectivement 16, 18, 20, 22, 24, 26, 28 et 30.

Pour chaque profil :

1. La valeur EF cible est exprimée en km/h.
2. Chaque autre colonne (AS42, AS21, Seuil, AS10, AS5, VMA) est interpolée linéairement entre les deux références VDOT qui encadrent cette valeur EF. L'interpolation utilise la colonne EF des cinq références comme abscisse.
3. La valeur interpolée en km/h est convertie dans l'échelle interne en la multipliant par deux.
4. Le résultat est arrondi à l'entier le plus proche ; les éventuelles égalités exactes sont arrondies à l'entier supérieur.
5. EF est conservée exactement à sa valeur cible entière en km/h, soit une valeur interne paire.

Cette méthode produit une granularité physique de 0,5 km/h sans stocker de flottants dans les profils de jeu. Elle remplace, pour les nouveaux profils, l'arrondi précédent au km/h entier.

#### 3.5.4. Nouveaux profils de départ proposés

| Profil | EF | AS42 | AS21 | Seuil | AS10 | AS5 | VMA |
|---|---:|---:|---:|---:|---:|---:|---:|
| P8 | 16 | 18 | 19 | 20 | 20 | 21 | 21 |
| P9 | 18 | 21 | 22 | 22 | 23 | 23 | 24 |
| P10 | 20 | 23 | 24 | 25 | 25 | 26 | 27 |
| P11 | 22 | 26 | 27 | 27 | 28 | 29 | 30 |
| P12 | 24 | 28 | 29 | 30 | 31 | 32 | 32 |
| P13 | 26 | 31 | 32 | 32 | 33 | 35 | 35 |
| P14 | 28 | 33 | 34 | 35 | 36 | 37 | 38 |
| P15 | 30 | 35 | 37 | 37 | 39 | 40 | 40 |

**Toutes les valeurs de ce tableau sont des unités internes entières ; une unité vaut 0,5 km/h.** Pour lecture physique, diviser les valeurs par deux. Exemple P10 : EF 20 = 10 km/h ; AS42 23 = 11,5 km/h ; AS21 24 = 12 km/h ; Seuil 25 = 12,5 km/h ; AS10 25 = 12,5 km/h ; AS5 26 = 13 km/h ; VMA 27 = 13,5 km/h.

Les profils respectent les contraintes de construction :
- ordre strict des points physiologiques : EF < Seuil < VMA ;
- ordre non décroissant des allures spécifiques : AS42 ≤ AS21 ≤ AS10 ≤ AS5 ;
- AS42 et AS21 restent entre EF et Seuil, bornes incluses ;
- AS10 reste proche du Seuil ;
- AS5 reste proche de la VMA.

Les égalités entre certaines allures spécifiques ou avec le Seuil ne sont pas des erreurs : les AS sont des repères de course et non des ancres physiologiques supplémentaires. La granularité de 0,5 km/h autorise ces égalités sans imposer artificiellement des écarts.

#### 3.5.5. Ancienne table P8–P15 : historique

La table de la section 3.4 reste conservée comme trace de l'ancienne proposition à granularité de 1 km/h. Elle est **supplantée** par la table de la section 3.5.4 pour les nouveaux travaux de calibrage. Les cinq références VDOT décimales des sections 3 et 3.2 restent, elles, inchangées.

#### 3.5.6. Conséquences sur Training et Race

- Un incrément de +1 sur une coordonnée de vitesse représente +0,5 km/h.
- Un palier EF qui améliore les trois ancres en vitesse applique le même incrément entier aux trois coordonnées de vitesse.
- Un palier Seuil ou VMA en vitesse modifie uniquement l'ancre concernée, selon les règles de progression déjà retenues.
- Les améliorations sur l'axe énergie ne sont pas multipliées par deux et ne sont pas affectées par cette convention.
- Les dés, leurs faces, les sommes, les seuils de réussite, les budgets d'énergie et les règles de fatigue ne sont pas modifiés par le simple changement d'unité de vitesse.
- La table physiologique énergie → vitesse reste une table entière sans interpolation. Ses valeurs de vitesse sont désormais exprimées dans l'unité interne doublée.
- Race conserve des vitesses entières dans cette même unité. Il n'y a donc pas d'arrondi systématique de demi-km/h vers un km/h entier au passage de Training à Race.
- Une conversion en km/h n'est nécessaire que pour une présentation physique ou une comparaison avec les références sportives.

Cette décision ne fixe pas encore la taille numérique des paliers de progression au-delà de la convention d'unité, ni les seuils d'adaptation, les coûts ou les rendements. Ces paramètres restent à calibrer sur les effets obtenus dans Race.

#### 3.5.7. Points de vigilance et travaux de validation

Le doublement de l'axe vitesse impose un audit des éléments qui manipulent des vitesses ou des différences de vitesse. Il faudra notamment vérifier :
- les plafonds et planchers EF/VMA ;
- les vitesses de course et les allures spécifiques ;
- les variations de vitesse et les écarts entre allures ;
- les comparaisons, seuils et constantes exprimés dans l'ancienne unité ;
- les fixtures, profils de test, exemples, rapports et simulations ;
- les affichages éventuels en km/h ;
- les formules qui combinent vitesse et énergie, afin de ne doubler que les grandeurs ayant effectivement la dimension d'une vitesse.

Les grandeurs d'énergie, de fatigue, de soutenabilité, les dés et les paramètres sans dimension ne doivent pas être doublés par simple propagation mécanique.

La validation quantitative devra comparer les courbes et tables Race produites avec les anciens profils et les nouveaux profils, mesurer les effets des paliers de +1 unité interne, et vérifier qu'aucune règle ne conserve accidentellement une constante exprimée dans l'ancienne échelle. La présente PR documente la convention et les profils de référence ; elle ne prétend pas réaliser cette migration de l'implémentation.

## 4. Interprétation et limites

1. **VDOT n'est pas une mesure directe de VO₂max.** C'est un indice de performance construit à partir des performances en course et intégrant notamment économie de course et fraction de VO₂max soutenable.
2. **EF est le point le moins déterminé.** Daniels donne une plage assez large. Le point central est choisi pour obtenir une valeur de base exploitable dans le jeu ; il ne doit pas masquer cette variabilité.
3. **I n'est qu'un proxy de VMA.** Il fournit un repère cohérent pour la vitesse proche de VO₂max, mais ne remplace pas une mesure de VMA.
4. **Les AS sont des équivalences de performance.** Elles décrivent un profil théorique homogène ; elles ne prennent pas en compte un déficit d'endurance, une spécialisation sur courte distance ou les conditions de course.
5. **Les profils sont des repères de cohérence.** Ils ne déterminent pas les coordonnées d'énergie des points EF, Seuil et VMA, ni la forme de la courbe entre ces points.
6. **Les AS ne sont pas des points physiologiques supplémentaires.** Elles restent des cibles propres à la distance préparée, conformément au modèle Race V2.
7. **Pas d'extrapolation automatique.** Le profil VDOT 70 donne une référence haute déjà performante. Une extension vers VDOT 80 ou davantage devra être justifiée séparément si le jeu doit représenter des niveaux d'élite.

## 5. Statut pour Run It

Les cinq profils VDOT physiques restent conservés comme **références documentaires**. Les huit profils P8–P15 de la section 3.5.4 deviennent la **nouvelle proposition de référence de jeu**, exprimée dans l'unité interne de 0,5 km/h, pour :
- la composante vitesse de la courbe physiologique EF / Seuil / VMA, avec des coordonnées entières dans l'échelle interne doublée ;
- les valeurs de départ des AS42 / AS21 / AS10 / AS5.

Ils ne changent pas les règles déjà retenues :
- EF < Seuil < VMA ;
- les trois points physiologiques possèdent chacun une coordonnée énergie et une coordonnée vitesse ;
- la courbe de conversion est une table entière énergie → vitesse, sans interpolation ; ses vitesses sont exprimées dans l'unité interne de 0,5 km/h ;
- EF reste le plancher de vitesse et VMA le plafond ;
- l'AS est un repère de course distinct, non un quatrième point physiologique.

Les valeurs des AS sont des valeurs initiales proposées pour les profils de référence. Dans les profils P8–P15, elles sont exprimées dans la même unité interne entière que les autres vitesses. Leur progression, leur éventuelle saturation et leur relation exacte aux points EF / Seuil / VMA restent régies par les décisions de conception Race V2 et doivent être calibrées par simulation.


### 5.1. Cible de progression par cycle Training

**Statut : hypothèse de conception à calibrer par simulation, non règle définitive.**

La cible provisoire pour un cycle Training est de permettre à un joueur réalisant un bon cycle d'obtenir environ **2 à 3 paliers de progression**. La plage de résultats envisagée est :

| Résultat du cycle | Paliers obtenus |
|---|---:|
| Cycle peu réussi | 0 à 1 |
| Cycle correct | 1 à 2 |
| Bon cycle | 2 à 3 |
| Excellent cycle | 3 à 4 |

Un palier représente une amélioration choisie par le joueur sur un point ou une caractéristique de son profil physiologique. Il ne correspond pas automatiquement à +1 km/h : les choix possibles peuvent notamment porter sur la vitesse à énergie constante ou sur l'énergie à vitesse constante.

Cette cible doit être évaluée en fonction de l'impact réel des améliorations sur Race : deux paliers de nature différente ne sont pas nécessairement équivalents en performance. La progression doit également ralentir avec le niveau initial et le niveau déjà atteint. L'équivalence en VDOT sert de contrôle d'ordre de grandeur, pas de conversion mécanique entre VDOT et paliers.



## 5.2. Contrôle de cohérence VDOT des profils entiers

Un contrôle secondaire a été effectué en reconvertissant chaque vitesse AS entière en temps théorique sur sa distance, puis en recalculant le VDOT équivalent par la relation Daniels–Gilbert. Ce contrôle mesure la distorsion introduite par l'arrondi entier ; il ne transforme pas le VDOT en variable du jeu.

| Profil | Marathon (AS42) | Semi (AS21) | 10 km (AS10) | 5 km (AS5) | VDOT moyen indicatif |
|---|---:|---:|---:|---:|---:|
| P8 | 4:41:18 | 2:06:35 | 1:00:00 | 30:00 | 32 |
| P9 | 4:13:10 | 1:55:05 | 54:33 | 25:00 | 37 |
| P10 | 3:30:58 | 1:45:29 | 46:09 | 23:05 | 43 |
| P11 | 3:14:45 | 1:37:22 | 42:51 | 20:00 | 48 |
| P12 | 3:00:50 | 1:24:23 | 40:00 | 18:45 | 53 |
| P13 | 2:48:47 | 1:19:07 | 35:18 | 17:39 | 59 |
| P14 | 2:38:14 | 1:14:28 | 33:20 | 15:47 | 64 |
| P15 | 2:28:55 | 1:10:20 | 31:35 | 15:00 | 68 |

Le VDOT moyen indicatif est la moyenne des quatre VDOT recalculés indépendamment à partir des quatre performances. Les écarts entre distances restent de l'ordre de 2 à 3,5 points selon le profil : ils proviennent principalement de la granularité de 1 km/h, et non d'une prétention à représenter un coureur parfaitement homogène. Les profils doivent donc être lus comme des archétypes de jeu arrondis, pas comme des équivalences VDOT exactes.

### Sensibilité de la performance à une variation de vitesse

À titre de repère, si les quatre vitesses AS d'un profil augmentaient toutes de +0,5 km/h, le VDOT moyen équivalent augmenterait d'environ +2,0 à +2,2 points. Une hausse uniforme de +1 km/h donnerait environ +4,0 à +4,3 points.

Cette sensibilité est un repère global, pas la valeur d'un palier Training : un palier réel modifie un seul point physiologique (vitesse à énergie constante ou énergie à vitesse constante), puis la courbe Race et les performances en découlent. Il n'existe pas encore de correspondance numérique validée entre un palier EF/Seuil/VMA et une variation des quatre AS. Cette correspondance doit être mesurée avec la table physiologique énergie → vitesse et les règles de soutenabilité Race V2.

### Conséquence pour le calibrage des paliers

- **Palier Vitesse :** son incrément doit être calibré en km/h au niveau d'un point physiologique, puis évalué par son effet indirect sur les quatre performances Race. Il ne faut pas lui attribuer directement +2 ou +4 VDOT.
- **Palier Économie :** il réduit l'énergie nécessaire à vitesse constante. VDOT seul ne peut pas en mesurer l'effet, puisque la vitesse théorique reste inchangée ; son intérêt se mesure par la dépense, la réserve et la soutenabilité en Race.
- **Rendements décroissants :** les coûts croissants des paliers doivent être vérifiés contre les gains de performance Race réellement obtenus, et pas seulement contre l'XP accumulée.

Le calibrage numérique des incréments de vitesse, des réductions d'énergie et des seuils d'XP reste **OPEN**. Aucun incrément n'est fixé par cette analyse.


## 6. Plans d'entraînement de référence par distance

**Statut : synthèse documentaire et hypothèse de calibration.** Les valeurs ci-dessous servent à comparer les demandes d'entraînement des préparations 5 km, 10 km, semi-marathon et marathon. Elles ne sont pas des prescriptions universelles ni des règles Training déjà validées.

### 6.1. Durée des plans

Les plans de référence consultés chez Daniels, Pfitzinger et Hansons couvrent des durées variables selon le niveau, le volume hebdomadaire et le degré de spécialisation. Les durées centrales suivantes sont des valeurs de travail représentatives, pas des moyennes statistiques calculées sur un échantillon exhaustif de plans.

| Préparation | Durée centrale retenue | Plage raisonnable de référence |
|---|---:|---:|
| 5 km | 12 semaines | 8–16 semaines |
| 10 km | 12 semaines | 8–16 semaines |
| Semi-marathon | 13 semaines | 11–18 semaines |
| Marathon | 16 semaines | 14–18 semaines |

La durée d'un plan ne doit pas être confondue avec la durée d'un cycle Training dans Run It. Elle sert ici à caractériser la préparation sportive réelle et à construire une pondération relative des contenus.

### 6.2. Répartition indicative du temps de course par intensité

Les pourcentages portent sur le **temps total de course**, et non sur le nombre de séances ou le nombre de kilomètres. Les échauffements, récupérations trottées et retours au calme sont comptés en EF. Les fractions rapides des séances sont ventilées dans leur catégorie d'intensité.

| Préparation | EF | Seuil | VMA | AS spécifique |
|---|---:|---:|---:|---:|
| 5 km | 76 % | 8 % | 12 % | 4 % |
| 10 km | 76 % | 10 % | 9 % | 5 % |
| Semi-marathon | 78 % | 10 % | 4 % | 8 % |
| Marathon | 82 % | 7 % | 2 % | 9 % |

Plages raisonnables observées/synthétisées pour construire des variantes de plans :

| Préparation | EF | Seuil | VMA | AS spécifique |
|---|---:|---:|---:|---:|
| 5 km | 70–85 % | 5–12 % | 8–18 % | 0–6 % |
| 10 km | 72–86 % | 7–14 % | 5–12 % | 2–8 % |
| Semi-marathon | 75–87 % | 7–14 % | 2–7 % | 4–12 % |
| Marathon | 78–90 % | 4–10 % | 0–5 % | 4–12 % |

Les plages ne sont **pas combinables indépendamment** : choisir simultanément toutes les bornes hautes produirait un total incohérent. Les lignes centrales sont des scénarios cohérents totalisant 100 %.

### 6.3. Lecture par distance

- **5 km :** part relativement importante du travail VMA/VO₂max et du seuil. Le travail à AS5 peut être proche de l'allure I/VMA ; il reste distingué ici pour suivre le spécifique de course.
- **10 km :** équilibre entre seuil, travail proche de VO₂max et allure spécifique. Dans les systèmes de zones, l'allure 10 km peut se situer entre T et I ; la séparation en catégories est donc une convention de comptage, pas une frontière physiologique absolue.
- **Semi-marathon :** dominante aérobie, avec un poids accru du seuil et du travail spécifique à AS21 ; la VMA est présente mais minoritaire.
- **Marathon :** forte dominante EF, travail au seuil en quantité limitée, faible volume VMA et part spécifique marathon significative. La préparation spécifique comprend aussi des sorties longues et des blocs à allure marathon.

### 6.4. Conséquences pour le catalogue Training

Pour Run It, cette synthèse suggère de conserver quatre familles de demande : EF, Seuil, VMA et AS de la distance préparée. Elle donne une première pondération des contenus à proposer, sans imposer que chaque plan reproduise exactement ces proportions.

La comparaison doit rester fondée sur le temps de course : une séance de fractionné peut contenir une faible durée à VMA mais une durée totale importante en EF en raison de l'échauffement, des récupérations et du retour au calme. Compter uniquement les minutes rapides surestimerait donc fortement la place de la VMA dans un plan.

### 6.5. Sources et limites de la synthèse

Références consultées :
- Jack Daniels, *Daniels' Running Formula*, 4th edition : zones E, T, I et plans 5 km/10 km.
- Pete Pfitzinger, *Faster Road Racing* : principes de préparation 5 km au semi-marathon, travail au seuil, VO₂max, endurance et vitesse.
- Plans officiels Pete Pfitzinger : plans marathon et semi-marathon, avec cycles de 14 à 18 semaines selon les variantes.
- Plans officiels Hansons : plans marathon et semi-marathon débutant/avancé, généralement structurés sur 18 semaines.

Les auteurs ne publient pas une table normalisée commune donnant la proportion exacte du temps total dans ces quatre catégories. Les durées et pourcentages de cette section sont donc une **synthèse de conception** à partir de la structure des plans et des séances décrites, et non des moyennes arithmétiques extraites des ouvrages. Les catégories se recouvrent partiellement selon les méthodes : notamment AS10 et T/I, ou AS5 et I. Cette limite doit être gardée à l'esprit lors de la calibration.


### 6.6. Première estimation du budget d'énergie Training

Une première estimation du budget moyen d'énergie disponible par tour a été construite à partir du scénario de progression du pool suivant :

- pool initial de **4D6**, soit une espérance de 14 points par lancer ;
- acquisition approximative d'un dé supplémentaire après 4 puis 8 tours, pour atteindre **6 dés** ;
- amélioration progressive des dés (D6 → D8 → D10 → D12), à raison d'environ une amélioration tous les 2 à 3 tours ;
- durées de cycle de travail retenues pour cette estimation : 12 tours pour 5 km, 12 pour 10 km, 13 pour semi-marathon et 16 pour marathon.

L'espérance d'un dé vaut respectivement 3,5 (D6), 4,5 (D8), 5,5 (D10) et 6,5 (D12). En fonction de la cadence d'amélioration, les budgets moyens estimés sont :

| Durée du cycle | Amélioration tous les 3 tours | Amélioration tous les 2 tours | Hypothèse centrale |
|---|---:|---:|---:|
| 12 tours | 19,0 | 20,0 | **19,5** |
| 13 tours | 19,5 | 20,5 | **20,0** |
| 16 tours | 20,6 | 21,9 | **21,2** |

Ces valeurs sont des ordres de grandeur issus d'un scénario simplifié, pas le résultat d'une simulation exhaustive de toutes les séquences possibles d'acquisition et d'amélioration. Elles devront être recalculées dès que le calendrier exact d'évolution des dés sera défini.

En appliquant à titre exploratoire les répartitions centrales de la section 6.2 à ces budgets moyens, on obtient les allocations énergétiques indicatives suivantes :

| Préparation | EF | Seuil | VMA | AS spécifique | Total moyen / tour |
|---|---:|---:|---:|---:|---:|
| 5 km | 14,8 | 1,6 | 2,3 | 0,8 | **19,5** |
| 10 km | 14,8 | 2,0 | 1,8 | 1,0 | **19,5** |
| Semi-marathon | 15,6 | 2,0 | 0,8 | 1,6 | **20,0** |
| Marathon | 17,4 | 1,5 | 0,4 | 1,9 | **21,2** |

Projection indicative sur l'ensemble du cycle :

| Préparation | EF | Seuil | VMA | AS spécifique | Total du cycle |
|---|---:|---:|---:|---:|---:|
| 5 km | 178 | 19 | 28 | 9 | **234** |
| 10 km | 178 | 23 | 21 | 12 | **234** |
| Semi-marathon | 203 | 26 | 10 | 21 | **260** |
| Marathon | 278 | 24 | 7 | 31 | **340** |

Les décimales représentent des espérances agrégées, pas des allocations littérales possibles à chaque tour. Cette transposition suppose que la part d'énergie suit la part de temps de course ; cette hypothèse est pratique pour un premier budget, mais elle n'est pas démontrée. Une séance de qualité concentre davantage l'énergie sur une allure donnée, tandis que ses échauffements et récupérations contribuent à l'EF. Il faudra donc calibrer les séances concrètes plutôt que transformer ces moyennes en quotas rigides.

### 6.7. Implications de conception à examiner

Cette première estimation fait ressortir deux implications importantes pour le système Training. Elles sont des **hypothèses de conception à tester**, pas encore des règles validées.

1. **Les séances de qualité doivent aussi contribuer à l'adaptation EF.** Une séance de seuil ou de VMA comporte généralement une durée substantielle de course facile (échauffement, récupérations, retour au calme), et s'inscrit dans une charge aérobie globale. Dans le jeu, son adaptation ne devrait donc pas être exclusivement affectée au seuil ou à la VMA : une contribution EF doit être intégrée, selon une règle à définir. Il faudra éviter de compter deux fois la même dépense ou de créer artificiellement de l'adaptation sans activité correspondante.
2. **La fatigue devrait réguler l'allocation en qualité davantage que le budget d'énergie brut.** Les budgets moyens suggèrent qu'une réserve d'énergie suffisante peut exister pour concentrer une part importante du pool sur les intensités élevées. Limiter cette allocation uniquement par un plafond d'énergie risquerait de rendre les séances de qualité artificiellement impossibles ou trop uniformes. La fatigue et la pénibilité peuvent constituer le mécanisme principal de régulation : elles rendent possible une allocation ambitieuse, mais en augmentent le coût et les risques (fatigue résiduelle, surentraînement, perte de dés au tour suivant, ou moindre bénéfice net). Le budget d'énergie reste une contrainte physique ; la fatigue devient le régulateur du volume et de la répétition des efforts de qualité.

**Point de vigilance :** cette distinction ne signifie pas que l'énergie est sans importance. Elle signifie que l'énergie détermine ce que le joueur peut engager sur le tour, tandis que la fatigue devrait davantage déterminer combien de travail de qualité il peut soutenir au fil du cycle sans dégrader sa progression.


## 7. Sources


- Jack Daniels, *Daniels' Running Formula*, 4th edition, Human Kinetics, 2022, tables 5.2 (« Training Intensities Based on Current VDOT ») et 5.3 (« Training Intensities for Novice Runners and Others Starting With Slow Performances »).
- Équivalences de performance VDOT calculées selon les équations Daniels–Gilbert, tableaux de référence VDOT 30 à 70.

Les allures E, T et I utilisées pour les points physiologiques sont reprises des tables Daniels. Les temps équivalents de course et les vitesses AS sont des références de performance calculées selon le modèle VDOT. Les conversions en km/h, le choix du point médian EF et leur utilisation comme valeurs de départ dans Run It sont des conventions de modélisation.
