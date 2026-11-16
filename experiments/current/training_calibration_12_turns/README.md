# Training — état du calibrage des adaptations sur 12 tours

**Date :** 16 novembre 2026  
**Statut :** note de travail — résultat analytique préliminaire, non normatif  
**Périmètre :** traduction de la matrice physiologique en progression des jauges sur une préparation de référence de 12 tours.

> Cette note documente le travail effectué, les hypothèses de calcul et les tâches restantes. Elle ne valide ni les fréquences de séances proposées ni l'équilibrage final des seuils. Les décisions explicites de l'utilisateur restent prioritaires ; les éléments qualifiés d'hypothèses ne doivent pas être traités comme des règles acquises.

---

## 1. Décisions et règles utilisées

### 1.1. Horizon de référence

**DECISION — 12 tours communs :** le calibrage en cours prend 12 tours comme horizon de référence pour les quatre préparations (5 km, 10 km, semi-marathon et marathon). Les différences entre plans doivent venir de la composition des séances, des adaptations et de leurs coûts, pas d'une durée différente dans ce calibrage.

Cette référence de 12 tours doit être répercutée dans le GDD : sa version actuelle décrit encore une préparation de 7, 10, 13 ou 16 tours selon le scénario. Cette divergence documentaire n'est pas résolue par la présente note.

### 1.2. Matrice : interprétation directe

**DECISION — coefficients directs :** chaque coefficient de la matrice représente directement le nombre de points d'adaptation apportés au nœud concerné par une séance réussie de la famille correspondante.

- Aucun coefficient n'est multiplié par la dose énergétique.
- Les coefficients ne constituent ni un budget à répartir, ni des poids à normaliser.
- La dose énergétique détermine le coût de réalisation de la séance.
- Le RPE détermine sa difficulté intrinsèque et intervient dans le risque de bust.
- La fatigue est une variable distincte.
- Une séance réussie apporte les adaptations fixes indiquées par sa ligne de matrice.

Exemple : une séance de la famille VMA apporte directement EF 0, AS42 0, AS21 0, Seuil +1, AS10 +1, AS5 +1 et VMA +2.

### 1.3. Matrice conservée

La matrice complète doit être conservée, y compris les colonnes des AS non actives :

| Famille de séance ↓ / Nœud physiologique → | EF | AS42 | AS21 | Seuil | AS10 | AS5 | VMA |
|---|---:|---:|---:|---:|---:|---:|---:|
| EF / Endurance | 2 | 1 | 1 | 1 | 0 | 0 | 0 |
| Seuil | 1 | 1 | 1 | 2 | 1 | 0 | 0 |
| VMA | 0 | 0 | 0 | 1 | 1 | 1 | 2 |
| AS42 | 1 | 2 | 1 | 0 | 0 | 0 | 0 |
| AS21 | 0 | 1 | 2 | 1 | 0 | 0 | 0 |
| AS10 | 0 | 0 | 0 | 1 | 2 | 1 | 0 |
| AS5 | 0 | 0 | 0 | 0 | 1 | 2 | 1 |
| Général | 1 | 1 | 1 | 1 | 1 | 1 | 1 |

Une seule AS est active dans un scénario. Les contributions de la matrice vers les autres AS ne sont toutefois pas supprimées : elles restent des adaptations physiologiques passives. La jauge Spécifique, les séances dédiées et la progression de RA concernent uniquement l'AS active.

### 1.4. Seuils de progression

Pour les jauges d'adaptation Endurance, Seuil, VMA et Spécifique, les coûts successifs retenus comme référence de travail sont :

| Palier | Coût du palier | Cumul |
|---|---:|---:|
| 1 | 3 | 3 |
| 2 | 4 | 7 |
| 3 | 5 | 12 |
| 4 | 7 | 19 |
| 5 | 10 | 29 |

Pour Spécifique, l'effet du palier reste le choix entre +1 énergie sur l'AS active et +1 RA, selon les règles du GDD.

La jauge Général est distincte : elle comptabilise de l'énergie et ne reçoit pas automatiquement les points d'adaptation de la matrice. La grille provisoire figée pour la suite du calibrage est :

| Palier Général | Coût successif en énergie | Cumul | Effet |
|---|---:|---:|---|
| 1 | 15 | 15 | +1 énergie EF, Seuil, VMA et AS active |
| 2 | 15 | 30 | idem |
| 3 | 35 | 65 | idem + ajout du 5e dé |
| 4 | 35 | 100 | idem |
| 5 | 55 | 155 | idem + ajout du 6e dé |

