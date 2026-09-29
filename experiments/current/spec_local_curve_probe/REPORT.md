# Micro-sonde SPEC / courbe locale

> **EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN**

## FACT

- Cette sonde analytique est isolée de la production. Elle ne modifie ni le GDD,
  ni Training V2, ni Race Engine V2, ni Fatigue V1.
- Protocole : énumération déterministe exhaustive des transitions `POSITION` et
  `EFFICACITÉ`, dédupliquées par état final `(AS, nombre P, nombre E)`, pour 4 AS,
  3 empreintes et les budgets exacts 2/3/4. Il n'y a ni RNG, ni seed, ni
  Monte-Carlo, ni simulation de course ou d'entraînement.
- Une `POSITION` déplace le centre et donc l'empreinte acquise de `AS` vers
  `AS+1`. Elle n'est retenue que si la courbe résultante reste valide. Les AS42/21
  restent strictement sous Seuil ; les AS10/5 restent strictement sous VMA.
- Une EFFICACITÉ répète la même empreinte locale. Elle devient illégale dès que
  la courbe descend sous le coût EF (= 0) ou cesse d'être non décroissante.
- Version du harness : 1. Commande reproductible :
  `python experiments/current/spec_local_curve_probe/probe.py`.

## RESULTS — COURBE NATIVE

La courbe choisie est volontairement abstraite et non calibrée : incrément `+2`
de EF jusqu'à Seuil inclus, puis `+3`. Seuil=5 porte ainsi l'unique changement de
régime global.

**Table A — courbe native**

| position | coût natif | zone |
|---:|---:|:---|
| 0 | 0 | EF→Seuil |
| 1 | 2 | EF→Seuil |
| 2 | 4 | EF→Seuil |
| 3 | 6 | EF→Seuil |
| 4 | 8 | EF→Seuil |
| 5 | 10 | EF→Seuil |
| 6 | 13 | Seuil→VMA |
| 7 | 16 | Seuil→VMA |
| 8 | 19 | Seuil→VMA |
| 9 | 22 | Seuil→VMA |
| 10 | 25 | Seuil→VMA |

Les coûts sont monotones, et l'incrément passe explicitement de 2 à 3 après la
position Seuil.

## RESULTS — E0

E0 est le point seul `{AS: -1}`. Après un niveau : AS42 `4→3`, AS21 `8→7`,
AS10 `13→12`, AS5 `19→18`. Toutes ces courbes restent valides. C'est l'empreinte
la plus locale et la moins économique (économie totale 1 par niveau).

## RESULTS — E1

E1 est l'empreinte symétrique `{AS-1: -1, AS: -2, AS+1: -1}`.

## RESULTS — E2

E2 est l'unique asymétrie testée : `{AS-1: -1, AS: -2, AS+1: -2}`. Elle garde
le bénéfice central sur le cran plus rapide, sans agir au-delà de `AS+1`. Ses
coefficients ont été fixés avant l'énumération et n'ont pas été ajustés.

**Table B — empreintes après 1 EFFICACITÉ**

| empreinte | AS | position(s) : natif→ajusté (delta) |
|:---|:---|:---|
| E0 | AS42 | 2 : 4→3 (-1) |
| E0 | AS21 | 4 : 8→7 (-1) |
| E0 | AS10 | 6 : 13→12 (-1) |
| E0 | AS5 | 8 : 19→18 (-1) |
| E1 | AS42 | 1 : 2→1 (-1); 2 : 4→2 (-2); 3 : 6→5 (-1) |
| E1 | AS21 | 3 : 6→5 (-1); 4 : 8→6 (-2); 5 : 10→9 (-1) |
| E1 | AS10 | 5 : 10→9 (-1); 6 : 13→11 (-2); 7 : 16→15 (-1) |
| E1 | AS5 | 7 : 16→15 (-1); 8 : 19→17 (-2); 9 : 22→21 (-1) |
| E2 | AS42 | 1 : 2→1 (-1); 2 : 4→2 (-2); 3 : 6→4 (-2) |
| E2 | AS21 | 3 : 6→5 (-1); 4 : 8→6 (-2); 5 : 10→8 (-2) |
| E2 | AS10 | 5 : 10→9 (-1); 6 : 13→11 (-2); 7 : 16→14 (-2) |
| E2 | AS5 | 7 : 16→15 (-1); 8 : 19→17 (-2); 9 : 22→20 (-2) |

E1 et E2 restent non décroissantes après un niveau pour les quatre fixtures.
E2 économise 5 unités par niveau contre 4 pour E1 et 1 pour E0 : elle est donc
la plus généreuse, sans former de vallée ni violer un invariant dans les états
accessibles observés.

## SATURATION / RÉOUVERTURE

