# Profils de référence — vitesses physiologiques et allures spécifiques

**Statut :** propositions de référence à conserver pour le calibrage de la courbe Race V2  
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

Les vitesses sont arrondies au dixième de km/h pour la lisibilité. Les temps de course sources sont conservés ci-dessous afin de permettre de retrouver les conversions.

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


## 4. Interprétation et limites

1. **VDOT n'est pas une mesure directe de VO₂max.** C'est un indice de performance construit à partir des performances en course et intégrant notamment économie de course et fraction de VO₂max soutenable.
2. **EF est le point le moins déterminé.** Daniels donne une plage assez large. Le point central est choisi pour obtenir une valeur de base exploitable dans le jeu ; il ne doit pas masquer cette variabilité.
3. **I n'est qu'un proxy de VMA.** Il fournit un repère cohérent pour la vitesse proche de VO₂max, mais ne remplace pas une mesure de VMA.
4. **Les AS sont des équivalences de performance.** Elles décrivent un profil théorique homogène ; elles ne prennent pas en compte un déficit d'endurance, une spécialisation sur courte distance ou les conditions de course.
5. **Les profils sont des repères de cohérence.** Ils ne déterminent pas les coordonnées d'énergie des points EF, Seuil et VMA, ni la forme de la courbe entre ces points.
6. **Les AS ne sont pas des points physiologiques supplémentaires.** Elles restent des cibles propres à la distance préparée, conformément au modèle Race V2.
7. **Pas d'extrapolation automatique.** Le profil VDOT 70 donne une référence haute déjà performante. Une extension vers VDOT 80 ou davantage devra être justifiée séparément si le jeu doit représenter des niveaux d'élite.

## 5. Statut pour Run It

Ces cinq profils sont conservés comme **références de calibrage proposées** pour :
- la composante vitesse de la courbe physiologique EF / Seuil / VMA ;
- les valeurs de départ des AS42 / AS21 / AS10 / AS5.

Ils ne changent pas les règles déjà retenues :
- EF < Seuil < VMA ;
- les trois points physiologiques possèdent chacun une coordonnée énergie et une coordonnée vitesse ;
- la courbe de conversion est une table entière énergie → vitesse, sans interpolation ;
- EF reste le plancher de vitesse et VMA le plafond ;
- l'AS est un repère de course distinct, non un quatrième point physiologique.

Les valeurs des AS sont des valeurs initiales proposées pour les profils de référence. Leur progression, leur éventuelle saturation et leur relation exacte aux points EF / Seuil / VMA restent régies par les décisions de conception Race V2 et doivent être calibrées par simulation.


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


## 6. Sources

- Jack Daniels, *Daniels' Running Formula*, 4th edition, Human Kinetics, 2022, tables 5.2 (« Training Intensities Based on Current VDOT ») et 5.3 (« Training Intensities for Novice Runners and Others Starting With Slow Performances »).
- Équivalences de performance VDOT calculées selon les équations Daniels–Gilbert, tableaux de référence VDOT 30 à 70.

Les allures E, T et I utilisées pour les points physiologiques sont reprises des tables Daniels. Les temps équivalents de course et les vitesses AS sont des références de performance calculées selon le modèle VDOT. Les conversions en km/h, le choix du point médian EF et leur utilisation comme valeurs de départ dans Run It sont des conventions de modélisation.
