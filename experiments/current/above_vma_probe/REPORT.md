# Race V2 — rapport de micro-sonde Charge > VMA

## FACT

- **Statut : EXPERIMENTAL COUNTERFACTUALS — NOT CURRENT BEHAVIOR.** Aucune
  variante étudiée ici n'est une règle validée.
- Le code intégré accepte `PhysiologyProfile(EF, Seuil, VMA)` avec
  `EF < Seuil < VMA`; `physiological_cost` rejette actuellement une Charge
  supérieure à VMA. La présente sonde ne modifie pas ce comportement.
- Protocole : énumération déterministe exhaustive de 3 profils × 4 Productions
  (`VMA-3 ... VMA`) × 4 Difficulties (`0 ... 3`) = **48 configurations**.
  Il n'y a ni RNG, ni course, ni tour, ni état persistant.
- A conserve la contrainte `Production + Difficulty <= VMA`. B prolonge
  localement la pente post-Seuil de `+3`. C conserve `C(VMA)` comme base et
  ajoute `k × Overload`, pour `k ∈ {2,3,4}`. Sous ou à VMA, B et C appellent et
  reproduisent exactement le coût intégré.
- `results.json` contient, pour chacune des 48 configurations : profil,
  Production, Difficulty, Charge, Overload, coût natif jusqu'à VMA, légalité A
  et coûts B/C2/C3/C4. La révision source, les paramètres et les agrégats y sont
  aussi enregistrés.

## RESULTS

### Variante A — plafond de Production induit

| Profil | Difficulty | Production maximale légale | Perte vs D=0 |
|---|---:|---:|---:|
| P1 (0/5/10) | 0 / 1 / 2 / 3 | 10 / 9 / 8 / 7 | 0 / 1 / 2 / 3 |
| P2 (0/6/10) | 0 / 1 / 2 / 3 | 10 / 9 / 8 / 7 | 0 / 1 / 2 / 3 |
| P3 (1/6/11) | 0 / 1 / 2 / 3 | 11 / 10 / 9 / 8 | 0 / 1 / 2 / 3 |

Ainsi, dès que `Difficulty > 0`, VMA devient indirectement le plafond
`Production <= VMA - Difficulty`. Chaque point de Difficulty retire exactement
un point à la Production maximale légale.

### Variantes B/C — surcharge par niveau d'Overload

Les nombres entre parenthèses sont le surcoût relatif à `C(VMA)`.

| Profil | `C(VMA)` | Overload | B | C2 | C3 | C4 |
|---|---:|---:|---:|---:|---:|---:|
| P1 (0/5/10) | 25 | +1 | +3 (12%) | +2 (8%) | +3 (12%) | +4 (16%) |
|  |  | +2 | +6 (24%) | +4 (16%) | +6 (24%) | +8 (32%) |
|  |  | +3 | +9 (36%) | +6 (24%) | +9 (36%) | +12 (48%) |
| P2 (0/6/10) | 24 | +1 | +3 (12.5%) | +2 (8.33%) | +3 (12.5%) | +4 (16.67%) |
|  |  | +2 | +6 (25%) | +4 (16.67%) | +6 (25%) | +8 (33.33%) |
|  |  | +3 | +9 (37.5%) | +6 (25%) | +9 (37.5%) | +12 (50%) |
| P3 (1/6/11) | 25 | +1 | +3 (12%) | +2 (8%) | +3 (12%) | +4 (16%) |
|  |  | +2 | +6 (24%) | +4 (16%) | +6 (24%) | +8 (32%) |
|  |  | +3 | +9 (36%) | +6 (24%) | +9 (36%) | +12 (48%) |

### Cas concrets obligatoires — P1 (`EF=0`, `Seuil=5`, `VMA=10`)

| Cas | P | D | Charge | Overload | Coût natif jusqu'à VMA | A | B | C2 | C3 | C4 |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|
| 1 | 8 | 2 | 10 | 0 | 25 | LEGAL | 25 | 25 | 25 | 25 |
| 2 | 9 | 2 | 11 | 1 | 25 | ILLEGAL | 28 | 27 | 28 | 29 |
| 3 | 10 | 1 | 11 | 1 | 25 | ILLEGAL | 28 | 27 | 28 | 29 |
| 4 | 10 | 3 | 13 | 3 | 25 | ILLEGAL | 34 | 31 | 34 | 37 |

