# Training B — décisions de conception

> **Statut :** consolidation des réponses et clarifications recueillies jusqu'à Q55, le 10 novembre 2026.  
> **Portée :** référence de conception pour construire la matrice des séances Training B et préparer son intégration avec Race V2.  
> **Nature :** décisions utilisateur, hypothèses provisoires et points ouverts sont distingués. Ce document ne constitue pas une validation de l'équilibrage numérique.

## 1. Principes directeurs

- Training est une phase de **préparation** qui construit le profil physiologique et les spécialisations du coureur.
- Race exploite ce profil préparé. L'ancien modèle Training sera abandonné au profit de Training B ; la compatibilité avec l'ancien moteur n'est pas un objectif.
- Le rapport Training/Race vise une préparation substantielle : environ deux tiers de Training et un tiers de Race, pour une durée totale de partie de l'ordre de 60 à 90 minutes.
- La conception doit rester directement implémentable et testable. Ne pas introduire d'abstractions d'architecture prématurées.
- Le GDD doit distinguer les éléments actuels, expérimentaux, ouverts et les écarts d'implémentation.

## 2. Tour de Training : dés et énergie

### 2.1 Pool de dés

- Le joueur commence avec **4 dés** et peut progresser jusqu'à **6 dés**.
- Les dés peuvent être améliorés individuellement de **d6 à d8, d10 puis d12**.
- Le joueur choisit librement quel dé améliorer ; l'amélioration n'est pas automatiquement appliquée au plus petit dé.
- Le pool peut recevoir des dés supplémentaires jusqu'à un maximum de 6.
- Les événements/jalons qui accordent un dé ou une amélioration, ainsi que leur calendrier, restent **OPEN**. Aucun seuil expérimental de l'ancien moteur ne constitue une règle validée.

### 2.2 Lancer et choix du joueur

Au début du tour, le joueur lance **N−1 dés**. Il choisit ensuite une seule opération :

1. **Keep** : conserver les résultats obtenus ;
2. **Reroll** : relancer un dé déjà lancé ;
3. **Add** : lancer le dé restant ;
4. **Add + Reroll** : relancer un dé déjà lancé puis lancer le dé restant.

Les résultats finaux de tous les dés sont conservés pour le calcul du tour. L'énergie disponible est la somme des résultats finaux.

### 2.3 Fatigue issue des dés et TN

- Le TN représente la somme attendue du pool complet de dés.
- La rétroaction des dés conserve la **courbe quasi-Fibonacci historique** du prototype ; elle n'est pas remplacée par une variation linéaire `somme finale − TN`.
- L'écart `somme finale − TN` est arrondi à l'entier supérieur avant d'être converti par cette courbe. Le TN reste calculé à partir de l'espérance du pool complet, même s'il est fractionnaire.
- La contribution de fatigue issue des dés peut être positive (charge), nulle ou négative (récupération), selon la courbe historique.
- La fatigue cumulée reste entière et ne peut pas descendre sous zéro.
- Cette variation est calculée après l'opération de dés, avant de résoudre les adaptations de séance.
- La fatigue calculée est conservée même si le joueur fait un bust.

> **Décisions confirmées le 11 novembre 2026 :** conserver la courbe quasi-Fibonacci historique et arrondir l'écart au TN à l'entier supérieur avant consultation de la courbe. Le TN est la somme des espérances de chaque dé. Les seuils d'overtraining restent ouverts.

## 3. Économie du tour : budgets EF et Qualité

- L'énergie du tour est la somme des résultats finaux des dés.
- Le joueur répartit librement cette énergie entre deux budgets :
  - **budget EF** ;
  - **budget Qualité**.
- Le budget Qualité est ensuite réparti librement entre **Seuil** et **VMA**.
- Il est possible d'investir dans Seuil et VMA au cours du même tour.
- Chaque budget peut être réparti entre plusieurs séances d'une même filière pendant le tour.
- Il n'existe pas de mécanique distincte de « surplus d'énergie ».
- Les anciennes règles d'excès de Qualité par rapport à EF ne font pas partie du modèle retenu.
- CTL est supprimé de Training B et ne doit pas servir de variable externe de préparation dans la nouvelle intégration Race.

