# Run It — Document de travail D1 : Training, portefeuille, fatigue et coopération D99

> **Date :** 16 octobre 2026  
> **Statut :** WORKING DESIGN / NON NORMATIF — ne remplace ni le GDD ni CURRENT_STATE.md.  
> **Objet :** consolider les arbitrages issus de la discussion C1/C2/D1, préparer un prototype minimal et conserver explicitement les points ouverts.  
> **Gouvernance :** décision exprimée en conversation ≠ règle CURRENT du dépôt ; promotion dans le GDD seulement après revue, tests et décision formelle.

## 1. Intentions et contraintes héritées

**Vision C1 (déjà discutée et retenue)**

- Training : construction d'un moteur physiologique ; Race : exploitation de ce moteur ; environ 2/3 et 1/3 de l'expérience.
- Session de jeu visée : 60–90 minutes, 2–4 joueurs ; préparation simultanée et coordination positive, pas de concurrence sur une ressource commune.
- Progression incrémentale et spécialisée sans verrouillage précoce ; décisions d'allocation centrales ; risque volontaire mais raisonnablement récupérable ; une erreur isolée ne doit pas détruire une préparation.
- Le hasard propose des opportunités et des contraintes ; le joueur arbitre.
- Training sur environ 12–16 tours à comparer, non figés.

**Principes C2 retenus**

- Une seule allocation finance les séances et leurs adaptations : pas de seconde réserve de dés pour des capacités.
- Le pool de dés est un instrument de décision, non la finalité du jeu : volume réellement réalisé → dés supplémentaires ; qualités réussies → améliorations de dés.
- Les séances apportent des adaptations physiologiques propres, éventuellement multidimensionnelles (EF / Seuil / VMA) ; paliers de progression croissants, bénéfices perceptibles à horizon de quelques tours.
- Ne pas réutiliser sans examen les anciens seuils CTL et d'upgrade comme objectifs d'équilibrage du modèle futur.

## 2. Décisions D1 formulées et acceptées en conversation

| ID | Décision de conception | Portée |
|---|---|---|
| D1-P1 | Progression du profil → déblocage d'options de séances → **choix d'acquisition** par le joueur | Les options ouvertes ne rejoignent pas automatiquement toutes son portefeuille |
| D1-P2 | **Portefeuille permanent** : séances acquises consultables à chaque tour, sans pioche ni cooldown de cartes | La réutilisation au sein d'un même tour demeure soumise aux règles de séance |
| D1-P3 | Acquisition lors de **certains jalons physiologiques**, distincts des simples déblocages | Cadence et jalons exacts OPEN |
| D1-P4 | **Sortie longue (SL) structurante mais facultative**, avec contraintes et bénéfices propres | Effet distinctif en Race OPEN |
| D1-P5 | Préserver l'idée de soutien EF, mais **réexaminer sa forme** | Débouche sur une régulation par la fatigue plutôt qu'un quota |
| D1-P6 | **SL = séance structurante ; SPEC = spécialisation transversale** pouvant caractériser plusieurs familles de séances | Propriété SPEC en Race OPEN |
| D1-F1 | La composante blackjack de fatigue dépend du **résultat final des dés comparé au TN**, non de la dépense en séances | Modification proposée par rapport au calcul principal codé |
| D1-F2 | Fatigue persistante tolérée jusqu'à la **taille du pool permanent**, soit 4/5/6 ; au-dessus : **réserve temporairement indisponible**, sans perte d'un dé permanent | Restitution à préciser ; seuils repris de l'intention exprimée et non promus CURRENT |
| D1-F3 | En surentraînement : **TN permanent inchangé** et **n−1 dés actifs lancés normalement** ; actions **Keep/Reroll** seulement ; **Add/Add+Reroll indisponibles** | Aucun motif ne réactive la réserve neutralisée |

### Orientation D1 confirmée sur l'EF et les qualités

