# Run It — Game Design Document

**Version :** GDD V3 — vision Training B / Race énergie–soutenabilité  
**Date de consolidation :** 16 novembre 2026 — révision courbe énergie–soutenabilité  
**Statut :** document de référence du design ; paramètres d'équilibrage et intégration encore partiellement ouverts.

> Ce document remplace les anciennes descriptions du Training CURRENT et le modèle Race fondé sur une conversion énergie → vitesse. Il rassemble les décisions de conception retenues, les orientations structurantes les plus récentes, les paramètres qui restent expérimentaux et les écarts entre le design et les prototypes. Il ne prétend pas que les règles décrites sont toutes implémentées.

---

## 0. Gouvernance et lecture du document

### 0.1. Autorité

Le GDD porte les règles de design validées et leur statut. Les autres documents ont des fonctions distinctes :

| Document | Rôle |
|---|---|
| README.md | Présentation courte du projet et index des références |
| DEVELOPMENT_PLAN.md | Ordre des chantiers, dépendances, priorités et écarts à traiter |
| CURRENT_STATE.md | État réellement présent dans le code au dernier snapshot |
| docs/game-design/RACE_V2_DESIGN.md | Spécification détaillée de l'ancienne Race V2 énergie–vitesse ; certaines règles tactiques restent des références, mais son modèle physiologique est supersédé par le présent GDD |
| docs/game-design/TRAINING_B_DECISIONS.md | Décisions Training B consolidées jusqu'à Q55 ; à lire avec les clarifications ultérieures intégrées ici |
| docs/game-design/PHYSIOLOGICAL_SPEED_REFERENCE_PROFILES.md | Références sportives VDOT et ancienne proposition de profils vitesse ; conservées pour traçabilité, non normatives pour le modèle actuel |
| DOCUMENTATION_AUDIT.md | Historique des divergences documentaires et de leurs résolutions |
| experiments/current/** | Prototypes, harnesses et rapports expérimentaux ; ils ne créent pas de règles par eux-mêmes |

En cas de divergence, appliquer l'ordre suivant :

1. instruction explicite de la mission en cours ;
2. décisions explicites les plus récentes de l'utilisateur ;
3. règles validées dans ce GDD ;
4. documents de décisions spécifiques, dans la limite de leur statut et de leur date ;
5. CURRENT_STATE.md pour le comportement implémenté ;
6. code et tests pour vérifier ce comportement ;
7. expériences, rapports et hypothèses historiques.

Une différence entre design et code doit être signalée, jamais résolue silencieusement. Une mécanique présente dans un prototype n'est pas automatiquement une règle validée.

### 0.2. Statuts

- **DECISION VALIDATED** : arbitrage explicitement retenu par l'utilisateur et intégré au design.
- **DESIGN DIRECTION** : principe structurant retenu comme direction de conception, mais dont certaines conséquences ou règles de détail restent à arbitrer.
- **EXPERIMENTAL** : mécanisme, valeur, politique ou résultat utilisé pour explorer une hypothèse ; non normatif.
- **OPEN** : question de conception ou paramètre qui demande encore un arbitrage.
- **IMPLEMENTATION GAP** : règle ou frontière de design absente, incomplète ou non raccordée dans le prototype.
- **CURRENT IMPLEMENTATION** : comportement effectivement présent dans le code ; ce statut ne valide pas sa pertinence comme règle.
- **HISTORICAL / SUPERSEDED** : ancienne règle ou ancienne hypothèse conservée pour comprendre l'évolution du projet, mais qui ne doit plus guider le design actif.

### 0.3. Principe de conception

La chaîne normale est :

~~~text
IDÉE → ANALYSE → PROPOSITION → DÉCISION UTILISATEUR → GDD
→ AUDIT → IMPLÉMENTATION → TESTS → SIMULATION → PLAYTEST
~~~

Le GDD décrit le jeu voulu. Le plan de développement décrit comment s'en rapprocher. Les tests vérifient des invariants ; les simulations explorent des comportements dans les limites des politiques et hypothèses qu'elles utilisent. Aucun de ces éléments ne se substitue aux autres.

---

# 1. Vision du jeu

## 1.1. Concept

Run It est un jeu tactique de préparation à la course. Chaque joueur incarne un entraîneur qui construit progressivement le profil d'un coureur, organise ses séances, arbitre entre développement physiologique et fatigue, puis met cette préparation à l'épreuve dans une course.

La partie repose sur deux phases complémentaires :

1. **Training** : construire un potentiel physiologique, développer la capacité à soutenir les dépenses, faire progresser le pool de dés et gérer la fatigue.
2. **Race** : mobiliser ce potentiel secteur après secteur, en arbitrant la dépense d'énergie et la consommation de soutenabilité, avec une part d'incertitude et d'interaction tactique.

La préparation n'est pas un simple prélude à la course : elle constitue la majeure partie de l'expérience et doit produire des profils réellement différenciés. La course donne une finalité aux choix d'entraînement et révèle leurs conséquences.

## 1.2. Expérience cible

**DECISION VALIDATED — cible de partie :**

- 2 à 4 joueurs en priorité ;
- environ 60 à 90 minutes ;
- environ deux tiers du temps consacré au Training et un tiers à la Race ;
- une préparation de l'ordre de 12 à 16 tours de Training à tester selon le scénario ;
- une course finale qui exploite les différences de préparation ;
- une coopération positive et opportuniste, sans compétition pour une ressource commune.

Le joueur doit avoir le sentiment de construire une préparation cohérente, de faire des arbitrages compréhensibles et d'en observer les effets pendant la course. Le jeu doit récompenser la qualité des décisions de préparation, pas uniquement le résultat final de la course.

## 1.3. Principes directeurs

1. **La préparation construit le profil.** Training n'est pas une simple accumulation de bonus génériques.
2. **La Race exploite le profil.** Les choix de dépense doivent faire apparaître les compromis construits pendant Training.
3. **La physiologie est représentée par peu de dimensions.** Le modèle doit conserver l'information utile sans multiplier les variables redondantes.
4. **L'énergie est la grandeur de performance.** La vitesse n'est pas une coordonnée indépendante nécessaire au calcul du jeu.
5. **La soutenabilité régule la durée de maintien.** Une dépense élevée peut être performante à court terme et coûteuse à soutenir.
6. **La fatigue est un régulateur longitudinal.** Elle doit rendre les choix de qualité intéressants sans imposer un quota artificiel uniforme.
7. **Les décisions appartiennent au joueur.** Les politiques automatiques servent à tester, pas à définir une stratégie humaine obligatoire.
8. **Les mécanismes doivent rester testables et directement implémentables.** Pas d'abstraction logicielle prématurée.

## 1.4. Critères d'évaluation du design

Les critères de C2 servent à évaluer les propositions et les prototypes ; ils ne constituent pas des règles de jeu.

| Critère | Poids |
|---|---:|
| Qualité des décisions | 20 |
| Feedback et progression | 15 |
| Différenciation physiologique | 15 |
| Impact du Training sur la Race | 15 |
| Maîtrise et adaptation | 10 |
| Fluidité et accessibilité | 10 |
| Risque opportuniste | 8 |
| Coopération positive | 7 |
| **Total** | **100** |

Une proposition qui améliore une métrique locale mais détériore fortement la lisibilité, la différenciation des profils ou l'impact réel du Training sur la Race n'est pas automatiquement une amélioration.

## 1.5. Course cible et structure de préparation

Le joueur choisit sa course cible avant le début du Training. Cette cible ne peut pas être changée en cours de partie. Elle détermine le contexte de préparation et la course finale.

Les distances de référence envisagées sont 5 km, 10 km, semi-marathon et marathon. Les scénarios peuvent utiliser des durées de Training différentes, tout en conservant le même nombre de tours pour tous les joueurs d'un même scénario.

Les durées centrales de 12, 12, 13 et 16 tours respectivement sont des repères de travail issus des références de plans sportifs ; elles ne sont pas encore un calendrier de jeu validé.

---

# 2. Modèle physiologique : énergie et soutenabilité

## 2.1. Changement de modèle

**DESIGN DIRECTION retenue le 14 novembre 2026 :** le modèle de Race ne doit plus dépendre d'une courbe de conversion énergie → vitesse.

La vitesse est une convention possible d'affichage ou de score, pas une dimension physiologique indépendante indispensable au système. La conversion énergie → vitesse étant bijective dans le modèle envisagé, elle ajoute une coordonnée dérivée sans apporter l'information minimale recherchée.

Le modèle de référence passe donc de trois coordonnées — énergie, vitesse et consommation de soutenabilité — à deux dimensions utiles :

- **Énergie** : niveau de dépense mobilisé et grandeur qui contribue directement à la performance / au score.
- **Consommation de soutenabilité** : coût associé au maintien de cette dépense.

La course devient un problème tactique de maximisation de l'énergie dépensée sous contrainte de soutenabilité.

Cette évolution remplace le modèle Race V2 antérieur fondé sur une table entière énergie → vitesse, un déplacement horizontal de cette courbe et un score égal à la somme des vitesses.

## 2.2. Trois axes de lecture physiologique

La représentation conceptuelle utilise trois axes parallèles ou superposés :

1. **Axe énergie** : gradué sur toute la plage de dépense que le pool de dés peut produire.
2. **Repères physiologiques** : EF, Seuil et VMA situent des seuils dans ce domaine énergétique.
3. **Axe de consommation de soutenabilité** : associe à chaque niveau d'énergie le coût de soutenabilité correspondant.

EF, Seuil et VMA ne sont donc pas trois vitesses à convertir. Ce sont trois repères physiologiques qui organisent l'espace des dépenses et leur coût de maintien.

L'ordre physiologique reste :

~~~text
EF < Seuil < VMA
~~~

- EF représente le niveau de dépense de référence facile.
- Seuil représente un niveau supérieur de dépense soutenable à une intensité plus élevée.
- VMA représente le plafond de dépense par secteur dans le modèle de jeu.

Les coordonnées énergétiques exactes des trois repères ne sont pas encore calibrées.

## 2.3. Courbe énergie–soutenabilité : ancres et domaine

**DECISION VALIDATED — 16 novembre 2026 :** la courbe est une fonction entière de lecture, construite à partir de trois ancres de soutenabilité fixes :

| Repère | Soutenabilité S |
|---|---:|
| EF | 1 |
| Seuil | 5 |
| VMA | 13 |

S est un **indice ordinal de coût**, pas une durée ni une mesure physiologique en unités physiques. Plus S est élevé, plus le maintien de la dépense est coûteux. Le coût de base d'un secteur est la valeur S lue sur la courbe. Cette échelle remplace l'ancienne formulation selon laquelle la consommation était nulle à EF : dans le modèle retenu, EF est le coût minimal, égal à 1.

Les trois énergies EF, Seuil et VMA sont des entiers stockés. La courbe complète est déterminée par ces trois valeurs ; aucune table d'énergie–vitesse n'est requise.

On définit n = Seuil − EF, largeur de la zone basse, et m = VMA − Seuil, largeur de la zone haute. Le domaine valide est 3 ≤ n ≤ 8, 2 ≤ m ≤ 8 et m ≤ n. Il existe 27 profils de forme autorisés. La condition m ≤ n garantit un coude moyen d'au moins 2 ; il vaut exactement 2 lorsque m = n.

La courbe est une abstraction de jeu inspirée de la relation intensité–durée et des domaines d'intensité modéré, lourd et sévère. Les ancres 1–5–13 et les bornes n/m sont des choix de modélisation, pas des constantes physiologiques mesurées.

### Repères physiologiques (justification qualitative)

| Domaine d'effort | Repère physiologique approximatif | Lecture dans le jeu |
|---|---|---|
| Modéré | Sous le premier seuil, autour de l'endurance facile | Zone basse, plateau puis hausse lente de S |
| Lourd | Entre le seuil critique et l'approche de la consommation maximale d'oxygène | Zone haute, coût croissant et maintien de plus en plus limité |
| Sévère | Proche de la VMA / vVO₂max, effort maximal de quelques minutes | Extrémité haute de la courbe, coût maximal |

La relation intensité–durée est fortement non linéaire : une hausse donnée d'intensité réduit beaucoup plus la durée de maintien à proximité des limites. Le coude encode cette asymétrie. Les durées usuelles évoquées pour le seuil et la VMA sont des ordres de grandeur dépendant du coureur et du protocole ; elles ne servent pas de conversion directe entre S et minutes.

## 2.4. Construction des cartes de soutenabilité

La courbe se lit sans calcul en partie, sur deux cartes déterminées par n et m.

### 2.4.1. Zone basse : EF → Seuil

Les quatre points de soutenabilité entre EF et Seuil sont répartis sur les quatre derniers pas avant le Seuil. Les pas précédents restent au plateau S = 1.

Pour n ≥ 4 :

~~~text
S(E) = max(1, 5 − (Seuil − E))
~~~

Pour n = 3, les quatre points sont répartis sur trois pas : les coûts des pas sont 1, 1, 2, d'où les valeurs S = 1, 2, 3, 5 de EF à Seuil.

| n | Valeurs S de EF à Seuil | Coût de chaque pas |
|---:|---|---|
| 3 | 1 – 2 – 3 – 5 | 1, 1, 2 |
| 4 | 1 – 2 – 3 – 4 – 5 | 1, 1, 1, 1 |
| 5 | 1 – 1 – 2 – 3 – 4 – 5 | 0, 1, 1, 1, 1 |
| 6 | 1 – 1 – 1 – 2 – 3 – 4 – 5 | 0, 0, 1, 1, 1, 1 |
| 7 | 1 – 1 – 1 – 1 – 2 – 3 – 4 – 5 | 0, 0, 0, 1, 1, 1, 1 |
| 8 | 1 – 1 – 1 – 1 – 1 – 2 – 3 – 4 – 5 | 0, 0, 0, 0, 1, 1, 1, 1 |

### 2.4.2. Zone haute : Seuil → VMA

On répartit les huit points entre Seuil et VMA par division entière :

~~~text
q = floor(8 / m)
r = 8 mod m
~~~

Chaque pas coûte q ; les r derniers pas coûtent q + 1. Comme m ≤ 8, chaque pas coûte au moins 1 : la zone haute est strictement croissante, sans plateau.

| m | Valeurs S de Seuil à VMA | Coût de chaque pas |
|---:|---|---|
| 2 | 5 – 9 – 13 | 4, 4 |
| 3 | 5 – 7 – 10 – 13 | 2, 3, 3 |
| 4 | 5 – 7 – 9 – 11 – 13 | 2, 2, 2, 2 |
| 5 | 5 – 6 – 7 – 9 – 11 – 13 | 1, 1, 2, 2, 2 |
| 6 | 5 – 6 – 7 – 8 – 9 – 11 – 13 | 1, 1, 1, 1, 2, 2 |
| 7 | 5 – 6 – 7 – 8 – 9 – 10 – 11 – 13 | 1, 1, 1, 1, 1, 1, 2 |
| 8 | 5 – 6 – 7 – 8 – 9 – 10 – 11 – 12 – 13 | 1, 1, 1, 1, 1, 1, 1, 1 |

### 2.4.3. Profils autorisés et coude

La pente moyenne de la zone basse vaut 4/n ; celle de la zone haute vaut 8/m. Le rapport des pentes (haute / basse) vaut :

~~~text
coude moyen = (8 / m) / (4 / n) = 2n / m
~~~

La contrainte m ≤ n garantit un rapport supérieur ou égal à 2. Le rapport est exactement 2 sur la diagonale m = n et supérieur à 2 lorsque m < n. Ce n'est pas un saut local strict au Seuil : la répartition entière peut produire un premier pas haut peu coûteux ; le coude est une propriété des pentes moyennes.

| n \ m | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 3 | ✓ | ✓ | – | – | – | – | – |
| 4 | ✓ | ✓ | ✓ | – | – | – | – |
| 5 | ✓ | ✓ | ✓ | ✓ | – | – | – |
| 6 | ✓ | ✓ | ✓ | ✓ | ✓ | – | – |
| 7 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – |
| 8 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

### 2.4.4. Exemple de lecture

Pour EF = 10, Seuil = 14 et VMA = 17, n = 4 et m = 3 :

| Énergie E | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Soutenabilité S(E) | 1 | 2 | 3 | 4 | 5 | 7 | 10 | 13 |

Les cartes sont lues depuis EF pour la zone basse et depuis Seuil pour la zone haute ; aucune interpolation ni aucun arrondi ne sont nécessaires en partie.

## 2.5. Développement intensif et extensif

La distinction porte sur deux transformations différentes du profil :

| Développement | Effet recherché | Traduction dans le modèle |
|---|---|---|
| **Intensif** | Faire progresser l'intensité accessible | Augmenter l'énergie d'une ancre, donc déplacer un repère vers une dépense supérieure, sous réserve des contraintes de forme du profil. |
| **Extensif** | Augmenter le temps de maintien à une intensité donnée | Réduire la soutenabilité S associée à une énergie donnée, sans augmenter cette énergie. Dans le modèle discret, cela passe par l'évolution des ancres et des cartes, pas par une seconde courbe stockée indépendante. |

L'intensif développe le niveau de dépense accessible ; l'extensif développe la capacité à maintenir une dépense donnée. L'économie de course est représentée par la baisse du coût de soutenabilité à énergie égale, sans réintroduire une conversion cachée énergie → vitesse.

## 2.6. Rôle spécifique de l'EF

L'EF constitue le socle de développement général.

**DECISION VALIDATED — portée des paliers EF, 14 novembre 2026 :**

- une progression EF agit sur les trois repères physiologiques EF, Seuil et VMA ;
- elle applique un déplacement commun qui conserve les écarts relatifs entre ces repères ;
- cette progression générale conserve donc n et m et translate le profil énergétique sans modifier la forme des cartes.

L'EF ne doit donc pas être interprétée comme une progression locale qui ne ferait évoluer que le point EF.

## 2.7. Rôle des qualités Seuil et VMA

Les adaptations de qualité développent plus spécifiquement le repère concerné :

- une adaptation Seuil agit sur le repère Seuil ;
- une adaptation VMA agit sur le repère VMA ;
- ces progressions modifient les positions relatives du profil, contrairement à la translation commune produite par un palier EF.

Une spécialisation intensive peut déplacer un repère sans améliorer automatiquement la soutenabilité de la dépense correspondante. Le développement extensif est représenté par une évolution de la forme des cartes au travers des ancres, sous réserve des contraintes n/m.

## 2.8. Progression des ancres et invariants

Une progression d'ancre est une hausse de +1 de l'énergie correspondante. Elle n'est autorisée que si le profil résultant respecte 3 ≤ n ≤ 8, 2 ≤ m ≤ 8 et m ≤ n.

| Ancre augmentée | Nouveau profil | Condition |
|---|---|---|
| EF +1 | (n − 1, m) | n − 1 ≥ 3 et m ≤ n − 1 |
| Seuil +1 | (n + 1, m − 1) | n + 1 ≤ 8 et m − 1 ≥ 2 |
| VMA +1 | (n, m + 1) | m + 1 ≤ 8 et m + 1 ≤ n |
| Progression générale | (n, m) inchangé | toujours possible |

Si une condition échoue, l'ancre ne progresse pas : sa jauge reste pleine et attend qu'une autre ancre ait évolué. Aucun point n'est perdu et aucune ancre ne monte automatiquement.

Invariants de conception :

1. les ancres de soutenabilité restent EF = 1, Seuil = 5, VMA = 13 ;
2. S(E) est non décroissante dans la zone basse et strictement croissante dans la zone haute ;
3. une progression d'ancre ou une progression générale ne rend aucune énergie plus coûteuse ;
4. une modification d'ancre ne change que la ou les zones adjacentes ; le Seuil touche les deux ;
5. aucune soutenabilité propre aux allures spécifiques n'est stockée en dehors des trois ancres et des cartes dérivées.

L'invariant de non-augmentation des coûts a été vérifié manuellement dans les cas de conception. Une vérification exhaustive par script et tests reste un préalable à l'implémentation et à l'impression définitive des cartes.

Le profil (8, 8) est un plafond de forme : aucune ancre ne peut progresser seule. La progression générale peut néanmoins déplacer ensemble les trois énergies sans changer n ni m. Toute extension de l'échelle au-delà de ces bornes est OPEN et ne fait pas partie de la règle actuelle.

### 2.8.1. Cas de progression et cas limites

| Cas | Profil initial | Tentative | Résultat |
|---|---|---|---|
| Profil moyen (4, 3) | EF 10, Seuil 14, VMA 17 | VMA +1 | Autorisé : (4, 4), courbe 1–2–3–4–5–7–9–11–13 |
| Diagonale (4, 4) | EF 10, Seuil 14, VMA 18 | VMA +1 | Bloqué : m deviendrait 5 > n. Seuil +1 donne (5, 3), puis VMA +1 devient possible |
| Profil comprimé (3, 2) | EF 20, Seuil 23, VMA 25 | EF +1 ou Seuil +1 | Bloqués car n tomberait sous 3 ou m sous 2. VMA +1 vers (3, 3) reste possible |
| Profil saturé (8, 8) | EF 10, Seuil 18, VMA 26 | Toute ancre seule +1 | Bloquée. Seule la progression générale peut encore déplacer les trois ancres ensemble |

Exemple de contrainte de forme : un coureur de profil (4, 4) ne peut pas étendre sa VMA sans élargir d'abord sa zone basse. Le joueur doit développer le Seuil avant de pouvoir repousser VMA. Il s'agit d'un garde-fou de design destiné à empêcher un profil « explosif sans fond » dans l'échelle courante, et non d'une loi physiologique universelle.

## 2.9. Allures spécifiques : énergie et réserve d'allure

Les allures spécifiques (AS42, AS21, AS10 et AS5) constituent une couche de spécialisation en énergie, posée sur la courbe de base sans la déformer.

Chaque AS stocke deux entiers :
- **Énergie AS** : niveau énergétique de référence de cette allure.
- **Réserve d'allure (RA)** : nombre de réductions de coût de 1 disponibles à cette allure, au maximum une réduction par secteur.

L'ordre obligatoire est :

~~~text
EF < AS42 ≤ AS21 ≤ Seuil ≤ AS10 ≤ AS5 ≤ VMA
~~~

Aucune soutenabilité n'est stockée pour une AS. Son coût de base est toujours lu sur la courbe générale : S(Énergie AS). La RA ne s'applique qu'à l'énergie exacte de l'AS concernée.

### 2.9.1. Progression d'une AS

À chaque palier d'une AS, le joueur choisit une seule option :

1. **Énergie +1** : augmente l'énergie de référence de l'allure, si l'ordre des AS et les ancres le permettent.
2. **RA +1** : conserve l'énergie de référence et augmente d'un point la réserve d'allure.

L'énergie et la RA consomment le même compteur de paliers : choisir la RA ne contourne pas le coût croissant de la progression. La limite de progression est de cinq paliers par AS. Les seuils de jauge de référence sont 10, 12, 15, 19, 24 puis 30 points ; la correspondance exacte entre ces seuils et les cinq paliers doit rester cohérente avec la jauge d'implémentation.

Si l'énergie d'une AS atteint son ancre supérieure (AS21 au Seuil, AS5 à VMA), l'option Énergie est bloquée et seul le choix RA reste disponible. Une progression des ancres peut pousser une AS vers le haut pour maintenir l'ordre ; une AS ne baisse jamais. Les règles détaillées de propagation aux AS voisines doivent préserver strictement l'ordre sans accorder de palier gratuit.

### 2.9.2. Dépense de la réserve d'allure

Quand un secteur est couru exactement à l'énergie d'une AS, le joueur peut dépenser un point de RA de cette AS. Le coût de soutenabilité du secteur est alors réduit de 1, sans jamais descendre sous 1. Au plus un point de RA peut être dépensé par secteur. Une RA d'AS21 ne procure aucun avantage à une dépense différente de l'énergie AS21.

La RA est une capacité permanente : le stock disponible est reconstitué à sa valeur complète au début de chaque course. Une réserve vide ramène exactement au coût de base de la courbe.

L'énergie achète une allure de référence plus élevée ; la RA achète une réduction locale du coût de maintien. L'augmentation d'énergie peut accroître S de plus de 1, alors qu'un point de RA réduit le coût d'un seul point et uniquement sur les secteurs courus exactement à cette AS.

Exemple : pour un profil EF 12, Seuil 19, VMA 24, l'AS21 peut être positionnée à l'énergie 18. La carte donne S(18) = 4. Avec RA = 2, le joueur peut payer 3 au lieu de 4 sur deux secteurs courus exactement à l'énergie 18 ; les autres secteurs paient le coût de base ou le coût dégradé applicable.

## 2.10. Ce qui est abandonné dans le modèle actif

Les éléments suivants appartiennent à l'ancien modèle énergie–vitesse et ne doivent plus être traités comme des règles actives :

- vitesse comme seconde coordonnée physiologique ;
- table entière énergie → vitesse ;
- interpolation ou lecture de vitesse dans cette table ;
- score de course égal à la somme des vitesses ;
- plancher de vitesse EF et plafond de vitesse VMA ;
- décalage horizontal de la courbe énergie → vitesse pour représenter la fatigue de soutenabilité ;
- AS comme points de conversion nécessaires au moteur ;
- terrain et aspiration appliqués comme modificateurs de conversion énergie → vitesse.

Les AS restent toutefois une couche de spécialisation en énergie et réserve d'allure, distincte de l'ancienne fonction de conversion.

Les références VDOT et les profils P8–P15 du document PHYSIOLOGICAL_SPEED_REFERENCE_PROFILES.md restent des éléments de traçabilité sportive. Leur ancienne échelle de vitesse interne à 0,5 km/h ne définit plus le modèle physiologique actif. Aucune conversion automatique vers les coordonnées énergétiques n'est établie.

# 3. Training B — structure de la phase de préparation

## 3.1. Rôle et statut

**DECISION VALIDATED :** Training B est la cible de développement. L'ancien Training CURRENT est historique et n'est pas une cible de compatibilité.

Training construit progressivement :

- le profil physiologique EF / Seuil / VMA ;
- la soutenabilité associée aux niveaux de dépense ;
- le pool permanent de dés ;
- le portefeuille d'options de séances ;
- la fatigue résiduelle qui conditionnera l'état du coureur au départ de la Race.

Training B doit rester une phase de choix d'allocation et de construction du profil, pas un simple calcul automatique de gains.

## 3.2. Pool permanent de dés

Le joueur commence avec quatre dés et peut progresser jusqu'à six dés.

Chaque dé possède une taille parmi :

~~~text
D6 → D8 → D10 → D12
~~~

Le joueur peut :

- ajouter un dé au pool, dans la limite de six ;
- améliorer individuellement un dé d'un cran ;
- choisir quel dé améliorer.

Les dés améliorés ne reçoivent pas de bonus numérique permanent supplémentaire : la taille du dé constitue leur caractéristique. Les anciens bonus +1 / +2 / +3 sont HISTORICAL / SUPERSEDED.

**OPEN :** calendrier, seuils et événements précis qui accordent un dé supplémentaire ou une amélioration. Les seuils CTL 50/100 et l'amélioration après quatre qualités réussies appartiennent à l'ancien Training et ne sont pas repris comme règles Training B.

## 3.3. Lancer et décisions de dés

Au début d'un tour, le joueur lance N−1 dés ; le dernier dé reste en réserve.

Il choisit ensuite une seule opération :

| Action | Effet |
|---|---|
| **Keep** | Conserver les résultats du lancer initial |
| **Reroll** | Relancer un dé déjà lancé |
| **Add** | Lancer le dé en réserve |
| **Add + Reroll** | Relancer un dé déjà lancé, puis lancer le dé en réserve |

L'opération Add + Reroll résout le reroll avant le lancer du dé en réserve. Les résultats finaux de tous les dés retenus dans le pool déterminent l'énergie disponible.

L'énergie disponible est la somme des faces finales. Le TN est l'espérance du pool permanent complet, dé de réserve compris. Le TN est une référence de charge pour la rétroaction des dés ; ce n'est pas un plafond de dépense.

## 3.4. Fatigue issue des dés

**DECISION VALIDATED — 11 novembre 2026 :**

- la rétroaction conserve la courbe quasi-Fibonacci historique du prototype ;
- l'écart entre l'énergie finale des dés et le TN est arrondi à l'entier supérieur avant consultation de cette courbe ;
- le TN est la somme des espérances des dés du pool complet et peut être fractionnaire ;
- la contribution peut représenter une charge, être nulle ou représenter une récupération ;
- la fatigue cumulée est entière et ne descend pas sous zéro ;
- cette contribution est calculée après l'opération de dés et avant la résolution des séances ;
- elle reste acquise même si une séance bust ensuite.

La fatigue issue des dés est distincte de la fatigue spécifique des séances. Elle ne doit pas être annulée rétroactivement par un bust. L'énergie issue du lancer reste la somme finale des dés : la fatigue ne réduit pas le budget énergétique.

La courbe de référence actuellement utilisée par le chemin Training B applique :

~~~text
offset = ceil(énergie_finale − TN)

si offset ≥ −1 : fatigue_dés = Fibonacci(offset + 3)
si offset ∈ {−2, −3} : fatigue_dés = 0
si offset ≤ −4 : fatigue_dés = −récupération(offset)
~~~

Valeurs de référence de la fonction actuelle :

| Offset | Contribution de fatigue |
|---:|---:|
| −1 | +1 |
| 0 | +2 |
| +1 | +3 |
| +2 | +5 |
| +3 | +8 |
| +4 | +13 |
| −2 ou −3 | 0 |
| −4 ou −5 | −1 |
| −6 ou −7 | −2 |
| −8 | −3 |
| −9 | −5 |
| ≤ −10 | −8 |

La fatigue cumulée après application de cette contribution est bornée inférieurement à zéro. Cette table décrit la courbe quasi-Fibonacci retenue et sa référence d'implémentation actuelle ; toute modification de la courbe doit être explicite et testée. Elle ne doit pas être remplacée par une variation linéaire de l'énergie dépensée moins le TN.

## 3.5. Répartition de l'énergie

L'énergie finale des dés est conservée et répartie librement entre deux compartiments :

- **budget EF** ;
- **budget Qualité**, lui-même réparti librement entre Seuil et VMA.

Il est possible d'investir dans Seuil et VMA au cours du même tour.

La répartition est une décision du joueur. Le système ne transforme pas automatiquement un reliquat en une autre ressource ou en une adaptation. L'énergie non dépensée reste non dépensée.

Il n'existe pas de CTL dans Training B. Le CTL de l'ancien Training ne doit pas servir de variable de préparation ni de pont caché vers Race.

Le modèle ne réintroduit pas de quota dur général du type Qualité ≤ EF. La régulation de l'investissement en qualité doit émerger de la fatigue, de la pénibilité, des coûts d'opportunité et de la progression, sauf limite particulière justifiée pour une séance donnée.

## 3.6. Catalogue de séances et doses

Le catalogue initial est organisé autour des trois filières physiologiques :

| Filière | Entrées de base |
|---|---|
| EF | EF1, EF2, EF3, EF4 |
| Seuil | Seuil3, Seuil4, Seuil5 |
| VMA | VMA3, VMA4, VMA5 |

Le chiffre de l'identifiant représente la dose énergétique exacte de la séance. Il ne représente ni une capacité physiologique, ni une adaptation, ni le RPE.

Chaque dose est une entrée de séance distincte. Une séance ne doit pas être comprise comme une option unique dont le coût varierait librement.

Le socle initial doit proposer au moins une option dans chacune des familles EF, Seuil et VMA. Le portefeuille de séances s'enrichit ensuite.

## 3.7. Données propres à une séance

Chaque option du catalogue doit pouvoir décrire au minimum :

| Champ | Rôle |
|---|---|
| Identifiant, nom, description | Identifier et rendre la séance compréhensible |
| Famille / filière | EF, Seuil ou VMA ; les familles transversales sont traitées séparément |
| Dose / coût énergétique | Quantité exacte d'énergie requise |
| RPE | Intensité et difficulté intrinsèque utilisées pour le risque |
| Adaptation principale | Contribution principale à une réserve d'adaptation |
| Adaptation secondaire | Contribution complémentaire, éventuellement vers EF |
| Fatigue spécifique | Pénibilité propre à la séance, indépendante de la fatigue des dés |
| Condition d'éligibilité | Condition qui rend l'option accessible |
| Limite par tour | Limite facultative et spécifique, lorsqu'elle est justifiée |

Le coût énergétique, le RPE, les adaptations et la fatigue sont des variables distinctes. Il ne faut pas les fusionner dans un coefficient unique. L'énergie détermine ce que le joueur peut engager sur le tour ; la fatigue régule davantage le volume et la répétition des efforts de qualité au fil du cycle.

Les adaptations sont définies par séance et par dose. Elles sont fixes pour une occurrence réussie ; elles ne sont pas multipliées automatiquement par le résultat des dés. Les effets conditionnels ou combos entre séances sont une extension possible, mais restent désactivés dans la première version : pas de moteur de combos ni de séquençage obligatoire.

## 3.8. Adaptations primaires et secondaires

Les séances peuvent contribuer à plusieurs dimensions physiologiques.

- Une séance EF contribue principalement à EF.
- Une séance Seuil contribue principalement à Seuil et peut aussi contribuer à EF.
- Une séance VMA contribue principalement à VMA et peut aussi contribuer à EF.
- Les contributions secondaires EF des séances de qualité alimentent le même compteur EF que les adaptations primaires des séances EF.

Cette contribution secondaire représente notamment le fait qu'une séance de qualité comporte une part de travail aérobie général. Elle ne doit pas être interprétée comme une création d'énergie gratuite : elle est attachée à une séance effectivement réalisée et à ses adaptations définies.

Les valeurs numériques des adaptations primaires et secondaires restent EXPERIMENTAL tant qu'elles n'ont pas été explicitement calibrées et promues.

## 3.9. RPE, risque et bust

Le RPE caractérise la difficulté intrinsèque de la séance. Il est distinct du coût énergétique.

Le risque dépend du dépassement entre le RPE de la séance et le RPE autorisé pour le tour. Le meilleur dé du pool persistant constitue le dé de référence du test.

La forme candidate utilisée dans le prototype est :

~~~text
excès = max(0, RPE_séance − RPE_autorisé)
bust si face_brute_du_meilleur_dé ≤ excès
~~~

Le RPE autorisé est une donnée de contexte du tour ; sa dérivation complète et son articulation avec les décisions de dés restent à finaliser. Les valeurs de RPE, les seuils de risque et les pénibilités du catalogue sont EXPERIMENTAL.

Ordre de résolution :

1. calculer et conserver la fatigue issue des dés ;
2. répartir l'énergie et composer le programme ;
3. résoudre les séances dans l'ordre prévu ;
4. tester le risque lorsqu'une séance dépasse le RPE autorisé ;
5. au premier bust, annuler la séance concernée et toutes les séances planifiées après elle ;
6. conserver les effets des séances réussies avant le bust.

Une séance bustée ne produit ni adaptation, ni progression de filière, ni fatigue spécifique. Les séances non exécutées après le bust ne produisent pas non plus ces effets. La fatigue issue des dés reste néanmoins acquise.

**OPEN :** convention définitive de test, autorisation du risque, ordre exact des choix et conséquences éventuelles au-delà de l'annulation de séance. Les blessures persistantes ne sont pas une conséquence validée du bust.

## 3.10. Progression physiologique par paliers

Les adaptations réussies alimentent trois réserves de progression indépendantes : EF, Seuil et VMA.

Chaque filière possède ses propres seuils de palier, croissants et de plus en plus espacés afin de matérialiser les rendements décroissants. Lorsqu'un palier est atteint :

- son coût est consommé après un choix valide ;
- l'excédent d'adaptation est conservé ;
- le joueur choisit la transformation permise par le palier ;
- aucune transformation automatique n'est appliquée.

Les seuils, les incréments et les calendriers de palier restent OPEN.

### 3.10.1. Portée d'un palier EF

Un palier EF agit sur les trois repères EF, Seuil et VMA par une transformation commune. Il conserve leurs écarts relatifs.

Les adaptations EF secondaires produites par les séances Seuil et VMA alimentent également cette progression EF.

### 3.10.2. Portée d'un palier Seuil ou VMA

Un palier Seuil agit sur le repère Seuil uniquement. Un palier VMA agit sur le repère VMA uniquement.

Ces paliers permettent donc de modifier les positions relatives des repères et de développer une spécialisation d'intensité.

### 3.10.3. Choix intensif / extensif

La lecture active des choix de progression est :

- **Intensif** : faire progresser l'intensité, en déplaçant le repère ciblé vers une dépense énergétique supérieure.
- **Extensif** : améliorer le temps de maintien, en diminuant la consommation de soutenabilité associée à une dépense donnée.

Cette distinction remplace l'ancienne explication en termes de « vitesse » et « économie » lorsqu'elle conduisait à réintroduire une coordonnée vitesse dans le modèle. Les incréments et leurs conditions restent à calibrer.

## 3.11. Portefeuille, éligibilité et acquisition

Le catalogue général, les options éligibles et le portefeuille acquis sont trois ensembles distincts.

1. Le catalogue définit les options possibles.
2. La progression rend certaines options éligibles.
3. Le joueur choisit explicitement lesquelles acquérir.
4. Une option acquise devient disponible durablement pour composer les programmes ultérieurs.

L'éligibilité n'est pas une acquisition automatique. Les options éligibles mais non acquises restent candidates.

Deux voies de progression sont envisagées :

- **Voie locale** : les jalons EF, Seuil et VMA ouvrent des options avancées de la filière correspondante.
- **Voie globale** : une progression générale ouvre progressivement les familles transversales, notamment SL et SPEC.

La voie locale ne doit pas permettre à un développement EF de débloquer automatiquement une option avancée VMA, ou inversement. L'acquisition ne doit pas introduire une seconde monnaie dédiée : les conditions de jalon et le choix du joueur suffisent à structurer cette progression.

**OPEN :** définition du développement global, seuils de jalons, cadence d'acquisition, nombre d'options et contreparties éventuelles. Aucun seuil observé dans un harness ne doit être repris comme règle sans décision.

## 3.12. SL et SPEC

SL (sortie longue) et SPEC (spécifique) ne sont pas de nouvelles filières physiologiques fondamentales.

- **SL** représente une préparation d'endurance longue, susceptible d'apporter des adaptations spécifiques de durabilité et une pénibilité propre.
- **SPEC** représente une préparation ciblée et transversale, qui peut caractériser différentes séances plutôt que constituer une cinquième capacité physiologique obligatoire.

Elles sont financées par les budgets existants et peuvent prendre la forme de variantes ou spécialisations de séances EF, Seuil ou VMA.

Leur contribution à la Race doit être réelle et lisible. Aucun bonus générique, aucune cinquième énergie et aucun effet automatique de course ne sont validés.

**OPEN / LATER :** définition de la matrice SL/SPEC, de leur progression globale, de leurs effets exacts sur la courbe énergie–soutenabilité et de leur articulation avec la course cible. SPEC est OPEN / NOT IMPLEMENTED dans le chemin actif.

## 3.13. Limites de répétition

Aucune limite uniforme n'est imposée à tout le catalogue.

Une limite peut être définie au niveau d'une séance ou d'une famille lorsque sa nature sportive le justifie. Les répétitions doivent d'abord être régulées par les coûts, la fatigue, la pénibilité et les rendements décroissants.

Une limite d'une occurrence de SL par tour est une candidate cohérente à tester, mais ne doit pas être étendue automatiquement à toutes les séances.

## 3.14. Fatigue et surentraînement

La fatigue combine au moins deux contributions distinctes :

- fatigue issue du résultat des dés ;
- fatigue spécifique des séances effectivement réalisées.

La fatigue issue des dés est calculée avant les séances et reste acquise en cas de bust. La fatigue spécifique n'est ajoutée que pour les séances réussies.

Le surentraînement doit produire une régulation progressive et lisible du joueur :

- à l'entrée dans un premier état de surentraînement, Add et Add + Reroll deviennent indisponibles ;
- Reroll reste possible ;
- dans un état sévère, un dé est perdu au tour suivant ;
- la sortie de l'état se fait automatiquement lorsque la fatigue repasse sous le seuil correspondant.

Le seuil est lié à la meilleure taille de dé du pool, mais les valeurs exactes, les paliers et la borne supérieure de fatigue restent OPEN. Ces effets définissent une architecture de règle ; ils ne sont pas encore une calibration validée.

Les blessures persistantes, la nutrition et d'autres systèmes de récupération sont LATER.

## 3.15. Taper et fatigue résiduelle

Le dernier tour peut être consacré à un taper facultatif : le joueur réduit volontairement son investissement afin de limiter la fatigue résiduelle avant la course.

Il n'existe pas de variable de fraîcheur indépendante validée. L'état de fatigue à la fin du Training constitue la donnée de départ pour déterminer l'affûtage en Race.

La fonction précise reliant fatigue résiduelle, pool de dés et palier d'affûtage reste à intégrer et à vérifier dans le chemin complet.

---

# 4. Race — maximiser l'énergie sous contrainte de soutenabilité

## 4.1. Principe

Race met à l'épreuve le profil construit pendant Training. À chaque secteur, le joueur choisit quelle quantité d'énergie mobiliser à partir des résultats de son pool de dés.

La performance est la somme des énergies réellement dépensées. La contrainte n'est plus une conversion en vitesse : elle est la consommation de soutenabilité associée à ces dépenses.

~~~text
Score de course = somme des énergies réellement dépensées
Consommation totale = somme des coûts de soutenabilité associés aux secteurs
~~~

Le joueur cherche à maximiser son score tout en évitant d'épuiser trop tôt sa capacité à soutenir l'effort.

## 4.2. Dépense par secteur

La mécanique de dés Race conserve les décisions suivantes comme base :

1. lancer l'intégralité du pool ;
2. effectuer les relances individuelles disponibles ;
3. choisir librement le sous-ensemble de dés dépensé ;
4. accepter qu'une sélection vide produise zéro énergie et zéro point.

Les dés non sélectionnés ne sont pas conservés : le pool complet est relancé au secteur suivant.

L'énergie dépensée est la somme des faces sélectionnées, plafonnée à VMA. VMA est le plafond de dépense par secteur. Une dépense brute supérieure à VMA est donc écrêtée.

Le score du secteur est égal à cette énergie réellement dépensée. Il n'existe pas de vitesse intermédiaire nécessaire au calcul du score.

## 4.3. Coût de soutenabilité d'un secteur

Pour chaque secteur, la dépense réelle E détermine un coût de base S(E), lu directement sur la carte de soutenabilité du profil. L'énergie réelle est la somme des dés sélectionnés après écrêtage à VMA ; c'est cette valeur, et non la somme brute avant écrêtage, qui détermine le score et le coût.

- Le coût minimal est 1, au niveau EF et sur les éventuels plateaux de la zone basse.
- Le coût augmente par paliers entiers dans la zone basse puis dans la zone haute.
- Le coût maximal de base est 13 à VMA.

Une RA peut réduire de 1 le coût d'un secteur couru exactement à l'énergie de l'AS correspondante, sans passer sous 1. La dégradation liée à la fatigue de course augmente ensuite le coût par lecture décalée de la courbe (section 4.4).

La consommation C d'un secteur est le coût effectivement payé après application du décalage de fatigue et, le cas échéant, de la réduction RA. La consommation totale C est la somme des coûts effectivement payés.

## 4.4. Crédit initial, forme du jour et dégradation par fatigue

La comptabilité de course distingue le crédit initial préparé pendant Training (S0), les effets des cartes de forme du jour (F) et la consommation réellement payée sur les secteurs (C) :

~~~text
Solde de soutenabilité = S0 + F − C
C = somme des coûts de secteur effectivement payés
~~~

La forme du jour modifie le crédit disponible. Les cartes révélées au début d'un secteur s'appliquent selon leur calendrier. S0 et les valeurs exactes des effets F restent à définir/calibrer.

**DECISION VALIDATED — forme de la dégradation :** la fatigue de course ne modifie pas le profil physiologique stocké. Elle applique un décalage temporaire de k énergies vers la gauche :

~~~text
Coût de base fatigué(E, k) = S(E + k)
k ∈ {0, 1, 2}
~~~

Le joueur lit la carte existante à E + k. Il n'y a pas de nouvelle courbe ni de +1 uniforme sur S. Cette règle épargne le plateau bas et pénalise davantage les dépenses proches des limites. Les énergies supérieures à VMA − k sont interdites lorsque k > 0.

**DECISION VALIDATED — déclenchement de base :** l'option A, par bandes du stock de soutenabilité dépensé, est retenue :

- k = 0 tant que la moitié du stock de référence n'a pas été consommée ;
- k = 1 à partir de 50 % consommés ;
- k = 2 à partir de 75 % consommés ;
- un nouveau niveau de k prend effet au début du secteur suivant celui qui franchit le seuil.

Le dénominateur exact du stock de référence, notamment le traitement des cartes F révélées progressivement, doit être fixé avec S0 avant implémentation. La progression de k est non réversible dans cette règle de base.

La dette de fatigue réversible (option B) est conservée comme variante avancée, non active. Le déclenchement par nombre de secteurs consécutifs au-dessus du Seuil (option C) n'est pas retenu.

Le coût d'un secteur est lu à S(E + k), puis réduit éventuellement de 1 si une RA est dépensée à cette AS, avec un plancher final de 1. Cette valeur alimente C et le solde S0 + F − C.

Exemple : si S(18) = 4, alors une fatigue k = 1 porte le coût de base à S(19) = 5 et k = 2 à S(20) = 6. Une RA dépensée à l'énergie 18 réduit le coût effectivement payé d'un point, sans descendre sous 1. Si k = 2, toute dépense supérieure à VMA − 2 est interdite.

**OPEN :** construction de S0, définition du stock de référence et articulation exacte avec F, conséquence mécanique d'un solde négatif et traitement du reliquat à l'arrivée.

## 4.5. Forme du jour — structure héritée, calibrage expérimental

Le modèle de forme du jour retenu dans Race V2 utilise trois dés à six faces dédiés, indépendants du pool d'entraînement. Leur somme détermine un niveau :

| Somme des 3d6 | Niveau |
|---:|---|
| 3–5 | Difficile |
| 6–8 | Moyenne |
| 9–12 | Bonne |
| 13–15 | Excellente |
| 16–18 | Exceptionnelle |

Chaque niveau détermine une recette de trois cartes tirées de paquets catégoriels Excellent, Bon, Moyen et Mauvais.

| Forme | Recette |
|---|---|
| Exceptionnelle | Excellent, Excellent, Bon |
| Excellente | Excellent, Bon, Bon |
| Bonne | Bon, Bon, Moyen |
| Moyenne | Bon, Moyen, Mauvais |
| Difficile | Moyen, Mauvais, Mauvais |

Le joueur connaît les catégories, mais pas les valeurs ni l'ordre de révélation. Les cartes sont mélangées face cachée et révélées progressivement au début des secteurs indiqués.

Les anciennes distributions de paquets (15 cartes par catégorie, valeurs de +2 à −2) et les calendriers de révélation sont des paramètres EXPERIMENTAL issus de Race V2. Ils peuvent être conservés comme fixtures de départ, mais leur équilibre doit être réévalué avec le score énergie et la nouvelle courbe de soutenabilité.

## 4.6. Découpage de course

Le prototype Race V2 utilise les longueurs suivantes :

| Course | Secteurs |
|---|---:|
| 5 km | 7 |
| 10 km | 10 |
| Semi-marathon | 13 |
| Marathon | 16 |

Ces longueurs constituent le découpage de référence du prototype, pas encore une validation de durée ou d'équilibrage avec le nouveau score.

## 4.7. Dés et relances en Race

Le joueur lance tous les dés de son pool à chaque secteur. Il peut relancer les dés individuellement, un à la fois.

- Chaque relance remplace le résultat précédent du dé concerné.
- Un même dé peut être relancé plusieurs fois si le capital le permet.
- Il n'y a pas de relance après le choix du sous-ensemble dépensé.
- L'action Add n'existe pas en Race.
- Les dés non dépensés sont relancés au secteur suivant.

Le capital de relance est global à la course, sans régénération. Le reliquat est perdu à l'arrivée.

La référence Race V2 attribue au 5 km un capital maximal dépendant du plus haut dé :

| Plus haut dé | Capital de référence 5 km |
|---|---:|
| D6 | 1 |
| D8 | 2 |
| D10 | 3 |
| D12 | 4 |

Pour une course de N secteurs, la formule de référence est :

~~~text
R = ceil(Rmax_5km × (N / 7) × P_affûtage)
~~~

Le coefficient d'affûtage vaut 0, 0,25, 0,50, 0,75 ou 1 selon le palier 0 à 4.

Cette mécanique de capital est indépendante de la conversion énergie–vitesse et peut être conservée comme base de travail. Son équilibre doit néanmoins être testé avec le nouveau score énergie.

## 4.8. Affûtage

L'affûtage dépend de la fatigue résiduelle à la fin du Training. Le modèle Race V2 précédent définit cinq paliers et des seuils dépendant du plus haut dé du pool. Entre deux seuils, le palier inférieur s'applique.

Les seuils de référence consignés dans RACE_V2_DESIGN.md sont :

| Plus haut dé | 0 % | 25 % | 50 % | 75 % | 100 % |
|---|---:|---:|---:|---:|---:|
| D6 | 0 | −2 | −3 | −4 | −6 |
| D8 | 0 | −2 | −4 | −6 | −8 |
| D10 | 0 | −4 | −6 | −8 | −10 |
| D12 | 0 | −6 | −8 | −10 | −12 |

Ces seuils sont conservés comme référence de conception antérieure. Leur compatibilité avec la fatigue Training B et la nouvelle courbe énergie–soutenabilité doit être vérifiée avant de les traiter comme définitivement intégrés.

## 4.9. Groupes et coopération en course

La Race V2 précédente regroupait les joueurs selon les écarts entre scores cumulés successifs. Le ou les joueurs en tête de chaque groupe devenaient lièvres ; les autres bénéficiaient d'une aspiration au secteur suivant.

Le principe d'une interaction positive et opportuniste entre joueurs reste cohérent avec la vision du jeu. En revanche, l'ancien calcul reposait sur un score de vitesse et un bonus de +1 énergie virtuelle utilisé uniquement pour la conversion. Cette règle ne peut pas être transposée telle quelle lorsque l'énergie dépensée devient directement le score.

**À conserver comme principe :**
- les joueurs peuvent se retrouver dans des groupes ;
- le classement peut être utilisé pour déterminer des rôles de lièvre et de suiveur ;
- l'interaction doit créer des décisions tactiques sans remplacer le choix de dépense individuelle.

**OPEN :**
- score cumulatif exact utilisé pour constituer les groupes ;
- règle de séparation entre groupes ;
- effet concret du rôle de lièvre ou du bénéfice d'aspiration ;
- coût éventuel de cet effet en soutenabilité ;
- traitement du premier secteur et des égalités.

Aucun bonus gratuit au score n'est validé dans le nouveau modèle.

## 4.10. Terrain

Dans l'ancien Race V2, le terrain modifiait l'énergie de conversion avant lecture de la vitesse, sans modifier la dépense réelle ni la consommation de soutenabilité.

Cette fonction dépendait de la conversion énergie → vitesse et est donc supersédée.

Le terrain peut rester un facteur de difficulté locale, mais sa traduction dans le modèle énergie–soutenabilité doit être définie. Il ne doit pas créer d'énergie dépensée gratuitement ni modifier le score sans règle explicite.

**OPEN :** déterminer si le terrain agit sur le coût de soutenabilité, sur une contrainte de dépense, sur un effet de groupe ou sur un autre paramètre ; ne pas réintroduire une énergie virtuelle de conversion par simple héritage.

## 4.11. Ordre de résolution cible d'un secteur

La séquence générale conservée est :

1. révéler les éventuelles cartes de forme prévues au début du secteur ;
2. actualiser le crédit de soutenabilité disponible ;
3. afficher les informations tactiques du secteur qui sont déjà déterminées ;
4. lancer l'intégralité du pool de dés ;
5. effectuer les relances individuelles disponibles ;
6. choisir librement le sous-ensemble de dés dépensé ;
7. calculer l'énergie réelle, plafonnée à VMA ;
8. ajouter cette énergie au score ;
9. calculer la consommation de soutenabilité associée à cette dépense ;
10. actualiser le solde pour les secteurs suivants ;
11. actualiser les groupes et informations tactiques pour le secteur suivant.

Cette séquence décrit la structure cible. Les étapes relatives au terrain et aux groupes restent incomplètes tant que leurs effets n'ont pas été redéfinis dans le modèle énergie–soutenabilité.

---

# 5. Intégration Training → Race

## 5.1. Principe

La configuration Race doit être dérivée de façon déterministe de l'état final réel de Training B. Une configuration saisie manuellement par le prototype ne constitue pas une intégration.

Le passage doit transmettre au minimum :

- les trois repères physiologiques EF / Seuil / VMA dans le domaine énergétique ;
- la courbe énergie–soutenabilité ;
- le crédit initial de soutenabilité S0 ;
- la taille et la composition du pool de dés ;
- la fatigue résiduelle et le palier d'affûtage qui en découle ;
- les effets de préparation transversale qui auront été explicitement définis.

## 5.2. Entrées qui ne sont plus nécessaires comme variables de jeu

Le modèle actuel n'exige plus :

- une table physiologique énergie → vitesse ;
- un score fondé sur des vitesses entières ;
- une soutenabilité indépendante stockée pour chaque AS ;
- une AS comme seuil de calcul de la consommation de base ;
- une conversion automatique des vitesses VDOT en valeurs de jeu.

Les énergies AS42 / AS21 / AS10 / AS5 et leurs RA font en revanche partie de la couche de spécialisation de course et doivent être transmises lorsqu'elles sont utilisées.

Les distances de course restent des paramètres de scénario. Elles peuvent orienter le catalogue de préparation sans créer automatiquement une coordonnée physiologique supplémentaire.

## 5.3. Éléments à définir

| ID | Élément | Travail requis | Statut |
|---|---|---|---|
| E1 | Profil énergétique | Définir les valeurs initiales EF / Seuil / VMA et les règles de progression depuis Training | PARTIELLEMENT DÉFINI — initialisation et intégration OPEN |
| E2 | Courbe énergie–soutenabilité | Construire les cartes depuis les ancres 1–5–13 et les largeurs n/m ; raccorder les adaptations intensives / extensives | DESIGN VALIDATED — construction définie ; raccord Training OPEN |
| E3 | Crédit S0 | Définir la contribution du Training au crédit initial de soutenabilité | OPEN |
| E4 | Allures spécifiques | Transmettre les énergies AS et leurs réserves d'allure | DESIGN VALIDATED — règles de spécialisation définies ; valeurs initiales et intégration OPEN |
| E5 | Pool de dés | Transmettre les dés réellement acquis et améliorés | IMPLEMENTATION GAP |
| E6 | Affûtage | Déduire le palier de la fatigue résiduelle et du pool de dés | IMPLEMENTATION GAP |
| E7 | Préparations transversales | Définir les effets Race de SL et SPEC s'ils sont retenus | OPEN / LATER |

Le modèle de courbe et sa lecture sont définis dans le GDD. Le mapping des adaptations Training vers les ancres et vers les évolutions extensives reste à spécifier. L'ancienne table énergie–vitesse et l'AS comme seuil de calcul de la consommation de base ne sont plus des besoins du modèle actif ; les AS/RA sont en revanche des données de spécialisation à transmettre.

---

# 6. État du projet et limites de l'implémentation

## 6.1. Training B

**CURRENT IMPLEMENTATION :**

- Training B est la base active du prototype ;
- le prototype est monoposte et en terminal, pas un jeu multijoueur ou graphique ;
- un pool de dés persistant, les décisions de dés, les budgets et des résolutions de séances existent sous forme de briques ;
- le catalogue, les adaptations, les jalons et la fatigue sont encore partiellement configurés par des fixtures expérimentales ;
- les seuils d'acquisition et le calendrier de progression ne sont pas entièrement définis ;
- la courbe énergie–soutenabilité n'est pas encore un système complet intégré.

Le chemin de résolution par budgets et doses est la cible. L'ancien chemin direct qui affectait des dés aux séances est historique et ne constitue pas une cible de compatibilité.

## 6.2. Race

**CURRENT IMPLEMENTATION :**

Le prototype isolé dans experiments/current/race_v2_prototype/ comprend :

- une orchestration multi-secteur ;
- les distances 5 km / 10 km / semi-marathon / marathon ;
- le lancer complet du pool ;
- les relances individuelles ;
- la sélection libre d'un sous-ensemble de dés, y compris vide ;
- un capital global de relance ;
- une forme du jour et des cartes ;
- un bilan de soutenabilité ;
- des groupes et une aspiration issus de l'ancien score vitesse ;
- une résolution en deux phases avec validation des décisions.

Ce prototype implémente encore le modèle énergie–vitesse antérieur. Il ne doit pas être présenté comme une implémentation du nouveau modèle énergie–soutenabilité.

## 6.3. Absence de boucle complète

Aucune boucle complète Training B → Race n'est revendiquée.

La configuration Race est encore fournie explicitement. Le dépôt ne dérive pas automatiquement l'ensemble des entrées Race depuis un état Training B réel.

L'intégration doit attendre la définition des coordonnées énergétiques, de la courbe de soutenabilité, de S0 et de la relation entre fatigue résiduelle et affûtage.

## 6.4. Pause d'implémentation

Le DEVELOPMENT_PLAN.md indique une pause d'implémentation après PR #67, avec priorité à la consolidation documentaire. La présente refonte est un travail de design et de documentation.

Aucun code, test, harness ou résultat de simulation n'est modifié par cette consolidation. La reprise de l'implémentation, du mapping Training → Race ou d'un calibrage demande une instruction distincte.

---

# 7. Équilibrage, preuves et expérimentation

## 7.1. Principe

Les expériences servent à répondre à une question définie, pas à choisir automatiquement les règles à la place du joueur.

Chaque rapport doit distinguer :

- **FACT** : propriété directement vérifiée dans le dépôt ou dans une équation ;
- **RESULT / OBSERVATION** : résultat effectivement mesuré ;
- **INTERPRETATION / HYPOTHESIS** : explication plausible, avec ses limites ;
- **DECISION** : arbitrage de design explicite ;
- **OPEN** : question qui reste à trancher.

Une politique automatique n'est pas un joueur humain standard. Une trajectoire simulée ne valide pas à elle seule une stratégie. Une expérience reproductible ne valide pas automatiquement l'équilibrage.

## 7.2. Références expérimentales Training

Les dossiers suivants restent des sources de preuves limitées :

- training_v2_minimal : sonde expérimentale des budgets, de la composition, de la progression et des variantes SPEC ;
- training_v2_specific : sonde isolée du rôle de SPEC et de certaines conventions de course ;
- training_b_trajectory : trajectoires de 16 tours sous heuristiques EF / Qualité / équilibrée ;
- training_allocation_harness : comparaison D / P / H, qui a motivé la direction hybride compartiments puis catalogue ;
- training_h_full_turn : prototype déterministe de transitions de tour et d'état.

Leurs seuils, poids de politiques, valeurs de séances, résultats et choix de scénarios restent expérimentaux lorsqu'ils sont explicitement qualifiés comme tels dans leurs README ou rapports.

En particulier, les trajectoires Training B ont mis en évidence que la fatigue cumulée ne contraignait pas encore automatiquement les dés disponibles au tour suivant. Elles ne valident donc pas la régulation longitudinale de la charge.

## 7.3. Références expérimentales Race

- race_v2_prototype : prototype multi-secteur de l'ancien modèle Race V2 ;
- race_engine_v2 : ancien moteur Production / Difficulty / Curve A-B-C, historique pour le modèle Race actuel ;
- training_race_bridge : sonde synthétique fondée sur l'ancien moteur et sur des hypothèses SPEC ;
- race_efficiency_probe : sonde analytique isolée de conventions SPEC / Efficacité.

Aucun résultat de ces sondes ne doit être interprété comme une validation de la courbe énergie–soutenabilité actuelle.

## 7.4. Calibration prioritaire

Avant une campagne de simulation importante, privilégier :

1. une formalisation de la courbe énergie–soutenabilité ;
2. des scénarios déterministes autour de EF, Seuil et VMA ;
3. la vérification des transformations intensives et extensives ;
4. la cohérence entre les adaptations Training et les coûts de Race ;
5. la vérification du solde de soutenabilité et de ses conséquences ;
6. une première boucle Training → Race sur quelques profils contrastés ;
7. des tests avec joueurs pour évaluer lisibilité, décisions et durée.

Une campagne Monte-Carlo massive, un solver complet ou une politique automatique avancée sont différés tant que le modèle de base et son intégration ne sont pas stabilisés.

---

# 8. Questions ouvertes et décisions à prendre

Cette section ne répète pas les décisions déjà fixées dans les sections 2 à 5. Elle ne contient que les paramètres, arbitrages ou raccords qui demandent encore un travail explicite.

## 8.1. Modèle physiologique et progression

1. Quelles valeurs initiales d'énergie EF / Seuil / VMA sont attribuées aux profils de départ ?
2. Comment les jauges Training déclenchent-elles les progressions d'ancre et les choix intensif / extensif dans le cadre des contraintes n/m ?
3. Comment une adaptation extensive se traduit-elle précisément dans les ancres et les cartes, sans stocker une seconde courbe indépendante ?
4. Comment propager une hausse d'ancre aux AS voisines tout en maintenant leur ordre, sans palier gratuit ?
5. La limite de cinq paliers par AS et la séquence de seuils 10–12–15–19–24–30 doivent-elles être confirmées telles quelles ?
6. La vérification exhaustive des invariants confirme-t-elle tous les passages de profils autorisés ?

## 8.2. Training

1. Quels événements accordent un dé supplémentaire ou une amélioration de dé, et à quelle cadence ?
2. Quels sont les seuils d'XP des trois filières et les incréments exacts des paliers ?
3. Quelle règle calcule le RPE autorisé à partir du tour et des dés ?
4. Quelles sont les valeurs de RPE et de fatigue de chaque séance ?
5. Quelle est la matrice complète des adaptations primaires et secondaires ?
6. Quels seuils déclenchent les états de surentraînement ?
7. Quel est le calendrier de déblocage et d'acquisition du portefeuille ?
8. Comment définir la progression globale ouvrant SL et SPEC ?
9. Quelle est la limite spécifique éventuelle de répétition pour chaque séance ?

## 8.3. Race

1. Comment calculer S0 à partir de Training ?
2. Quel est le stock de référence exact pour les seuils de dégradation à 50 % et 75 %, et comment les effets F révélés progressivement y contribuent-ils ?
3. Quelle conséquence exacte produit un solde de soutenabilité négatif : restriction immédiate, impossibilité de dépenser ou autre règle ?
4. Quel score cumulatif et quelle règle de groupe produisent les interactions les plus lisibles avec le score énergie ?
5. Quel effet de course remplace l'ancienne aspiration virtuelle ?
6. Comment le terrain intervient-il sans réintroduire une conversion énergie–vitesse ?
7. Le capital de relance et les paliers d'affûtage restent-ils équilibrés avec le score énergie ?
8. Le nombre de secteurs est-il adapté au rythme de décisions du nouveau modèle ?

## 8.4. Expérience et intégration

1. Comment dériver de façon déterministe les ancres, les AS/RA, le profil de dés, S0 et l'affûtage depuis un état Training B réel ?
2. Quelle télémétrie minimale permet de comprendre les arbitrages de dépense et de soutenabilité, notamment les effets de k et de RA ?
3. Quel scénario déterministe valide la chaîne Training → Race avant toute simulation longue ?
4. Quelle durée réelle obtient-on avec 2 à 4 joueurs ?

# 9. Historique des modèles remplacés

Cette section conserve les principaux changements de cap afin d'éviter de réintroduire involontairement des règles anciennes.

## 9.1. Training CURRENT historique

L'ancien Training reposait notamment sur :

- CTL et ses seuils d'ajout de dés ;
- D99 comme plafond de qualités planifiables ;
- un quota Qualité ≤ EF ;
- RPE Max et des tests de bust propres à cet ancien catalogue ;
- une fatigue V1 composée de Q, Recovery et S ;
- une redistribution EF après bust ;
- un chemin de simulation persistant dans simulate_player.py.

Ces règles ont été utiles pour les audits et les prototypes antérieurs, mais le Training B est la cible. Elles ne doivent pas être réintroduites dans le modèle actif sans décision explicite.

## 9.2. Ancienne Race énergie–vitesse

Le modèle Race V2 du 12 novembre utilisait :

- trois repères EF / Seuil / VMA avec coordonnées énergie et vitesse ;
- une table entière de conversion énergie → vitesse ;
- un point AS propre à la distance ;
- un score égal à la somme des vitesses ;
- une consommation de soutenabilité calculée par rapport à l'AS ;
- un décalage horizontal de la courbe en cas de déficit de soutenabilité ;
- un bonus d'aspiration utilisé uniquement dans la conversion ;
- une difficulté de terrain appliquée à l'énergie de conversion.

La proposition du 14 novembre supprime la vitesse comme dimension indépendante et fait de l'énergie dépensée le score. La soutenabilité devient le coût de maintien de cette dépense. Les anciennes règles de conversion, d'AS, de terrain et d'aspiration doivent donc être redéfinies avant d'être reprises.

## 9.3. Anciennes réserves et expériences SPEC

RACE_RESERVE_DESIGN.md est historique et supersédé comme modèle de réserve Race par la comptabilité S0 + F − C.

Les expériences Position / Efficacité / SPEC restent des sondes de conception isolées. Elles ne définissent pas le modèle physiologique actuel et ne valident pas une cinquième filière.

## 9.4. Anciennes références de vitesse

La décision du 14 novembre sur une unité interne de vitesse égale à 0,5 km/h et les profils P8–P15 a été documentée dans PHYSIOLOGICAL_SPEED_REFERENCE_PROFILES.md et dans la PR #71.

Cette décision répondait à l'ancien modèle énergie–vitesse. Elle est conservée pour l'historique et pour les références sportives, mais elle ne doit plus être utilisée comme coordonnée du modèle énergie–soutenabilité. Les grandeurs d'énergie, de fatigue et de soutenabilité n'ont jamais été concernées par le doublement de l'axe vitesse.

---

# 10. Références documentaires

## Sources de design actives

- README.md — présentation du projet et hiérarchie des documents.
- DEVELOPMENT_PLAN.md — gouvernance, portes, dépendances et pause d'implémentation.
- docs/game-design/TRAINING_B_DECISIONS.md — décisions Training B jusqu'à Q55.
- Présent GDD — consolidation normative du modèle énergie–soutenabilité et des décisions ultérieures.

## Sources d'implémentation

- CURRENT_STATE.md — snapshot du prototype.
- training_v2/README.md — chemin Training B et limites de son implémentation.
- experiments/current/race_v2_prototype/README.md — état et limites du prototype Race multi-secteur.

## Sources expérimentales et historiques

- experiments/current/training_v2_minimal/README.md et REPORT.md.
- experiments/current/training_v2_specific/README.md et REPORT.md.
- experiments/current/training_b_trajectory/README.md.
- experiments/current/training_allocation_harness/README.md.
- experiments/current/training_h_full_turn/README.md.
- experiments/current/training_race_bridge/README.md et REPORT.md.
- experiments/current/race_efficiency_probe/README.md et REPORT.md.
- docs/game-design/RACE_V2_DESIGN.md — règles détaillées de l'ancien modèle Race énergie–vitesse, à ne pas lire comme la spécification du modèle actuel.
- docs/game-design/PHYSIOLOGICAL_SPEED_REFERENCE_PROFILES.md — références sportives et ancienne échelle vitesse.
- docs/game-design/RACE_RESERVE_DESIGN.md — historique du modèle de réserve remplacé.
- D1_TRAINING_WORKING_DESIGN.md — document de travail non normatif, à lire comme trace des hypothèses de conception et non comme GDD.

---

**Principe directeur final :** Run It doit faire émerger une tension lisible entre le niveau de dépense qu'un coureur peut mobiliser, le coût de soutenabilité de cette dépense et le temps pendant lequel il peut la maintenir. Training développe ces dimensions par des décisions intensives et extensives ; Race oblige le joueur à les arbitrer sous incertitude et en interaction avec les autres coureurs.
