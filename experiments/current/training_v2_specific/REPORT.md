# Training V2 — rôle du Spécifique : rapport D1–D3

**EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN.**

Baseline inspectée avant création du harnais :
`f9f94bd75fd46fd8ee5cecf5a70fa8564150eb7b`.

## FACT

- D1 exécute les seeds `0..49`, 16 tours, 2 contextes × 3 tables × 3
  politiques : **900 campagnes / 14 400 tours**. Les mêmes seeds sont employés
  dans chaque cellule. État initial : EF 6, Seuil 8, VMA 10, AS42 7 ou AS10 9.
- Le lancer, D99 bonus-réserve, les pistes EF/Q, la difficulté et
  `coût = niveau - EF + difficulté(niveau)` viennent de Training V2 minimal.
  Une partition physique maximise Q sous `EF >= Q` (tie-break déterministe).
  VMA puis Seuil sont tentés au plus une fois par tour; un coût tenté mais
  busted ne crédite pas progression Q. Toute énergie est comptée comme
  physiologie, SPEC, ou inutilisée.
- G_GENERAL finance VMA/Seuil puis verse le reliquat à SPEC. G_SWITCH compare
  le coût physiologique marginal minimal aux points restant au prochain palier
  (égalité : physiologie; égalité physiologique : VMA). G_SPEC finance d'abord
  le prochain palier, puis la physiologie. D1 emploie uniquement BALANCED.
- Un palier Vitesse saturé par Seuil (AS42) ou VMA (AS10) devient
  obligatoirement ECO. Cette conversion et tous les tie-breaks sont des
  conventions **expérimentales**, non des règles proposées.
- D2 reprend six états finaux observés de D1 (seed 0, S2), sans nouvelle
  campagne. Curve B ne reçoit que Production; ni EF, ni Seuil, ni VMA
  n'entrent dans le calcul. C1 applique ECO à AS±1; C2 applique ECO complet à
  AS et la moitié arrondie au supérieur à AS±1. D3 est une grille déterministe
  de quatre paliers, exécutée parce que D2 distingue bien Production (AS) et
  réduction locale (ECO).

## RESULTS D1

Moyennes G_SWITCH sur 50 seeds; les quatre colonnes donnent `% Q → SPEC` par
blocs de quatre tours.

| Table | T1–4 | T5–8 | T9–12 | T13–16 | Part finale | Paliers | 1er tour SPEC > physio, médiane [min–max] |
|---|---:|---:|---:|---:|---:|---:|---:|
| S1 | 40,5 % | 36,1 % | 17,8 % | 0,3 % | 19,9 % | 5,00 | 2 [1–4] |
| S2 | 38,4 % | 38,2 % | 33,6 % | 30,3 % | 34,1 % | 4,72 | 2 [1–5] |
| S3 | 38,5 % | 36,6 % | 34,0 % | 35,6 % | 35,8 % | 3,34 | 2 [1–11] |

- Le premier investissement volontaire G_SWITCH arrive médianement au tour 1
  (plage 1–2) pour toutes les tables. SPEC dépasse 25 % de Q cumulée au tour 1
  médian (plage 1–5). **Le basculement général → spécifique recherché
  n'apparaît donc pas.** S1 montre même l'inverse : SPEC se tarit après
  saturation des cinq paliers. S2 est légèrement décroissante; S3 est presque
  plate, avec un léger rebond final.
