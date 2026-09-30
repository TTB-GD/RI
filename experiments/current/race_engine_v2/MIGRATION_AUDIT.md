# Race Engine V2 — audit de migration vers la physiologie intégrée

## SCOPE

**Nature de ce document : audit en lecture seule.** Il ne change ni le GDD, ni
le moteur, ni le statut des mécanismes. Les mots `CURRENT`, `EXPERIMENTAL` et
`OPEN` ci-dessous reprennent leur statut documentaire ; décrire le comportement
du harnais ne le promeut pas en règle de design.

L'audit porte sur le code, les tests, les rapports et les sorties compactes de
`experiments/current/race_engine_v2/`, ainsi que sur `physiology.py`,
`race_v2.py`, le GDD, `CURRENT_STATE.md`, le README racine et
`DOCUMENTATION_AUDIT.md`. La PR #16 est bien fusionnée dans le commit de merge
`40fafda`; ce HEAD fusionné est donc la base auditée. Aucune campagne n'a été
relancée.

Terminologie employée :

- **FAIT CODE** : comportement directement établi par l'implémentation ou ses
  tests ; cela ne lui confère pas un statut de design.
- **FIXTURE EXPERIMENTALE** : valeur ou convention gelée pour les campagnes.
- **POLITIQUE TECHNIQUE** : automate déterministe utilisé comme sonde, pas comme
  modèle validé d'un joueur humain.
- **OBSERVATION EXPERIMENTALE** : mesure des campagnes déjà exécutées.
- **QUESTION OPEN** : arbitrage qui ne peut pas être déduit du harnais.

Conclusion de périmètre : l'objet à migrer n'est pas seulement la résolution
locale de `race_v2.resolve_segment()`. Le harnais a aussi effectivement exercé
une orchestration longitudinale (lancers, Form progressive, construction et
dépense de Réserve, filtrage des choix, DNF et politiques). Cette orchestration
reste toutefois **EXPERIMENTAL**, et non une règle CURRENT.

## FACT — EXISTING RACE ENGINE V2

### Chaîne de résolution effectivement testée

1. **Pool persistant — FAIT CODE du harnais.** Une `DicePool` immuable est
   fournie pour toute la course. Elle n'est ni consommée ni modifiée entre les
   segments.
2. **Lancer complet — FAIT CODE.** Pour chacun des 6 ou 9 segments, tous les dés
   du pool fourni sont lancés. Tous les lancers sont prégénérés avec un RNG
   privé seedé ; une politique ne peut donc pas modifier les lancers futurs.
3. **Sous-ensembles — FAIT CODE.** `available_productions()` énumère toutes les
   combinaisons d'indices de taille 1 à `n`. Chaque sous-ensemble non vide est
   légal avant filtrage énergétique.
4. **Déduplication — FAIT CODE.** Les compositions sont regroupées par leur
   somme ; `productions` est le tuple trié des sommes distinctes. Plusieurs
   sous-ensembles donnant la même somme n'offrent donc qu'une valeur de
   Production.
5. **Choix — POLITIQUE TECHNIQUE.** Le résolveur ne choisit pas. Il transmet le
   menu à l'une des politiques déterministes, puis rejette une valeur qui ne
   figure pas dans `payable`.
6. **Difficulty et Charge — FAIT CODE R1-B.** La Difficulty locale publique est
   ajoutée après le choix de Production :
   `Charge = Production + Difficulty`.
7. **Coût — FIXTURE EXPERIMENTALE.** R1-B calcule
   `Cost = CurveB(Charge)`. La table B vaut 1 jusqu'à 15, 2 de 16 à 21, puis
   3/5/7/10/13 pour 22/23/24/25/26 et 16 pour toute Charge au moins égale à
   27. Sa dernière classe est volontairement non bornée.
8. **Réserve et score — FAIT CODE.** `spent` augmente du coût entier du segment.
   Le score augmente de la Production choisie seulement ; Difficulty n'est
   jamais ajoutée au score.

### Espace exact de Production

Réponses directes sur `available_productions()` :