Cette grille est une référence provisoire figée pour le travail en cours, pas encore une validation par simulation. Les ajouts du 5e et du 6e dé ne comptent pas dans le plafond global de quatre améliorations de dés. Les améliorations restent plafonnées à quatre.

---

## 2. Premier modèle analytique testé

### 2.1. Hypothèse de composition des 12 tours

Pour isoler l'effet de la matrice, un premier squelette a été construit avec 12 séances structurantes réussies, soit une occurrence par tour :

| Famille de séance | 5 km | 10 km | Semi | Marathon |
|---|---:|---:|---:|---:|
| EF | 6 | 6 | 7 | 8 |
| Seuil | 2 | 2 | 2 | 1 |
| VMA | 3 | 2 | 1 | 0 |
| AS active | 1 | 2 | 2 | 3 |
| **Total** | **12** | **12** | **12** | **12** |

**HYPOTHESIS :** cette répartition cherche à traduire une spécialisation croissante vers l'AS et l'EF à mesure que la distance augmente, avec davantage de VMA sur 5 km. Elle n'est pas présentée comme une distribution validée de l'entraînement réel.

Les pourcentages de temps couru par intensité ne permettent pas, à eux seuls, de déduire le nombre de séances : durée, échauffement, récupération et contenu d'une séance diffèrent selon les familles. Le tableau est donc une hypothèse de fréquence, pas la conversion directe des pourcentages sportifs.

### 2.2. Résultat de l'application de la matrice

Les coefficients sont additionnés tels quels pour chaque occurrence. Les valeurs ci-dessous présentent les quatre nœuds associés aux jauges suivies dans ce premier calcul : EF, Seuil, VMA et AS active.

| Préparation | EF | Seuil | VMA | AS active |
|---|---:|---:|---:|---:|
| 5 km | 14 | 13 | 7 | 5 (AS5) |
| 10 km | 14 | 14 | 4 | 8 (AS10) |
| Semi | 16 | 14 | 2 | 13 (AS21) |
| Marathon | 20 | 10 | 0 | 15 (AS42) |

Les colonnes des AS passives sont bien calculées par la matrice, mais ne sont pas affichées ici comme jauges de Spécifique indépendantes.

### 2.3. Paliers atteints dans ce modèle

En appliquant les seuils cumulés 3 / 7 / 12 / 19 / 29 :

| Préparation | EF | Seuil | VMA | AS active |
|---|---:|---:|---:|---:|
| 5 km | 3 | 3 | 2 | 1 |
| 10 km | 3 | 3 | 1 | 2 |
| Semi | 3 | 3 | 0 | 3 |
| Marathon | 4 | 2 | 0 | 3 |

**RESULT / OBSERVATION :** la composition proposée différencie les profils dans le sens recherché : VMA davantage développée sur 5 km ; profil plus équilibré sur 10 km ; AS active davantage développée sur semi et marathon ; EF renforcée sur marathon.

**LIMITES :** il s'agit d'un calcul arithmétique déterministe sur une composition hypothétique. Ce n'est ni une simulation de partie, ni une mesure de probabilité, ni une preuve que les séances peuvent être financées ou réussies dans les conditions du jeu.

---

## 3. Ce que ce premier calcul permet — et ne permet pas — de conclure

### Ce qu'il permet d'observer

- La matrice produit des profils différents selon les familles de séances retenues.
- Avec 12 séances structurantes réussies, plusieurs jauges atteignent déjà deux ou trois paliers.
- Le calibrage des seuils ne peut pas être évalué indépendamment du nombre de séances réellement finançables et réussies.
- La matrice doit rester directe : réduire les coefficients ou les multiplier par la dose pour corriger un résultat serait contraire à la règle retenue.

### Ce qu'il ne permet pas encore de conclure

- Si les compositions proposées sont réalistes en nombre de séances et en temps d'entraînement.
- Si les joueurs peuvent financer ces séances avec l'énergie produite par leur pool de dés.
- Si le RPE et le risque de bust rendent certaines compositions trop difficiles.
- Si la fatigue limite suffisamment l'accumulation de séances de qualité.
- Si les cinq jauges ont toutes un intérêt décisionnel distinct, notamment Endurance par rapport à Général.
- Si les seuils de progression sont trop bas ou trop élevés dans une partie jouée.