## 4. Catalogue de séances et dose

### 4.1 Catalogue de base

Les entrées de catalogue initiales sont des séances distinctes, chacune correspondant à une dose précise :

| Filière | Séances de base |
|---|---|
| EF | EF1, EF2, EF3, EF4 |
| Seuil | Seuil3, Seuil4, Seuil5 |
| VMA | VMA3, VMA4, VMA5 |

- Le chiffre représente la **dose investie**, c'est-à-dire le coût exact en points du budget correspondant.
- Ce chiffre ne représente ni une capacité physiologique, ni une adaptation, ni le RPE.
- Chaque dose est une entrée de séance distincte ; ce n'est pas une séance unique à coût variable.
- Les séances peuvent être débloquées par la progression globale et, pour certaines séances spécialisées, par des prérequis physiologiques.

### 4.2 Adaptations

- Chaque séance possède une filière d'adaptation principale et une filière secondaire.
- Les quantités d'adaptation principale et secondaire sont définies indépendamment pour chaque séance ; aucune proportion universelle n'est imposée.
- L'adaptation dépend de la séance et de sa dose. Le résultat des dés n'en modifie pas directement la quantité, hors réussite ou bust.
- Un bust annule l'adaptation de la séance concernée, mais ne supprime pas la fatigue déjà calculée à partir des dés.
- Les adaptations sont accumulées dans des réserves/XP distinctes pour EF, Seuil et VMA.
- Lorsqu'un palier est atteint, le coût requis est consommé et le surplus d'XP est conservé.
- Les seuils de progression sont indépendants entre filières et de plus en plus espacés pour matérialiser les rendements décroissants.
- Certaines séances peuvent également avoir leurs propres rendements décroissants en fonction de la dose ; ce traitement est défini au cas par cas, pas par une formule universelle.

### 4.3 RPE, bust et fatigue de séance

- Le RPE caractérise la difficulté intrinsèque de la séance et sert d'indicateur de son potentiel d'adaptation.
- Le mécanisme de bust repose sur le **meilleur dé du pool**, comparé au dépassement de RPE autorisé par rapport au RPE de la séance.
- La fatigue produite par une séance dépend à la fois de son RPE et de sa dose. Sa fonction peut varier selon la séance.
- La fatigue issue des dés (écart au TN) et la fatigue produite par les séances sont deux contributions distinctes.

### 4.4 Limites de répétition

- Des limites peuvent exister au niveau d'une séance précise et/ou d'une famille de séances.
- Ces limites sont définies au cas par cas ; aucune limite uniforme n'est imposée à tout le catalogue.

## 5. Overtraining

- Plusieurs niveaux/seuils de fatigue structurent l'overtraining.
- Le seuil d'entrée est lié à la meilleure valeur de dé du pool ; un seuil plus élevé déclenche un état plus sévère.
- En début d'overtraining :
  - **Add** et **Add + Reroll** deviennent indisponibles ;
  - **Reroll** reste possible.
- En overtraining sévère, le joueur perd un dé au tour suivant.
- La sortie de l'état d'overtraining est automatique lorsque la fatigue repasse sous le seuil correspondant.
- La fatigue calculée à partir des dés reste acquise même en cas de bust.

> **Ouvert :** valeurs numériques des seuils, articulation précise avec la meilleure face de dé et éventuel effet supplémentaire sur le budget disponible.

## 6. SL et SPEC : préparation de course transversale

- **SL** (sortie longue) et **SPEC** (spécifique) sont des familles transversales, pas de nouvelles filières physiologiques.
- Elles sont financées par les budgets existants et peuvent être des variantes ou spécialisations de séances EF/Seuil/VMA.
- Elles contribuent à la préparation de Race :
  - préparation générale et fraîcheur ;
  - bonus contextuels selon la distance ou le profil de la course cible.