- La **récupération** provient de la **charge globale du blackjack sous TN**, pas d'un surplus d'EF.
- Seul l'**excès de dépense en qualité sur la dépense EF** ajoute une fatigue de déséquilibre ; un programme majoritairement EF ne produit pas de récupération additionnelle à ce titre.
- Certaines séances (notamment SL ou qualité particulièrement exigeante) peuvent avoir une **pénibilité intrinsèque positive**.
- La liberté de composition doit être régulée par la fatigue et ses conséquences, plutôt que par des plafonds arbitraires : étudier la suppression de `Qualités ≤ EF` et du plafond de qualités D99.
- La formule exacte, les unités et l'effet de la pénibilité sont **hypothèses à calibrer**, non décisions numériques.

## 3. Modèle conceptuel de fatigue — candidat de référence D1

Notations explicites :

- `P` : pool **permanent** ; `n = |P|` ; `TN(P) = Σ (faces_d + 1)/2`, réserve permanente comprise.
- `R` : somme des faces **retenues au résultat final** selon les règles de dés ; pas la dépense du programme.
- `E_EF`, `E_qual` : coûts d'énergie des séances **effectivement réalisées** classées EF ou Qualité ; la classification de SL reste à préciser, SPEC est une propriété transversale.
- `F_t` : fatigue persistante avant le tour.

Proposition de calcul :

```text
F_blackjack = f(R - TN(P))
F_exces_qualite = alpha * max(0, E_qual - E_EF)
F_penibilite = somme(penibilite_positive_des_seances_effectivement_realisees)
F_(t+1) = F_t + F_blackjack + F_exces_qualite + F_penibilite
```

- **Aucune récupération issue d'un excédent EF** : si `E_EF >= E_qual`, `F_exces_qualite = 0`.
- Exemples avec 14 dépensés : 8 EF / 6 Qualité → surcharge de déséquilibre 0 ; 6 EF / 8 Qualité → `2*alpha`.
- La composante de blackjack est **fixée au lancer**, puis les séances réalisées déterminent les composantes de programme ; un bust ne recalcule pas rétroactivement `F_blackjack`.
- Une éventuelle borne inférieure de fatigue, la persistance et l'arrondi de `alpha` restent OPEN.
- Attention au double comptage : `S` de Fatigue V1 (surcroît de risque `RPE−RPE Max`) et la pénibilité des séances ne doivent pas être cumulés aveuglément ; décider de les fusionner, conserver ou remplacer.

### Autorégulation du surentraînement

```text
tolérance = n (nombre de dés permanents : 4 / 5 / 6)
si F_t > tolérance :
    lancer n−1 dés actifs
    TN = TN(P), inchangé
    actions = Keep / Reroll
    réserve indisponible (y compris via tout motif D99)
sinon :
    lancer normal n−1 dés actifs
    actions = Keep / Reroll / Add / Add+Reroll
```

Hypothèse de restitution à valider : la réserve redevient disponible au premier tour **suivant** celui où la fatigue retombe à `F <= n`. Ne pas créer un cycle de retrait permanent sans période de récupération ; un seul dé de réserve neutralisé pour le premier prototype, sans blessure additionnelle.

**Attention :** le résultat normal avec 4d6 comporte déjà 3 dés actifs et une réserve ; le surentraînement **ne réduit pas à 2 dés actifs**, il supprime l'accès à la réserve. TN reste 14.

## 4. D99 remanié — proposition de règle

### 4.1 Fonction individuelle

- Conserver les **motifs combinatoires du lancer final** comme mécanisme d'accès à `n` dés retenus plutôt que `n−1` lorsque cela est permis.
- Ne plus utiliser les motifs D99 comme **plafond du nombre de séances Qualité** dans la variante D1.
- Les règles d'accès à la réserve doivent rester cohérentes avec `Keep/Reroll/Add/Add+Reroll` et avec sa neutralisation en surentraînement.
- Les tableaux exacts d'accès à `n` dés par motif sont à vérifier ; ne pas inventer de nouveau bonus automatique.

### 4.2 Fonction coopérative — intention retenue

**Coopération spontanée/opportuniste, sans phase de négociation imposée.**