- Les métriques d'allocation sont identiques entre AS42 et AS10. C'est une
  conséquence structurelle : les deux contextes partagent coûts et lancer, et
  leur frontière AS affecte l'attribution AS/ECO, pas le choix Q. Les seeds
  font varier le premier tour SPEC > physiologie (jusqu'à T11 sous S3), mais
  pas sa médiane.
- Contrôles : G_GENERAL envoie 18,5–20,0 % de Q à SPEC; G_SPEC en envoie 19,9 %
  (S1), 36,4 % (S2), 62,2 % (S3). S3/G_SPEC est dominant dès T1–4 (84,4 %).
  S1 plafonne tôt sous toutes les politiques; aucun palier testé ne produit la
  trajectoire tardive attendue sous G_SWITCH.

## RESULTS D2

- Les six états observés couvrent EF 10–11, Seuil 12–16, VMA 17–18, AS 9–12,
  ECO 1–2 et 3–5 paliers. À AS±2, Curve B vaut toujours 1 dans cette plage.
- Sous C1, ECO 1 ou 2 ramène le coût à zéro à AS−1, AS et AS+1, mais laisse le
  coût 1 à AS±2 : coûts répétés respectifs `0` et `4/10`. C2 conserve le coût
  nul au centre et, avec l'arrondi supérieur, également à AS±1 pour ces états.
- Un profil physiologique supérieur n'obtient **aucun avantage direct** : le
  calcul ne lit pas EF/Seuil/VMA. SPEC est lisible (déplacement du point AS et
  économie locale), mais le plancher et la zone basse de Curve B écrasent les
  différences ECO entre 1 et 2 dans cet échantillon.
- Une AS saturée reste améliorable par ECO : chaque nouveau point continue à
  augmenter la réduction avant application du plancher, même si le coût observé
  peut déjà être nul.

## RESULTS D3

Avec quatre paliers identiques et C1 :

| Contexte | Build | AS | ECO | Coût à AS | ×4 | ×10 |
|---|---|---:|---:|---:|---:|---:|
| AS42 | FULL_SPEED | 11 | 0 | 1 | 4 | 10 |
| AS42 | BALANCED | 9 | 2 | 0 | 0 | 0 |
| AS42 | FULL_ECO | 7 | 4 | 0 | 0 | 0 |
| AS10 | FULL_SPEED | 13 | 0 | 1 | 4 | 10 |
| AS10 | BALANCED | 11 | 2 | 0 | 0 | 0 |
| AS10 | FULL_ECO | 9 | 4 | 0 | 0 | 0 |

AS+1 et ECO+1 agissent donc sur des axes distincts : Production potentielle
contre coût répété. Cependant BALANCED et FULL_ECO ont ici le même coût à AS à
cause du plancher; D3 établit une distinction mécanique, pas une valeur
stratégique équilibrée.

## OBSERVATIONS

1. **Q1 — Non.** Sous G_SWITCH, SPEC n'augmente pas progressivement : il est
   déjà choisi dès le début; S1 décroît fortement, S2 légèrement, S3 reste
   presque stable.
2. **Q2 — Seeds oui, distance non.** Le premier dépassement par tour varie de
   1 à 4/5/11 selon S1/S2/S3, mais AS42 et AS10 donnent exactement le même
   timing d'allocation dans ce modèle.
3. **Q3 — Aucune des trois formes.** S1 est mesurable mais sature; S2/S3 sont
   mesurables mais déjà autour de 38–41 % au premier bloc. S2 est la sonde la
   moins extrême sur l'ensemble de la campagne, sans réaliser le signal visé.
4. **Q4 — Oui, par construction vérifiée.** Modifier la physiologie sans
   modifier AS/ECO ne change aucune sortie D2.
5. **Q5 — Oui mécaniquement, avec réserve.** AS déplace la Production du point
   spécifique; ECO réduit son coût local répété. Curve B basse/plancher zéro
   masque toutefois une partie de la graduation économique.

## INTERPRETATIONS

- Avec ces coûts initiaux (Seuil 3, VMA 5) et un premier palier SPEC à 5,
  l'arbitrage marginal G_SWITCH ne crée pas une phase générale initiale : le
  reliquat et les comparaisons deviennent immédiatement favorables ou utiles à
  SPEC. Les coûts croissants ne sont donc pas, seuls, la cause d'un basculement
  tardif dans le protocole testé.
- L'absence d'effet distance sur le timing n'indique pas que la distance est
  inutile; elle indique que les frontières AS interviennent après l'allocation
  dans ce harnais. Elles différencient les adaptations obtenues, pas la demande
  énergétique qui les finance.
- SPEC peut porter seul une transformation lisible, mais la combinaison
  AS initiales 7/9 + Curve B rend surtout visible la géographie locale du bonus,
  beaucoup moins son amplitude économique.

## LIMITS

- Les politiques sont des sondes déterministes, pas des joueurs ni une IA
  optimale. La partition maximise Q afin d'isoler son allocation; ce choix peut
  sous-représenter une stratégie EF.
- Les trajectoires divergent après upgrades et busts; les seeds partagés ne
  sont pas des contre-factuels tour par tour. Cinquante seeds ont suffi : les
  profils par blocs sont nets, donc aucune extension à 100 n'a été lancée.
- D2 sélectionne seed 0 et S2 par politique comme états observés illustratifs;
  six états ne décrivent pas toute la distribution. Aucune course complète
  n'est simulée.
- Curve B est un instrument externe conçu pour des Productions plus hautes.
  Aux AS imposées ici, son coût plat minimal et le plancher zéro limitent la
  capacité de distinguer les niveaux ECO.
- « Production potentielle au point spécifique » est ici l'AS elle-même; le
  harnais ne prétend pas convertir cette valeur en performance ou résultat de
  course.

## DESIGN QUESTIONS

1. Le premier palier SPEC doit-il être accessible dès que son coût marginal
   égale une adaptation générale, ou une condition d'ouverture est-elle voulue ?
2. La distance cible doit-elle agir sur l'allocation SPEC, plutôt que seulement
   sur la frontière d'AS ?
3. Une fois les cinq paliers atteints, l'énergie Q actuellement inutilisée
   doit-elle rester perdue, être convertie, ou être dépensable autrement ?
4. Le domaine de Production de Curve B doit-il être remappé avant d'évaluer la
   valeur économique d'AS/ECO aux valeurs physiologiques 6/8/10 ?
5. Le plancher zéro doit-il faire partie d'une future règle ECO, ou rester une
   simple protection technique de cette expérience ?

---

# D4 — Enveloppe SPEC physiologique

**EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN.** Cette enveloppe est une
**sonde structurelle**, pas une règle validée.

## FACT

- D4 teste une seule formule : `headroom = zone_high - zone_low` et
  `used_spec_capacity = (AS - zone_low) + ECO`, donc la contrainte équivalente
  `AS + ECO <= zone_high`. AS42 emploie `[EF, Seuil]`; AS10 emploie
  `[Seuil, VMA]`. Une unité de Vitesse ou d'Économie consomme une unité de
  capacité.
- D4-A est une énumération analytique sans Monte-Carlo. D4-B n'est lancé
  qu'après confirmation analytique; il exécute **30 seeds (`0..29`) × 2
  contextes × 16 tours = 960 tours**, uniquement avec S2, BALANCED et
  `G_SWITCH_HEADROOM`.
- À saturation, SPEC est indisponible. Une réussite Seuil rouvre AS42; une
  réussite VMA rouvre AS10. La capacité rouverte ne devient éligible qu'au tour
  suivant. Les coûts, le bust, les pistes, la partition maximisant Q et le D99
  bonus-réserve restent ceux du harnais D1.
- `alternation_count` compte un cycle complété où SPEC avait déjà été choisi,
  est ensuite observé saturé avec investissement physiologique, est rouvert par
  la frontière pertinente, puis est de nouveau choisi.
- Classement descriptif fixé dans le harnais : 0 % des runs avec alternance =
  `PAS D'ALTERNANCE`; strictement moins de 50 % = `ALTERNANCE RARE`; au moins
  50 % = `ALTERNANCE RÉCURRENTE`.

## RESULTS D4-A

| Contexte / zone | Headroom | Builds | Vitesse | Économie | Mixtes | Nouveaux builds après `high +1` |
|---|---:|---:|---:|---:|---:|---:|
| AS42 6–8 | 2 | 6 | 2 | 2 | 1 | 4 |
| AS42 8–12 | 4 | 15 | 4 | 4 | 6 | 6 |
| AS42 10–15 | 5 | 21 | 5 | 5 | 10 | 7 |
| AS42 12–18 | 6 | 28 | 6 | 6 | 15 | 8 |
| AS10 8–10 | 2 | 6 | 2 | 2 | 1 | 4 |
| AS10 12–16 | 4 | 15 | 4 | 4 | 6 | 6 |
| AS10 15–20 | 5 | 21 | 5 | 5 | 10 | 7 |
| AS10 18–24 | 6 | 28 | 6 | 6 | 15 | 8 |

Le build neutre `(0, 0)` complète chaque total. Dans chaque fixture,
`zone_high +1` ajoute exactement la nouvelle diagonale
`AS_relative + ECO = headroom +1`, soit 4, 6, 7 ou 8 builds. D4-A confirme
donc qu'une unité de frontière rouvre une capacité utile et plusieurs choix,
et autorise l'exécution de D4-B.

## RESULTS D4-B

Parts moyennes de Q par bloc :

| Contexte | Mesure | T1–4 | T5–8 | T9–12 | T13–16 |
|---|---|---:|---:|---:|---:|
| AS42 | Physiologie | 49,7 % | 39,7 % | 55,2 % | 50,2 % |
| AS42 | SPEC | 38,2 % | 39,8 % | 33,0 % | 30,2 % |
| AS10 | Physiologie | 49,7 % | 42,4 % | 53,9 % | 45,9 % |
| AS10 | SPEC | 31,6 % | 38,2 % | 34,0 % | 31,3 % |

| Mesure | AS42 | AS10 |
|---|---:|---:|
| Tours saturés, moyenne [min–max] | 0 [0–0] | 0,9 [0–2] |
| Épisodes, moyenne [min–max] | 0 [0–0] | 0,9 [0–2] |
| Premier épisode | jamais | médiane T3 [T3–T4], 86,7 % des runs |
| Réouvertures, moyenne [min–max] | 0 [0–0] | 0,9 [0–2] |
| Alternations complètes, moyenne [min–max] | 0 [0–0] | 0,9 [0–2] |
| Runs avec ≥1 alternance | 0 % | 86,7 % |
| Réouverture → prochaine saturation | non observé | 4 tours en moyenne |
| AS final moyen | 9,73 | 11,70 |
| ECO final moyen | 2,00 | 2,00 |
| Seuil / VMA final moyens | 15,13 / 16,73 | 15,10 / 16,60 |

Sur les 60 trajectoires, 26 (43,3 %) présentent au moins une alternance; elles
sont toutes AS10. Classement global descriptif : **ALTERNANCE RARE**. Le sous-
ensemble AS10 est au contraire **ALTERNANCE RÉCURRENTE**; AS42 est
**PAS D'ALTERNANCE**.

## OBSERVATIONS

1. **Les timings diffèrent enfin.** AS10 sature généralement vers T3 et alterne
   dans 86,7 % des runs; AS42 ne présente aucun tour saturé.
2. **La saturation AS10 est précoce mais non universelle**, entre T3 et T4. Sa
   durée n'est pas longue : VMA rouvre la capacité dans les 27 épisodes
   observés. AS42 ne permet pas de qualifier un timing de saturation.
3. **La réouverture est effective.** Chaque `+1 VMA` pertinent en AS10 rouvre
   une décision SPEC, suivie d'un nouveau choix SPEC dans les cycles comptés.
   D4-A établit analytiquement la même propriété pour `+1 Seuil` en AS42, mais
   D4-B n'observe pas de saturation AS42 à rouvrir.
4. **Aucun blocage durable n'est observé.** AS10 sort de chacun de ses épisodes;
   AS42 ne s'y engage jamais.
5. L'alternance AS10 n'est pas une simple alternance imposée à chaque tour :
   seuls 0 à 2 cycles apparaissent par run et quatre tours séparent en moyenne
   une réouverture de la saturation suivante. Elle reste néanmoins une
   conséquence directe et mécanique de la priorité minimale testée.

## INTERPRETATIONS

- D4 **EST INCONCLUSIF SUR** l'hypothèse générale : « la physiologie construit
  l'enveloppe, SPEC la consomme, puis sa saturation rend la physiologie à
  nouveau pertinente ». La chaîne est structurellement valide en D4-A et
  apparaît nettement pour AS10, mais pas une seule fois pour AS42 en D4-B.
- La différence vient de la dynamique des coûts et frontières, non d'une règle
  propre à la distance : dans les tours qui financent SPEC, Seuil progresse
  assez souvent pour déplacer simultanément la frontière AS42 et empêcher
  l'état saturé d'être observé au tour suivant. Pour AS10, une progression
  Seuil ne déplace pas VMA; la capacité peut donc se fermer avant que VMA ne la
  rouvre.
- L'enveloppe produit ainsi plus qu'un simple plafond, mais elle ne garantit pas
  à elle seule le même cycle selon la zone physiologique considérée.

## LIMITS

- Une saturation n'est comptée que si elle existe au début d'un tour. Une
  frontière progressant dans le même tour qu'un palier SPEC peut empêcher
  toute saturation observable, ce qui explique une partie du résultat AS42.
- La partition maximise Q et la politique reste déterministe; les fréquences
  décrivent cette sonde, pas un joueur humain. Les trajectoires ne sont pas des
  contre-factuels appariés après divergence du RNG.
- Seule S2, une formule de headroom et 16 tours sont testés. Conformément au
  critère d'arrêt, aucune autre équation ni campagne supplémentaire n'est
  essayée après ce résultat mixte.
- Les builds D4-A sont des possibilités géométriques. Leur nombre ne mesure ni
  leur valeur de course, ni leur accessibilité temporelle dans D4-B.

## DESIGN QUESTIONS

1. Une saturation momentanée en fin de tour, immédiatement annulée par la
   progression de frontière du même tour, doit-elle avoir une signification de
   jeu ou rester invisible comme dans cette sonde ?
2. Une enveloppe est-elle voulue si elle produit des cycles pour AS10 mais pas
   pour AS42 avec les mêmes coûts et la même politique ?
3. Le déplacement de la borne basse doit-il avoir un effet propre sur la
   capacité, malgré l'équivalence algébrique `AS + ECO <= zone_high` ?
4. Faut-il juger l'alternance sur la présence d'au moins un cycle ou sur une
   répétition minimale au cours d'une préparation ?