- Leurs bénéfices sont conservés jusqu'à la course ; il n'y a pas de décroissance automatique.
- Le joueur choisit une course cible au début de la partie, avant le Training. La cible comprend la distance et éventuellement le profil du parcours.
- La course cible ne peut pas être changée en cours de partie.
- Le nombre de tours de Training dépend de la distance cible et du scénario. Tous les joueurs d'un même scénario ont le même nombre de tours.
- Le dernier tour peut être consacré à un taper facultatif : le joueur réduit volontairement son investissement pour favoriser la récupération/fraîcheur.
- Le bonus de fraîcheur en Race dépend du niveau de fatigue à la fin du Training ; il n'existe pas de variable de fraîcheur indépendante.
- La formule du bonus de Race reste à calibrer. Une relation continue avec plafond a été évoquée comme hypothèse, pas validée.

## 7. Progression physiologique et spécialisations

### 7.1 Valeurs de départ

Valeurs provisoires reprises du prototype :

| Filière | Valeur initiale |
|---|---:|
| EF | 6 |
| Seuil | 8 |
| VMA | 10 |

Ces valeurs sont conservées provisoirement, puis recalibrées avec la matrice et les scénarios.

### 7.2 Courbe physiologique énergie / vitesse

EF, Seuil et VMA sont trois points d'une même courbe de conversion énergie → vitesse. Chaque point possède deux coordonnées :

- **Énergie** : dépense nécessaire au niveau de vitesse correspondant.
- **Vitesse** : vitesse accessible à cette dépense.

L'ordre doit être strict sur les deux axes :

~~~text
E(EF) < E(Seuil) < E(VMA)
V(EF) < V(Seuil) < V(VMA)
~~~

L'énergie du point VMA constitue le maximum d'énergie dépensable en Race. Les valeurs initiales 6 / 8 / 10 restent des valeurs provisoires de l'ancien prototype et ne suffisent pas à définir les six coordonnées de la nouvelle courbe.

### 7.3 Progression physiologique par paliers

- Les adaptations de séances alimentent trois réserves d'XP indépendantes : EF, Seuil et VMA.
- Chaque filière possède ses propres seuils de palier, croissants et de plus en plus espacés.
- Lorsqu'une réserve atteint le coût du prochain palier, le joueur choisit **une seule** des deux transformations du point correspondant :
  1. **Vitesse** : augmenter la vitesse sans modifier l'énergie.
  2. **Économie** : diminuer l'énergie sans modifier la vitesse.
- Il n'y a **aucun effet physiologique automatique** au palier.
- Le coût du palier est consommé après le choix ; l'XP excédentaire est conservée pour le palier suivant.
- Une transformation qui romprait l'ordre EF < Seuil < VMA sur l'un des deux axes est interdite.

Les seuils d'XP, les incréments de vitesse et les réductions d'énergie restent à calibrer. Ils sont fournis comme configuration et ne sont pas fixés par le code.

Le système de spécialisations de Race décrit ci-dessous est distinct de cette transformation physiologique ; son articulation exacte avec le nouveau choix de palier reste à confirmer.

### 7.4 Spécialisations

- Les spécialisations sont choisies par le joueur lorsqu'un palier les ouvre.
- Elles sont permanentes et cumulatives jusqu'à la fin de la partie ; il n'y a ni emplacements limités ni remplacement.
- Les options proposées dépendent des séances réalisées pendant le Training.
- Le principe retenu provisoirement est celui de **seuils de pratique** pour rendre une spécialisation accessible. Les seuils numériques et leur métrique exacte ne sont pas définis.
- Une amélioration de spécialisation modifie la **courbe physiologique de Race**.
- Les paramètres de courbe modifiés sont ceux déjà présents dans Race V2, après audit du moteur.
- Les effets de spécialisation se cumulent par addition.
- Une spécialisation ne modifie qu'un seul paramètre de la courbe.
- Les spécialisations ne sont donc pas de simples bonus contextuels indépendants : elles modifient la conversion de l'énergie en production/vitesse via les paramètres de la courbe.