- Les joueurs peuvent communiquer leurs résultats/motifs au fil de la phase de dés (« Qui a fait un brelan ? », « Si tu tentes le brelan, on peut obtenir le bonus ensemble »).
- Chacun conserve le choix de son action sur les dés et peut tenter d'obtenir une concordance.
- **Seuls les joueurs qui partagent effectivement un motif choisi bénéficient du bonus de ce groupe**. Pas de bonus distribué à tous les participants de la partie.
- La concordance porte sur le **type de figure** (paire, brelan, etc.), **indépendamment de la valeur des faces et du nombre total de dés lancés**. Un brelan obtenu sur trois dés peut correspondre à un brelan contenu dans un lancer de cinq dés.
- Si un tirage contient plusieurs motifs admissibles (ex. `full = paire + brelan`), son propriétaire **choisit un seul motif pour la coopération de ce tour**. Il ne reçoit pas plusieurs bonus via des groupes différents.
- Exemple : A obtient un full, B une paire, C un brelan. **A peut choisir de s'associer à B via « paire » OU à C via « brelan », mais pas aux deux**. Le groupe non choisi ne reçoit pas de bonus sur la base du tirage de A.
- La déclaration du motif coopératif n'interdit pas d'utiliser la figure complète pour la fonction individuelle de D99 ; ces deux fonctions sont distinctes.
- Pas de relance supplémentaire ni de transfert de ressources créé uniquement pour obtenir la coopération : les coûts d'opportunité viennent de la décision de dés elle-même.

**Questions OPEN** : vocabulaire exact des figures admises et décomposition (deux paires, carré, cinq identiques), possibilité de former plusieurs groupes disjoints, ordre d'annonce et verrouillage simultané, bonus concret (léger, positif, non dominant), résolution des cas où un motif pourrait être partagé avec plusieurs joueurs. La convention minimale « un motif coopératif déclaré par joueur et par tour » reste la règle candidate.

## 5. Portefeuille et construction du programme

- Catalogue général → options éligibles selon le profil physiologique → **acquisitions personnelles** aux jalons.
- La carte représente une **option permanente** ; les ressources du tour et les règles de composition déterminent les occurrences réalisées.
- Hypothèse de dimensionnement : environ **5–6 cartes au départ** et **8–10 en fin de Training** ; **pas de plafond de possession validé**. Débuter sans plafond strict et mesurer la charge cognitive.
- Pas de coût additionnel en dés pour acquérir une carte, conformément à l'allocation unifiée ; il reste à définir si l'acquisition a d'autres contreparties.
- Répétition d'EF et unicité d'une entrée Qualité par tour : **références CURRENT provisoires**, non résolues pour les cartes spécifiques.
- La **SL** reste une vraie séance, potentiellement coûteuse et intrinsèquement fatigante, avec adaptation d'endurance longue distincte d'une simple EF ; effet sur Reserve/durée en Race à tester.
- **SPEC** est transversal : une séance EF/Seuil/VMA/SL peut porter une adaptation SPEC (pistes Vitesse/Économie expérimentales). Ni quatrième capacité obligatoire ni bonus universel acquis.
- Les gains multidimensionnels par séance sont recherchés ; tout chiffre de coût/contribution montré en conversation était **illustratif**, non validé.

## 6. État des règles techniques vérifiées — ne pas confondre avec D1

Sources dépôt (GDD V2, CURRENT_STATE, code principal au 16-10-2026) :

- **CURRENT :** 4d6 initiaux ; un dé de réserve en général ; TN = espérance du pool permanent entier ; énergie = somme des valeurs retenues (pas plafonnée au TN) ; D99 borne actuellement les qualités (SL comprise), `Qualités ≤ EF`, sept séances au maximum, qualités uniques/EF répétables, RPE Max et risque de bust.
- **CURRENT :** volume/CTL réellement réalisé pour le développement du pool, qualités réussies pour les upgrades ; les séances réussies après bust/redistribution comptent.
- **GDD Fatigue V1 EXPERIMENTAL :** `Δ = E_realisée − TN`, composantes `Q + S + Recovery`, et borne inférieure de fatigue. **Cette base n'est pas la formule D1 souhaitée** (qui utilise le résultat des dés pour le blackjack).
- **Code `decision_engine.py` :** `energy_and_fatigue` applique une quasi-Fibonacci différente des tables du GDD ; `simulate_player.py` l'utilise sur `resolution.energy_effective`, puis cumule la fatigue sans imposer directement de conséquence aux tours suivants.
- **Code `session_selector.py` :** contrainte dure `Qualités ≤ EF` et priorité technique préalable accordée à SL ; ces choix techniques ne représentent pas une politique humaine normative.
- **Historique :** un retrait temporaire de dé a bien été expérimenté ; le GDD consolidé précise que ses anciens seuils/tables ne sont **pas CURRENT**. L'intention D1 a été re-précisée par le joueur.
- **Race V2 :** moteur `PhysiologyProfile(EF, Seuil, VMA)` intégré, conversion Training → profil absente, SPEC non intégrée, calibration de Reserve/Fatigue/SL toujours ouverte.
- **Audit de dominance** : si fatigue blackjack dépend de l'énergie des séances, un budget élevé peut être partiellement abandonné pour éviter le dépassement du TN. D1 corrige cette faille en calculant la composante blackjack sur le **résultat de dés**, et en régulant séparément l'excès qualitatif du programme.