1. oui, tous les dés du pool sont lancés ;
2. oui, tous leurs sous-ensembles non vides sont énumérés ;
3. oui, les sommes sont dédupliquées ;
4. oui, toutes les faces étant strictement positives, la Production maximale
   est nécessairement la somme du lancer complet ;
5. oui, les dés hors du sous-ensemble choisi n'ont aucun autre effet sur ce
   segment (le lancer complet a toutefois déjà servi au signal de Form aux trois
   premiers segments) ;
6. non, le harnais n'applique aucun plafond de Production lié au CTL, à VMA, à
   RPE Max ou à une autre statistique. **C'est un FAIT DU HARNAIS, pas une
   décision de design.** Après S3, la seule restriction supplémentaire est
   l'abordabilité du coût par la Réserve restante.

Les maximums théoriques des pools audités sont respectivement 36 (`6d6`), 38
(`4d8+1d6`), 44 (`2d10+4d6`), 26 (`1d8+3d6`) et 44
(`1d12+1d8+4d6`). Avant Difficulty, le domaine possible du harnais commence à
1. Avec les Difficulties 0–3 de R1-B, la Charge peut atteindre 47 ; le stress
case D4 de R1-B2 porte ce maximum à 48.

### Comportement longitudinal

Chaque segment reçoit l'état accumulé (`spent`, Réserve connue ou non, Form
observée), le menu du lancer courant et la Difficulty courante/restante. Les
trois premiers engagements ne sont pas filtrés par une Réserve finale encore
inconnue. Après la révélation et le clamp de S3, chaque segment ne propose que
les Productions payables. La conséquence persistante de tous les choix est donc
la Réserve déjà dépensée ; il n'existe ni récupération ni autre état de terrain.

### Politiques techniques

- **EFFICIENT** maximise `Production / Cost` parmi les choix payables, avec la
  Production comme tie-break. Elle privilégie les plateaux efficaces et s'est
  fortement modérée sous Difficulty.