> **Précision importante :** le choix « seuils de pratique » (Q50) est une orientation préférée par l'utilisateur (« plutôt C »), pas encore un arbitrage ferme sur les valeurs ou la métrique de seuil.

## 8. Course cible et calibration Race

- Référence de calibration évoquée : 5 km réalisable à VMA et 10 km au seuil.
- Le découpage exact de la course en segments et les cibles de consommation restent à finaliser.
- La course utilise un budget/réserve énergétique et une courbe physiologique qui convertit la dépense en production/vitesse.
- Le terrain constitue une surcharge locale.
- La forme de course est révélée progressivement et modifie la réserve ; les règles détaillées restent à consolider.
- Les anciens résultats de simulation fondés sur CTL externe, allocation directe des dés aux séances ou anciennes normalisations ne valident pas le nouveau modèle.

## 9. Registre des décisions récentes (Q44–Q55)

| Question | Décision | Statut / précision |
|---|---|---|
| Q44 — valeurs initiales EF/Seuil/VMA | C | Valeurs du prototype conservées provisoirement, puis recalibrées |
| Q45 — effet d'un palier | SUPERSEDED 2026-11-11 | Le palier donne le choix vitesse ou économie sur le point de la filière ; aucun effet physiologique automatique |
| Q46 — nature de la progression automatique | D | Effet propre à chaque filière |
| Q47 — amplitude de l'effet automatique | C | Définie explicitement pour chaque palier |
| Q48 — cumul des spécialisations | A | Toutes permanentes et cumulatives |
| Q49 — accès aux spécialisations | C | Dépend des séances réalisées |
| Q50 — critère de déblocage | Plutôt C | Seuils de pratique ; métrique et valeurs ouvertes |
| Q51 — nature de l'amélioration | Clarification | La spécialisation modifie la courbe physiologique de Race |
| Q52 — partie de courbe modifiable | D | Forme de courbe : seuils, pentes, rendements et transitions |
| Q53 — cumul des modifications | A | Additif |
| Q54 — nombre de paramètres par spécialisation | A | Un seul paramètre |
| Q55 — définition des paramètres | D | Partir des paramètres existants de Race V2 après audit |

## 10. Points ouverts prioritaires

Les points suivants doivent être résolus pour produire une matrice exploitable et implémentable :

1. **Matrice des séances** : pour chaque séance et chaque dose, fixer coûts, RPE, adaptation primaire/secondaire, fatigue, bust autorisé, limites de répétition et rendements décroissants éventuels.
2. **Formule de bust** : formaliser précisément la comparaison entre meilleur dé, RPE de séance et dépassement autorisé.
3. **Fatigue de séance** : fixer les fonctions/valeurs par séance et les interactions avec la fatigue issue des dés.
4. **Overtraining** : fixer les seuils numériques et l'éventuel impact sur le budget d'énergie.
5. **Progression** : fixer les seuils d'XP indépendants EF/Seuil/VMA, les amplitudes des deux transformations proposées à chaque palier et les événements qui accordent un dé supplémentaire ou une amélioration choisie par le joueur.
6. **Spécialisations** : définir les familles de séances contributrices, les seuils de pratique, les options offertes et leur paramètre de courbe modifié.
7. **Race V2** : auditer les paramètres mathématiques réellement présents dans le moteur, vérifier qu'ils permettent les modifications additives à un paramètre, puis définir les effets des spécialisations.
8. **SL/SPEC** : définir les séances/variantes, les conditions d'accès et les effets sur la préparation générale ou contextuelle.
9. **Taper et fraîcheur** : calibrer le lien entre fatigue finale du Training et bonus de Race.
10. **Scénarios** : définir les durées de Training selon la course cible et valider la progression par simulations.

## 11. Prochaine étape de conception

Construire une **matrice provisoire des séances Training B** à partir du catalogue EF1–EF4, Seuil3–Seuil5 et VMA3–VMA5. Les paramètres non arbitrés doivent rester explicitement marqués **OPEN** plutôt que recevoir des valeurs inventées.