### Cas non inclus dans le calcul

La ligne « Général » de la matrice n'a pas été incluse dans les totaux ci-dessus. Son rôle doit être raccordé explicitement au catalogue des familles de séances. Il faut éviter toute confusion entre :

1. la famille de séance Général, ligne de la matrice qui apporte +1 à chaque nœud ;
2. la jauge Général, qui accumule de l'énergie et possède ses propres paliers ;
3. la famille EF / Endurance, qui contribue selon sa propre ligne de matrice.

Aucune contribution de la ligne Général ne doit être ajoutée arbitrairement tant que le nombre et la définition des séances de cette famille ne sont pas établis.

---

## 4. Travail restant — ordre proposé

### Étape 1 — Définir un catalogue de séances exploitable

Pour chaque séance et chaque dose disponible, préciser :

- famille et nœuds affectés ;
- coût énergétique exact ;
- adaptations directes fixes ;
- RPE ;
- fatigue produite ;
- limites éventuelles de répétition et conditions d'éligibilité.

La dose est un coût de réalisation et identifie une entrée de séance ; elle ne multiplie pas les adaptations de la matrice.

### Étape 2 — Construire des plans-types sur 12 tours

Pour chaque distance, établir une composition plausible qui distingue :

- séances EF / Endurance ;
- séances Seuil ;
- séances VMA ;
- séances AS active ;
- éventuelles séances de la famille Général.

La composition doit être cohérente avec les répartitions de temps d'entraînement réel, sans assimiler pourcentage de temps et nombre de séances. Les séances secondaires, échauffements et récupérations doivent être traités selon les conventions du catalogue, pas ajoutés comme des occurrences fictives.

### Étape 3 — Vérifier la faisabilité énergétique

À partir du pool initial de 4d6 et de sa progression, vérifier tour par tour :

- énergie produite et énergie allouable ;
- coût des séances choisies ;
- possibilité de financer les plans-types ;
- effets de la progression de la jauge Général ;
- trajectoires normale, bonne et exceptionnelle.

Les objectifs de progression de dés actuellement visés restent des cibles de conception : partie normale, ajout du 5e dé et deux améliorations ; bonne partie, cinq ou six dés et trois améliorations ; préparation exceptionnelle, six dés, quatre améliorations et dernier palier Général. Ils ne sont pas encore démontrés par un modèle de trajectoire.

### Étape 4 — Intégrer RPE, bust et fatigue

Évaluer les séances réellement réussies, et pas seulement les séances planifiées :

- risque de bust selon le RPE autorisé ;
- annulation de la séance concernée et des séances suivantes en cas de bust, selon la règle en vigueur ;
- fatigue acquise et ses conséquences sur les tours ultérieurs ;
- régulation de la qualité par la fatigue, sans imposer un quota arbitraire.

### Étape 5 — Recalculer les progressions et évaluer les seuils

Appliquer la matrice directe aux séances effectivement réussies, puis calculer les paliers atteints. Vérifier notamment :

- différenciation des quatre distances ;
- fréquence des jauges qui atteignent les paliers 4 et 5 ;
- fréquence des occasions d'amélioration de dés ;
- plafond global de quatre améliorations ;
- place réelle de l'Endurance et recouvrement éventuel avec Général ;
- caractère suffisamment exceptionnel du dernier palier Général.

Ne modifier les seuils qu'après ce calcul intégré. Les résultats devront être accompagnés de leurs hypothèses et d'une méthode reproductible.

### Étape 6 — Consolider le GDD

Une fois les règles et hypothèses suffisamment stabilisées :

- réconcilier la référence de 12 tours avec la section du GDD qui indique encore 7 / 10 / 13 / 16 tours ;
- clarifier la formulation des adaptations par séance et par dose ;
- expliciter le rôle de la famille Général dans la matrice ;
- intégrer les résultats de calibrage avec leur statut exact (décision, hypothèse ou résultat expérimental).

---

## 5. Prochaine action

Construire le modèle de faisabilité tour par tour : pool de dés, énergie disponible, catalogue de séances, coûts, RPE et fatigue. C'est le prochain travail nécessaire pour passer du calcul théorique de la matrice à une progression réellement atteignable en partie.

**Aucune modification du code ni aucun résultat de simulation ne sont inclus dans cette étape.**