Pour le joueur : A supprime les choix 2–4; B et C les conservent avec les coûts
affichés. Le cas 2 montre aussi que le dépassement vient de Difficulty alors que
la Production choisie reste sous VMA; le cas 3 montre la même Charge et donc les
mêmes coûts avec une décomposition Production/Difficulty différente.

## OBSERVATIONS

1. Sous A, la réduction de Production maximale vaut exactement Difficulty :
   `0/1/2/3` points pour `D=0/1/2/3`.
2. B ne crée ni saut ni changement de pente à VMA : son incrément reste `+3`,
   comme dans toute la zone post-Seuil. VMA est donc mathématiquement invisible
   dans la fonction de coût B; elle ne subsiste que comme repère de mesure de
   l'Overload.
3. C ne crée aucun **saut** de coût à VMA : à Overload 0, le coût vaut exactement
   `C(VMA)`. C2 et C4 créent toutefois une **rupture de pente** (`3→2` et `3→4`).
   C3 est point par point identique à B.
4. Parmi les coefficients testés, C2 et C4 sont effectivement différents de B;
   C3 ne l'est pas. Après `n` points d'Overload, leur écart à B vaut
   respectivement `-n`, `0`, `+n`.
5. Tous les coûts testés sont strictement croissants. Il n'existe aucune
   discontinuité de valeur. C2 a seulement une baisse de coût marginal à la
   frontière, C4 une hausse, et B/C3 aucune rupture mathématique.
6. Dans la grille demandée, D=3 laisse exactement `P=VMA-3` légal parmi les
   quatre Productions testées; Difficulty ne rend donc jamais toute la grille
   impossible. La sonde ne définit pas « choix raisonnable » et ne permet pas
   de déclarer si ce choix restant est raisonnable pour une course.

## INTERPRETATIONS

- **Structurel :** A transforme la difficulté en réduction un-pour-un du plafond
  légal de Production. B autorise le dépassement sans signal mathématique à VMA.
  Une C dont `k` diffère de la pente préfrontière donne une frontière visible
  comme changement de coût marginal, mais pas comme saut.
- **Dépendant des coefficients expérimentaux :** les coûts absolus, pourcentages,
  le fait précis que C3 soit identique à B, et les pentes `3→2`/`3→4` résultent
  de la calibration `2/3` et des coefficients C testés. Avec une autre pente
  post-Seuil, le coefficient C identique à B changerait lui aussi.
- La séparation sémantique « coût physiologique de base + Overload » de C3 ne
  suffit pas à produire une différence numérique avec B. Une éventuelle valeur
  de cette séparation hors coût immédiat n'est pas testée ici.

## LIMITS

- Cette analyse locale n'évalue ni Réserve, Form, Fatigue, blessure, DNF, SPEC,
  Training, politique de joueur, trajectoire de course ou équilibrage.
- Les Productions supérieures à VMA ne sont pas testées. Les 48 lignes ne
  couvrent que les offsets demandés et une Difficulty maximale de 3.
- Les pourcentages sont relatifs à `C(VMA)`, pas à une Réserve ou à un coût de
  course complet. Ils ne mesurent donc ni faisabilité ni gravité pour le joueur.
- Aucune variante n'est classée ou recommandée. Les pentes `2/3` restent une
  calibration expérimentale.

## DESIGN QUESTIONS

1. **DESIGN QUESTION —** Difficulty doit-elle réduire directement la Production
   maximale légale (A), ou une Production `<= VMA` doit-elle rester disponible
   lorsque seul le terrain crée le dépassement ?
2. **DESIGN QUESTION —** VMA doit-elle être une frontière uniquement sémantique,
   une frontière de légalité, ou une rupture visible de coût marginal ?
3. **DESIGN QUESTION —** Si une rupture marginale est voulue, doit-elle rendre
   l'Overload moins coûteux que la zone post-Seuil (C2) ou plus coûteux (C4) ?
   C3 n'apporte aucune rupture numérique par rapport à B avec la calibration
   actuelle.
4. **DESIGN QUESTION —** Quel niveau minimal de Production doit rester
   « raisonnable » ou disponible sur une Difficulty élevée ? Cette notion et ses
   conséquences sur une course complète sont hors de la présente sonde.