## 7. Plan de validation minimal (sans campagnes lourdes)

**Étape A — Vérification locale et déterministe**

1. Fixer une courbe blackjack candidate (tables Fatigue V1 vs fonction quasi-Fibonacci), sans fusion silencieuse.
2. Réduire D99 à la disponibilité `n / n−1` et étudier tous les motifs, y compris 3 vs 5 dés pour la coopération.
3. Énumérer les actions Keep/Reroll/Add/Add+Reroll ; comparer décision optimale sous fatigue calculée **sur résultat de dés**, plutôt que sur énergie réellement dépensée.
4. Tester le surentraînement pour pools 4/5/6 : même TN, même nombre de dés actifs, absence de Add/Add+Reroll, restitution de réserve.

**Étape B — Comparaison de 2–3 programmes légaux par état**

1. Reprendre les contraintes RPE Max/bust, budget, répétition et nombre de séances comme contrôles témoins.
2. Comparer `Qualités ≤ EF` CURRENT versus suppression du quota + surcharge `max(0,E_qual−E_EF)`.
3. Vérifier l'effet du choix EF majoritaire : pas de récupération de répartition ; seules les qualités excessives ajoutent de la fatigue.
4. Tester SL et SPEC à valeurs neutres puis avec effets candidats : ne pas masquer l'équilibrage blackjack.

**Étape C — Trajectoires courtes**

1. Tester sur **3, 6 puis 12–16 tours** les stratégies intensives, équilibrées et EF-dominantes, sur seeds partagées et budgets de test modérés.
2. Mesurer progression physiologique, fatigue, fréquence/durée de perte de réserve, taux de restitution, fréquence d'Add, temps/complexité des programmes, bénéfices des cartes acquises.
3. Détecter en priorité : stratégie « toujours Add », saturation des qualités, récupération trop facile ou impossible, oscillation autour du seuil, bonus collectif dominant.
4. Isoler l'effet de la coopération D99 par une comparaison bonus off/on et des joueurs indépendants/coordonnés. Ne jamais prétendre à une profondeur stratégique validée sur la seule base des politiques techniques.

## 8. Questions OPEN prioritaires

1. **Courbe de fatigue blackjack :** quelles valeurs conserver ? `f(R−TN)`, et non `f(E_realisée−TN)`.
2. **Excès de qualité :** choix `alpha`/arrondi, classification énergétique de SL et de ses éventuels effets intrinsèques.
3. **Fatigue persistante :** borne basse, restitution de la réserve après récupération, moment de vérification du seuil, interactions avec bust et upgrades.
4. **D99 :** table des accès au dé de réserve après retrait du plafond Qualité ; définition exacte des figures coopératives ; bonus coopératif, non cumulable pour un joueur sur plusieurs motifs.
5. **Portefeuille :** cadence précise des acquisitions, tailles, séances initiales et critères de déblocage.
6. **Training → Race :** représentation des contributions des séances EF/Seuil/VMA/SL/SPEC, calibration Reserve/Cost.

## 9. Hors portée de ce document

Aucune modification de GDD CURRENT, aucun changement de code de production, aucun réglage numérique promu comme normatif, aucune affirmation que le moteur V2 intégré implémente déjà ces règles. Ce document sert de référence de discussion et de harnais pour une PR de prototypage ultérieure.