**Table C — espace SPEC** (`distincts / saturés`; un zéro signifie que la
saturation a empêché de dépenser exactement ce budget, pas qu'un état a disparu.)

| AS | empreinte | SPEC 2 | SPEC 3 | SPEC 4 |
|:---|:---|---:|---:|---:|
| AS42 | E0 | 3 / 0 | 2 / 0 | 1 / 1 |
| AS42 | E1 | 3 / 0 | 2 / 0 | 1 / 1 |
| AS42 | E2 | 3 / 0 | 2 / 0 | 1 / 1 |
| AS21 | E0 | 1 / 1 | 0 / 0 | 0 / 0 |
| AS21 | E1 | 1 / 1 | 0 / 0 | 0 / 0 |
| AS21 | E2 | 1 / 1 | 0 / 0 | 0 / 0 |
| AS10 | E0 | 3 / 0 | 4 / 0 | 3 / 0 |
| AS10 | E1 | 3 / 0 | 3 / 0 | 3 / 0 |
| AS10 | E2 | 3 / 0 | 3 / 0 | 3 / 0 |
| AS5 | E0 | 2 / 0 | 2 / 0 | 1 / 1 |
| AS5 | E1 | 2 / 0 | 2 / 0 | 1 / 1 |
| AS5 | E2 | 2 / 0 | 2 / 0 | 1 / 1 |

Les courbes complètes, les niveaux P/E et les deux légalités de chaque état sont
dans `results.json`. AS10 ne sature pas dans la fenêtre demandée : ses trois
POSITION possibles laissent encore une branche légale au budget 4.

**Table D — réouverture des 9 états saturés distincts**

| état saturé | frontière avant | frontière +1 | Position rouverte ? | Efficacité rouverte ? |
|:---|---:|---:|:---:|:---:|
| E0 / AS42 / P2 E2 | Seuil 5 | 6 | oui | non |
| E1 / AS42 / P2 E2 | Seuil 5 | 6 | oui | non |
| E2 / AS42 / P2 E2 | Seuil 5 | 6 | oui | non |
| E0 / AS21 / P0 E2 | Seuil 5 | 6 | oui | non |
| E1 / AS21 / P0 E2 | Seuil 5 | 6 | oui | non |
| E2 / AS21 / P0 E2 | Seuil 5 | 6 | oui | non |
| E0 / AS5 / P1 E3 | VMA 10 | 11 | oui | non |
| E1 / AS5 / P1 E3 | VMA 10 | 11 | oui | non |
| E2 / AS5 / P1 E3 | VMA 10 | 11 | oui | non |

La frontière +1 rouvre donc systématiquement POSITION, jamais EFFICACITÉ
directement dans cet échantillon. La nouvelle POSITION peut ensuite déplacer
l'empreinte et créer une nouvelle trajectoire SPEC ; cette trajectoire ultérieure
n'est pas comptée comme une réouverture directe d'EFFICACITÉ.

À EF=0 et Seuil=5 constants, les courbes VMA=10, 11 et 12 restent monotones
(`[0,…,25]`, `[0,…,28]`, `[0,…,31]`). Respectivement 81, 90 et 99 petits
états locaux bruts ont été contrôlés ; 4 candidats illégaux près d'EF sont
rejetés à chaque largeur. Le nombre d'illégalités n'augmente donc pas avec VMA.
La progression VMA rouvre proprement POSITION dans les états AS5 saturés sans
nécessiter une règle `VMA-EF <= X`.

## OBSERVATIONS

1. Les trois empreintes préservent les invariants sur tous les états **retenus** ;
   les transitions qui les violeraient sont correctement déclarées illégales.
2. Avec la même règle, les espaces diffèrent : AS21 est saturée dès 2 paliers,
   AS42 et AS5 à 4, tandis qu'AS10 ne l'est pas encore à 4.
3. La chaîne `SPEC → saturation → frontière +1 → POSITION rouverte` est observée
   pour AS42, AS21 et AS5. Elle n'est pas observable pour AS10 dans la fenêtre 2–4.
4. E0 offre une branche supplémentaire à AS10 aux budgets 3 et 4, car les
   incréments natifs post-Seuil permettent trois réductions ponctuelles légales.

## INTERPRETATIONS

- **Q1.** E0 conserve le plus strictement localité et économie ; E1 est le
  compromis local équilibré le plus lisible. E2 reste mécaniquement propre ici,
  mais son économie totale supérieure ne lui donne aucun gain d'espace SPEC sur
  E1 dans cette fenêtre.
- **Q2.** Oui : la distance de l'AS à sa frontière crée quatre capacités
  distinctes, même si E1 et E2 ont les mêmes nombres agrégés.
- **Q3.** Oui pour 3 AS sur 4 dans le budget observé, mais sous la forme précise
  d'une réouverture de POSITION. Ce n'est pas démontré pour AS10 à 4 paliers.
- **Q4.** Oui dans cette sonde : VMA+1 rouvre AS5, et étendre VMA jusqu'à 12
  n'altère ni la monotonie native ni le nombre fixe de candidats locaux rejetés.
- **Q5.** Aucune vallée ou rupture retenue. E2 est manifestement la plus
  économique ; E0 rend EFFICACITÉ plus disponible post-Seuil. Aucune dominance
  globale ni absence générale de saturation n'est établie.

## LIMITS

- La courbe et les coefficients sont des fixtures analytiques, pas une
  calibration physiologique ni une proposition de règle CURRENT.
- L'énumération ne mesure ni choix humain, ni valeur en course, ni entraînement,
  ni RPE Max. En particulier, elle ne teste pas encore la régulation dynamique
  que RPE Max pourrait apporter à une VMA non bornée par EF.
- Les budgets sont exactement 2/3/4 et les résultats de saturation ne doivent pas
  être extrapolés au-delà. AS10 demanderait plus de 4 paliers pour tester sa
  réouverture après saturation.
- Le déplacement de l'empreinte avec POSITION est une convention expérimentale
  explicitée ici, pas une décision de Game Design.

## DESIGN QUESTIONS

1. E0 (minimal) ou E1 (local équilibré) doit-elle servir de candidate lors d'une
   éventuelle proposition de design ?
2. Une économie de 5 unités par niveau rend-elle E2 trop généreuse malgré le
   respect des invariants locaux ?
3. La progression physiologique doit-elle rouvrir seulement POSITION directement,
   comme ici, ou aussi EFFICACITÉ ?
4. La différence de capacité observée entre AS21 et AS10 est-elle souhaitable ?