- **AGGRESSIVE** prend la plus grande Production qui laisse un budget technique
  de continuation (coût futur minimal tenant compte du profil restant et buffer
  d'un point par segment), ou la plus grande payable si aucune ne passe ce test.
- **ADAPTIVE** vise une fraction variable de l'espérance du pool : Form observée
  avant S3, puis marge moyenne de Réserve. En présence de Difficulty actuelle ou
  future, elle applique aussi le test de continuation. Elle a produit la plus
  nette accélération finale.
- **GREEDY** prend toujours la plus grande Production payable. Avant le clamp,
  toute Production disponible est payable : cette sonde dépense donc librement
  pendant les trois premiers segments, puis subit souvent un DNF.

Ces politiques démontrent que, **sous leurs propres heuristiques**, le noyau
offre plusieurs trajectoires longitudinales (modération, attaque, adaptation,
myopie). Elles ne démontrent ni une stratégie optimale, ni la perception de cet
espace par un humain, ni un comportement joueur officiel.

## FACT — RESERVE / THREE-SEGMENT REVEAL

### Réserve de base

`base_reserve_from_ctl()` utilise exactement :

```text
base_reserve = race_length × 2 + floor(CTL / 50) × 1
```

R1-A, R1-A2, R1-B et R1-B2 fixent en campagne principale `CTL = 100`, soit une
Réserve de base de 14 pour 6 segments et 20 pour 9 segments. Les tests couvrent
aussi CTL 0. `per_segment=2`, `ctl_step=50` et `reserve_per_step=1` sont des
**FIXTURES EXPERIMENTALES** explicitement gelées pour fournir un choix bon marché
par segment avec une petite marge CTL. Ni le GDD post-PR #16 ni le noyau intégré
n'en font une formule CURRENT ; la construction de Réserve reste EXPERIMENTAL.

### Segments 1, 2 et 3

- **S1 :** le lancer complet et son signal de Form sont révélés avant le choix.
  La Réserve finale reste inconnue (`final_reserve is None`). Toutes les sommes
  disponibles sont donc `payable`, sans contrainte par la Réserve future. Le
  coût choisi est ajouté à `spent`.
- **S2 :** même ordre. Le second signal et la Form cumulée S1–S2 sont connus,
  mais pas le signal S3 ni la Réserve finale. Toutes les Productions disponibles
  restent libres vis-à-vis de celle-ci ; `spent` cumule les deux coûts.
- **S3 :** le troisième signal est classé avant le choix, puis
  `raw_final_reserve` est calculé et transmis à la politique. Malgré cette
  révélation, `final_reserve` n'est pas encore assignée : aucun filtrage
  d'abordabilité n'est appliqué au choix S3. Son coût est ajouté à `spent`, puis
  le plancher est résolu.

La formule exacte avant clamp est :

```text
raw_final_reserve = base_reserve + freshness_bonus + sum(form_values_S1_to_S3)
```

Puis, après le paiement S3 :

```text
final_reserve = max(raw_final_reserve, spent_after_segment_3)
reserve_floor_clamped = (final_reserve != raw_final_reserve)
```

Rôle mécanique, sans interprétation de design : le clamp empêche les trois
engagements non filtrés de produire immédiatement une Réserve restante négative.
Il ne rembourse aucun coût et ne revient sur aucun choix ; quand il s'active, la
Réserve restante juste après S3 vaut zéro.

### Segments 4 et suivants, payable et DNF

Pour chaque Production disponible `p`, `payable_productions()` conserve
exactement les valeurs satisfaisant :

```text
CurveB(p + current_difficulty) <= final_reserve - spent
```

Soit, de façon générique, `cost <= reserve_remaining`. Si le tuple payable est
vide, la course s'arrête avant tout choix ou paiement sur ce segment : `dnf=True`
et `dnf_turn` vaut ce segment. Le score retourné est le score partiel des
segments achevés ; le harnais n'ajoute aucune pénalité de score au DNF.

## FACT — FORM / FRESHNESS / SL

### FORM_SUM

- Donnée utilisée : somme brute du lancer complet courant.
- Classes : distribution exacte des sommes pour le pool ; premiers seuils
  atteignables dont les probabilités cumulées atteignent 20 %, 70 % et 93 % ;
  puis `LOW`, `NORMAL`, `GOOD`, `EXCEPTIONAL`.
- Valeurs de Réserve : `-1`, `0`, `+1`, `+2` respectivement, sous réserve de
  l'effet SL décrit plus bas.
- Temporalité : une classe est connue avant le choix de chacun des segments
  S1–S3. Sa valeur entre dans `observed_form` immédiatement ; l'ensemble des trois
  valeurs entre dans la Réserve révélée à S3.
- Effet sur le choix courant : le signal ne change jamais le menu de Production
  ni son coût. Il peut cependant changer immédiatement le choix d'une politique
  qui lit `observed_form` : ADAPTIVE le fait directement en S1–S2 et utilise la
  Réserve brute révélée en S3. Il finance ensuite les choix futurs via la
  Réserve. Il est donc inexact de dire que Form n'affecte *que* les segments
  futurs dans le harnais testé.

### FORM_PATTERN

- Données utilisées : uniquement structure du lancer complet — multiplicité
  maximale, groupes répétés/paires, triple, deux paires, full, carré, longueur
  maximale de suite et nombre de valeurs distinctes. Ni somme brute ni
  Production choisie ne participe au score.
- Classes : score structurel pondé, distribution exacte propre à chaque pool,
  puis seuils atteignables les plus proches des cibles cumulées 20/70/93 %.
- Valeurs et temporalité : exactement les mêmes `-1/0/+1/+2`, révélation S1–S3
  et usages de politique/Réserve que FORM_SUM.

FORM_PATTERN a été introduit comme contre-factuel contrôlé pour réduire le
« double avantage » de FORM_SUM : un gros lancer donnait à la fois une forte
Production accessible et un meilleur signal de Form. **FORM_PATTERN demeure
EXPERIMENTAL et n'est pas CURRENT.**

### Freshness

Freshness entre uniquement sous la forme d'un entier `freshness_bonus` :

```text
raw_final_reserve = base_reserve + freshness_bonus + Form_S1 + Form_S2 + Form_S3
```

Les valeurs testées dans R1-A sont 0 et +3 ; R1-A2, R1-B et R1-B2 utilisent 0.
Le bonus est connu des politiques dès S1. Avant la révélation, AGGRESSIVE et
son test de continuation peuvent donc déjà l'utiliser ; après S3, il fait partie
de la Réserve finale. Il s'additionne à Form, sans modifier sa classe. Il ne
modifie directement ni Production disponible, ni Charge, ni coût, ni score.
Aucune formule Training → Freshness n'existe dans ce moteur ou n'est déduite ici.

### SL

Le booléen technique `long_run_preparation` n'agit que dans `form_value()` :

```text
sans SL : LOW=-1, NORMAL=0, GOOD=+1, EXCEPTIONAL=+2
avec SL : LOW= 0, NORMAL=0, GOOD=+1, EXCEPTIONAL=+2
```

SL protège donc seulement contre la valeur négative d'une classe LOW aux trois
premiers segments. Il peut augmenter la Réserve brute/finale d'un point par LOW,
mais n'ajoute pas un bonus fixe direct et ne touche ni Production, ni Difficulty,
ni Charge, ni courbe de coût. Les observations montrent un effet modeste et ne
rendent pas SL obligatoire. Son rôle de course reste **EXPERIMENTAL / OPEN**.

## FACT — DIFFICULTY / PRODUCTION

La règle exacte de R1-B est :

```text
Charge = Production + Difficulty
Cost = CurveB(Charge)
Score = Production
```

- Difficulty est un entier local non négatif, public avant le choix.
- Le profil entier est une fixture connue. `PolicyView` expose explicitement la
  Difficulty courante et le tuple des Difficulties restantes ; il n'expose ni
  lancers futurs, ni signaux futurs.
- Difficulty ne possède aucun compteur, cumul, récupération ou autre état
  persistant. Seul le coût déjà ajouté à `spent` transporte son effet.
- Elle ne change pas les Productions `available`. Après S3, elle peut réduire
  `payable`, car le coût de chaque option est calculé sur `P + D`.
- Les dés non sélectionnés sont inutilisés pour la Production de ce segment.
  Aucun reliquat de dé n'est conservé.

## EXPERIMENTAL EVIDENCE

Les chiffres suivants sont ceux des rapports versionnés, pas de nouveaux
résultats. Ils caractérisent les fixtures et politiques testées seulement.

### R1-A — noyau longitudinal plat

- Le menu comporte en moyenne 10,41 à 22,19 sommes distinctes selon le pool ;
  l'énumération maximale reste de 63 sous-ensembles pour six dés. La composition
  du pool change donc la granularité, pas seulement son espérance.
- Sous Curve B, les scores moyens agrégés sont 108,70 EFFICIENT, 129,66
  AGGRESSIVE, 124,83 ADAPTIVE et 91,47 GREEDY. Les DNF correspondants sont 0 %,
  1,9 %, 0 % et 76,3 %. Les politiques ont donc produit des trajectoires
  longitudinales distinctes ; GREEDY est la sonde myope nettement pathologique.
- ADAPTIVE accélère en fin de course dans 87,7 % des courses Curve B agrégées,
  contre 37,5 % pour EFFICIENT et 13,7 % pour AGGRESSIVE.
- Freshness +3 modifie les scores de 0,00 / +2,55 / +3,63 / +5,10 et les DNF de
  0 / −0,8 / 0 / −4,5 points (EFFICIENT / AGGRESSIVE / ADAPTIVE / GREEDY).
- SL modifie les scores de 0,00 / +1,75 / +1,36 / +1,38 et réduit modestement
  les DNF AGGRESSIVE/GREEDY ; rien n'indique qu'il soit obligatoire.
- Le clamp est absent pour EFFICIENT et ADAPTIVE, présent dans 0,4 % des courses
  AGGRESSIVE et 47,0 % des courses GREEDY sur l'ensemble R1-A. Il absorbe donc
  surtout la dépense précoce non contrainte de la sonde myope.

### R1-A2 — contre-factuel Form

- La corrélation Pearson signal↔somme brute passe de 0,741 (SUM) à −0,109
  (PATTERN), et signal↔Production choisie de 0,390 à −0,057. La corrélation
  résiduelle varie par pool et PATTERN ne constitue pas une normalisation parfaite.
- PATTERN change 68,9 % à 96,7 % des trajectoires ADAPTIVE appariées selon le
  pool, mais change peu la performance moyenne (120,68 SUM contre 120,63
  PATTERN). Cela prouve un effet sur les décisions de cette politique, pas une
  valeur perceptible ou optimale pour un joueur.
- Les bandes de classe structurelles restent grossières, notamment pour
  `1d8+3d6`. Le rapport maintient explicitement PATTERN comme contre-factuel
  EXPERIMENTAL, non comme règle CURRENT.

### R1-B — Difficulty locale

- EFFICIENT ralentit d'environ 2,6 Production sur les segments difficiles et
  reste sur un plateau de coût identique. ADAPTIVE maintient presque sa
  Production (−0,05 EARLY, −0,46 LATE) en payant un surcoût modeste.
  AGGRESSIVE alterne maintien et ralentissement ; GREEDY maintient les
  difficultés EARLY atteintes et paie ensuite par davantage de trajectoires
  tronquées.
- EARLY fait passer les DNF agrégés FLAT de 0/0/6,0/68,3 % à
  0/0,1/8,2/75,5 % pour EFFICIENT/ADAPTIVE/AGGRESSIVE/GREEDY. LATE donne
  0/0/6,0/70,7 %. Le timing affecte donc surtout les sondes agressive et myope.
- Après un bloc difficile, les baisses de Production persistent pour trois
  politiques alors que le segment redevient plat : c'est uniquement l'effet de
  `spent`/de l'abordabilité, pas un état de Difficulty.
- Difficulty ne marque jamais directement : tous les scores mesurés sont la
  somme des Productions des segments achevés.

### R1-B2 — magnitude, fréquence et placement

- D1 est doux ; D2 et D3 séparent encore clairement les politiques, avec
  ralentissements et maintiens et sans nouveau régime DNF pour les politiques
  prudentes. Il s'agit d'une zone technique observée, pas d'une échelle validée.
- D4 est l'avertissement principal : le nombre de choix jugés plausibles ne
  s'effondre pas, mais le DNF ADAPTIVE agrégé atteint 19,3 % sous les fixtures
  fixes. D4 reste un stress case, pas une Difficulty retenue.
- Deux occurrences D2/D3 restent localisées ; trois et quatre produisent une
  érosion progressive (score/accélération en baisse, dette de Réserve en hausse)
  sans explosion des DNF non-GREEDY.
- Les profils distinguent petites Difficulties roulantes et blocs plus forts :
  P1 et P2 ont la même somme brute de Difficulty 4 mais pas les mêmes effets,
  conformément à la non-linéarité de Curve B.

**LIMITES communes :** pas de test humain, courbe et Réserve non validées,
politiques déterministes, profils publics et non négatifs, aucune Nutrition,
Fatigue, récupération, blessure ou SPEC. Ces résultats prouvent l'existence d'un
espace de réponse dans le harnais, pas son équilibrage final.

## MIGRATION MATRIX

| Élément Race V2 existant | État actuel | Dépend de Curve B ? | Compatible tel quel avec `PhysiologyProfile` ? | Modification nécessaire | Statut |
|---|---|---:|---:|---|---|
| Lancer du pool | Pool complet, RNG seedé, lancers prégénérés | Non | Oui | Aucune logique | FAIT CODE, orchestration EXPERIMENTAL |
| Énumération des sous-ensembles | Tous non vides, par indices | Non | Oui | Aucune logique | FAIT CODE |
| Production | Sommes positives distinctes, sans plafond physiologique | Non | Partiellement | Aucun changement pour l'énumération ; la validité du domaine de Charge doit être décidée | EXPERIMENTAL / OPEN à la frontière |
| Difficulty | Entier local public, profil restant visible | Non | Partiellement | Aucune logique locale ; peut faire sortir la Charge du domaine | EXPERIMENTAL |
| Charge | `Production + Difficulty` | Non | Oui dans `EF..VMA` seulement | Aucune formule ; domaine hors bornes OPEN | CURRENT local / limites OPEN |
| Coût | `CurveB(Charge)`, table non bornée | **Oui** | Non par simple substitution totale | Injecter profil et appel physiologique ; traiter les domaines OPEN requiert une décision préalable | Curve B EXPERIMENTAL ; physiologie intégrée |
| Réserve de base | `2×length + floor(CTL/50)` | Non | Oui mécaniquement | Aucune pour le profil ; statut design inchangé | FIXTURE EXPERIMENTALE |
| Form | SUM ou PATTERN, trois signaux, `-1/0/+1/+2` | Non | Oui mécaniquement | Aucune pour le profil | EXPERIMENTAL |
| Freshness | Bonus direct 0/+3 à la Réserve | Non | Oui mécaniquement | Aucune pour le profil | FIXTURE EXPERIMENTALE |
| SL | Neutralise seulement `LOW=-1` | Non | Oui mécaniquement | Aucune pour le profil | EXPERIMENTAL / OPEN |
| Clamp segment 3 | `max(raw, spent_after_S3)` | Indirectement via `spent` | Oui si les trois coûts sont définis | Conserver la logique ; les coûts hors domaine bloquent avant le clamp | EXPERIMENTAL |
| Filtrage payable | `cost(P+D) <= remaining` après S3 | Oui, via la fonction de coût | Oui dans le domaine seulement | Remplacer l'évaluateur de coût et lui fournir le profil | FAIT CODE, orchestration EXPERIMENTAL |
| DNF | Aucun choix payable | Indirectement | Oui dans le domaine seulement | Aucune condition nouvelle ; l'erreur de domaine n'est pas un DNF | EXPERIMENTAL |
| Score | Somme des Productions achevées | Non | Oui | Aucune | CURRENT dans la résolution locale |
| `PolicyView` | État longitudinal, courbe nommée et profil Difficulty restant | Oui pour le champ `curve` | Non tel quel | Le contexte de coût doit fournir le profil plutôt qu'un nom de table ; contrat hors domaine à décider | DETTE TECHNIQUE de migration |
| Policies | Appellent `production_cost(..., curve)` | Oui | Non telles qu'écrites | Rebrancher leur consultation de coût sur le profil, sans changer leurs heuristiques | POLITIQUES TECHNIQUES |

La compatibilité « oui » signifie uniquement que la logique ne dépend pas de
la forme de Curve B. Elle ne promeut pas l'élément au statut CURRENT.

## INCOMPATIBILITIES WITH PHYSIOLOGYPROFILE

### Compatible immédiatement dans le domaine

Pour toute Charge satisfaisant `profile.ef <= Charge <= profile.vma`, la chaîne
locale est déjà alignée : Production et Difficulty forment Charge, le coût est
pur, seul le coût est dépensé, et seul Production marque. Lancers,
sous-ensembles, déduplication, Form, Freshness, SL, révélation S3, clamp, score
et persistance par `spent` ne requièrent pas de nouvelle règle physiologique.

Le filtrage payable et les politiques sont conceptuellement réutilisables parce
qu'ils interrogent tous une fonction de coût. Ils ne sont toutefois pas
compatibles *syntaxiquement* tels quels : leur API transporte un identifiant
`curve: str`, et `production_cost()` appelle `energy_cost`, tandis que
`physiological_cost()` exige un `PhysiologyProfile`.

### Cas incompatibles et changement de domaine

`physiological_cost()` lève actuellement `ValueError` lorsque `load < EF` ou
`load > VMA`. Une substitution littérale ne filtre donc pas proprement ces
options : elle peut interrompre la construction du tuple payable, une politique
qui évalue ses choix, ou la résolution des trois premiers segments. Une erreur de
domaine n'est pas assimilable au DNF existant, lequel signifie exclusivement
« aucun coût défini ne tient dans la Réserve restante ».

- **Charge sous EF.** Le harnais peut offrir une Production aussi basse que 1,
  sans plancher. Avec `Difficulty=0`, toute Production `< EF` donne une Charge
  sous EF ; une Difficulty positive remonte la Charge et peut réduire ou annuler
  ce cas. La source première est donc la liberté de choisir un petit sous-ensemble
  de Production ; Difficulty non négative ne peut jamais créer à elle seule un
  passage sous EF.
- **Charge au-dessus de VMA.** Les Productions possibles atteignent 26 à 44
  selon les pools, sans plafond. Elles peuvent donc dépasser VMA seules. Une
  Difficulty positive ajoute jusqu'à 3 dans R1-B et 4 dans R1-B2 : elle peut
  créer le franchissement lorsque `Production <= VMA` mais
  `Production + Difficulty > VMA`, ou amplifier un dépassement déjà causé par
  Production. Le domaine théorique observé des fixtures atteint Charge 48.

Sans valeurs de profil injectées dans ces campagnes, l'audit peut localiser et
borner les Loads possibles, mais pas compter honnêtement leur fréquence sous EF
ou au-dessus de VMA. La réponse dépendrait du profil et de la politique. Aucun
nouveau Monte-Carlo n'est nécessaire pour établir le blocage logique.

### Charge > VMA — recadrage

**Ancien moteur R1-B :**

1. il ne possédait aucune notion de VMA ;
2. il ne limitait pas Production par VMA ou par une autre statistique ;
3. il ne limitait pas davantage Charge ;
4. Curve B possédait une dernière classe `>=27`, sans borne supérieure ;
5. toute Charge positive élevée recevait donc simplement le coût constant 16.

**Nouvelle physiologie intégrée :** VMA est la borne haute explicite du domaine
modélisé, et l'implémentation rejette une Charge supérieure. Les tests intégrés
confirment ce rejet ; aucun fichier ou résultat nommé `above_vma_probe` n'est
présent dans le HEAD fusionné audité. La seule information locale disponible
est donc celle-ci : le cas est détecté et signalé hors domaine, sans clamp et sans
règle de coût.

**Question de migration :** VMA introduit ainsi une frontière qui n'existait pas
dans Curve B. Décider ce qui se passe à cette frontière est indispensable avant
de pouvoir appliquer le nouveau coût à tous les choix du moteur existant. Cet
audit ne transforme ni VMA en plafond de Production, ni l'exception en DNF, ni
la classe terminale de Curve B en règle physiologique.

## DOCUMENTATION GAPS

| Constat | Classement | Impact |
|---|---|---|
| Le GDD §7.2 et le README racine décrivent correctement la résolution locale `P + D → Charge → coût/score`, mais ne rappellent pas dans ce passage que le harnais a déjà caractérisé une orchestration longitudinale complète. | **AMBIGUÏTÉ GDD** | Une lecture isolée peut confondre la petite frontière CURRENT avec toute l'étendue des preuves EXPERIMENTAL. Le GDD dit néanmoins explicitement que Réserve, Form, politiques, longueurs et objectifs restent hors de cette frontière : il n'y a pas de contradiction objective. |
| `CURRENT_STATE.md` qualifie Réserve/Form/policies/lengths/DNF d'`experimental harness material`, puis liste l'orchestration multi-segment comme non intégrée ; cette formulation de statut est exacte mais ne résume pas les comportements et campagnes déjà disponibles. | **DETTE TECHNIQUE** documentaire | Le snapshot est juste mais trop compact pour servir seul à la migration ; le présent audit fournit le chaînon manquant sans promouvoir le harnais. |
| `race_v2.py` ne contient que `resolve_segment()` tandis que l'orchestration effective reste dans `experiments/current/race_engine_v2/core.py` et dépend d'une API Curve A/B/C. | **RISQUE ARCHITECTURAL** | Une migration centrée uniquement sur le module intégré pourrait réimplémenter ou oublier la révélation S3, le clamp, le payable, le DNF et le contexte des politiques. |
| L'ancien harnais accepte toute Charge positive ; le nouveau coût rejette sous EF et au-dessus de VMA. | **DIVERGENCE GDD** au sens de domaines entre fixture historique et nouvelle base intégrée, explicitement signalée comme OPEN | Le remplacement direct n'est pas total. Ce n'est ni une erreur de Curve B ni une autorisation implicite de plafonner Production. |
| `PolicyView.curve` et les politiques sont couplés à l'identifiant de table plutôt qu'à une abstraction/profile de coût. | **DETTE TECHNIQUE** | Adaptation d'interface requise, sans raison de changer la philosophie des politiques. |
| La formule CTL→Réserve, FORM_SUM/PATTERN, Freshness direct, effet SL et clamp S3 ne sont pas des règles CURRENT. | **CHOIX DE DESIGN** encore EXPERIMENTAL / OPEN | Ils sont mécaniquement conservables mais ne doivent pas être promus par la migration. |
| Le harnais ne contient pas de profil Training→`PhysiologyProfile` et ne peut donc pas quantifier les sorties de domaine pour les futurs coureurs. | **LIMITE PROTOTYPE** | La compatibilité globale dépend des profils réellement produits, encore non implémentés. |

Aucun **BUG / ERREUR OBJECTIVE** n'a été identifié dans la correspondance
locale : le code intégré et le harnais R1-B partagent bien `Charge=P+D`, coût de
Charge et score de Production. Aucune **INCOHÉRENCE GDD** interne supplémentaire
n'est établie par cet audit ; l'enjeu est la différence de périmètre et de statut.

## DESIGN QUESTIONS

Les seules décisions bloquantes avant un branchement complet sont :

1. **Domaine inférieur :** quel est le comportement de course quand une option
   existante donne `Charge < EF` (légalité et/ou coût), puisque le harnais offre
   des Productions dès 1 et que le noyau intégré rejette ce domaine ?
2. **Frontière supérieure :** quel est le comportement quand
   `Production + Difficulty > VMA`, sans supposer que VMA plafonne Production et
   sans transformer arbitrairement l'erreur de domaine en DNF ?
3. **Orchestration à conserver :** la Réserve expérimentale doit-elle devenir la
   règle de migration avec ses trois signaux connus successivement, sa Réserve
   révélée avant le choix S3 mais clampée après ce choix, ou ce timing doit-il
   rester un simple harnais ?
4. **Entrées de Réserve :** FORM_SUM ou FORM_PATTERN, Freshness direct et la
   protection LOW de SL ont-ils un statut de design suffisant pour être inclus
   dans l'intégration, ou doivent-ils rester des commutateurs expérimentaux ?
5. **Profil issu du Training :** quelle conversion minimale et validée produit
   `EF`, `Seuil` et `VMA` pour la course ? Sans elle, le moteur peut accepter un
   profil fourni mais ne peut ni construire celui du joueur ni évaluer la portée
   réelle des deux sorties de domaine.

Ces questions ne demandent ni SPEC, ni Fatigue, ni Nutrition, ni nouveau rôle
pour VMA. Tant qu'elles restent ouvertes, la migration sûre consiste seulement
à reconnaître que la majorité de l'orchestration est mécaniquement réutilisable,
alors que la fonction de coût et son domaine ne sont pas substituables partout
sans décision de Game Design.


## Note de clôture post-audit — 2026-09-29

Cet audit reste le constat historique pré-intégration. Les décisions ultérieures ont
validé le plancher `Cost = EF` sous EF, la légalité `Charge <= VMA`, et la
conservation expérimentale de l'orchestration S1–S3. Le moteur a ensuite reçu un
chemin `PhysiologyProfile` explicite tout en conservant Curve A/B/C pour reproduire
les campagnes historiques. Les calibrations et la conversion Training restent OPEN.