En parallèle, auditer les paramètres existants de Race V2 nécessaires aux modifications additives de courbe. Les deux travaux doivent converger vers un premier scénario jouable et testable, sans réintroduire CTL ni l'ancien modèle Training.


## 12. Race V2 — dépense, terrain et conversion énergie/vitesse (11 novembre 2026)

### Décisions confirmées

- À chaque segment, le joueur lance **N−1 dés** et utilise les mêmes opérations que pendant Training : Keep, Add one, Reroll one ou Add + Reroll.
- Le résultat final choisi est l'énergie **effectivement dépensée** sur ce segment. Cette dépense est débitée de la réserve.
- Le résultat énergétique des dés est écrêté à la coordonnée énergie de VMA : `énergie dépensée = min(résultat des dés, énergie VMA)`. L'excédent est perdu, sans échec ni DNF.
- La difficulté du terrain est ensuite soustraite à l'énergie dépensée :
  `énergie utile = énergie dépensée − difficulté`.
- Une difficulté positive représente une montée et réduit la vitesse. Une difficulté négative représente une descente et augmente la vitesse pour une même dépense.
- La vitesse lue dans la grille constitue le score du segment.
- Le plateau du joueur présente une grille de conversion énergie entière → vitesse entière. La conversion est arrondie à l'entier le plus proche.
- La grille est prolongée linéairement hors de sa plage imprimée, en utilisant la pente du premier segment sous EF et celle du dernier segment au-delà de VMA.
- La réserve est débitée de l'énergie dépensée avant correction du terrain ; la correction ne modifie donc pas le coût énergétique réel.

### Implémentation — fondation R1-C

`experiments/current/race_engine_v2/physiology_grid.py` construit cette grille
à partir de `training_v2.PhysiologyCurve` et expose la résolution d'un segment.
Les valeurs d'énergie et de vitesse des trois ancres restent celles du profil
individuel ; aucun barème numérique de progression n'est inventé.

La résolution applique un plancher technique de vitesse à zéro si une montée
extrême conduit, par extrapolation, à une vitesse négative. Ce plancher est une
protection de résolution, à confirmer lors des tests de scénario.

### À ne pas confondre avec l'ancien harness

L'ancien `core.py` expérimental utilise encore une production, une charge
(production + difficulté), puis une table de coût énergétique. Ce chemin n'est
pas la nouvelle règle. La migration complète doit aussi remplacer le lancer
de tous les dés et l'énumération de tous les sous-ensembles par les opérations
N−1 / Keep / Add / Reroll / Add+Reroll de Training B.

La provenance et le calcul de la réserve totale de Race depuis la préparation
Training restent à intégrer. Le CTL et la réserve expérimentale calculée depuis
CTL ne doivent pas être repris comme règles du nouveau modèle.


## 13. Race V2 — réutilisation des actions de dés Training B (11 novembre 2026)

### Règles déjà arbitrées

- Chaque segment utilise le même pool persistant que celui construit pendant Training.
- Le joueur lance N−1 dés ; le dé restant est réservé.
- Les quatre opérations sont identiques à Training : Keep, Add, Reroll, Add + Reroll.
- Add lance le dé réservé ; Reroll remplace un seul dé parmi les N−1 dés déjà lancés.
- Le résultat final des dés est transmis à la résolution du segment, qui applique le plafond VMA, la correction de terrain et le débit de réserve conformément à la section 12.

### Intégration technique

`experiments/current/race_engine_v2/race_turn.py` réutilise directement
`training_v2.dice.roll_initial` et `resolve_dice_action`. Il n'existe donc
pas de seconde implémentation des règles Keep/Add/Reroll.

Le résolveur reçoit la réserve restante en entrée. La formule de constitution
de la réserve Race depuis la préparation Training reste **OPEN** ; aucun calcul
basé sur CTL n'est repris dans ce nouvel adaptateur.

### Limite actuelle

L'adaptateur résout un segment isolé. L'orchestration longitudinale de la course
(forme, réserve initiale, fraîcheur et enchaînement des segments) reste à migrer
depuis l'ancien harness expérimental.
