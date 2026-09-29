# Run It — registre de consolidation documentaire

**Provenance :** registre initialement créé après la PR #7, puis actualisé le 29 septembre 2026 pour le jalon `Integrated V2 baseline` / PR #16. **Portée :** consolidation documentaire et suivi des divergences. Le GDD V2 décrit le design ; `CURRENT_STATE.md` décrit le prototype. Le registre conserve la preuve et le statut des divergences, sans remplacer les décisions de Game Design.

## Sources et méthode

- Décisions CURRENT du brief de consolidation et discussion « Audit éditorial du GDD » : notamment correction de la section 8, Q/Recovery séparés, charge post-bust, P0 et Standard Training Player.
- Dépôt : `AGENTS.md`, `CURRENT_STATE.md`, ancien `Run It - GDD.md`, `README.md`, `CLEANUP_NOTES.md` (historique de nettoyage) ; vérifications ciblées dans `session_effects.py`, `sessions_catalog.py`, `progression.py`, `session_selector.py`, `session_resolution.py`, `session_risk.py`, `simulate_player.py`, `dice_progression.py`, `dice_types.py`, `decision_engine.py`, les tests ciblés et `experiments/current/bust_trigger/README.md`.
- Autorité : décisions explicites > règles CURRENT du brief > snapshot `CURRENT_STATE.md` > ancien GDD > tests/code pour l'état implémenté > expériences historiques. Une divergence code/design n'est pas silencieusement résolue. Les anciennes propositions restent accessibles dans l'historique Git du GDD.

## Registre des divergences

| Sujet | Ancien état / source | CURRENT validé | État implémenté | Action documentaire | Statut |
|---|---|---|---|---|---|
| Pool et CTL | GDD D0–D3 sans seuils explicites ; README général | `4d6 → 5d6 → 6d6`, `n−1` dés actifs ; CTL 50/100, effet tour suivant | `dice_progression.py`, `simulate_player.py` | Expliciter seuils et délai | RESOLVED |
| D4, upgrades | GDD D4 et P3 décrivaient niveaux et bonus | Un upgrade par quatre qualités réussies, au plus quatre ; choix du dé | `dice_progression.py` applique les seuils ; choix du dé automatisé | Séparer progression de sa politique de sélection | RESOLVED / IMPLEMENTATION GAP |
| Bonus permanents | Ancien GDD D4/P3 et ancien README : `+1/+2/+3` | `0/0/0` ; aucun bonus permanent sur d8/d10/d12 | `dice_types.py` configure `0/0/0` | Classer les anciennes valeurs et moyennes comme HISTORICAL | RESOLVED |
| D5, énergie, récupération | GDD D5/P3/P4 : partage des dés ; sections « Réflexions » : énergie plafonnée TN | Énergie somme des valeurs retenues ; récupération via fatigue, sans ressource séparée | `session_effects.py`, `decision_engine.py` | Corriger les règles du tour ; ne pas reprendre les vieux exemples numériques | RESOLVED |
| D6 | GDD D6 décrivait « save a die » comme règle | FUTURE / EXPERIMENTAL | Pas de flux CURRENT du tour correspondant | Déclasser hors des règles CURRENT | FUTURE / EXPERIMENTAL |
| D99 | Tables GDD incohérentes entre lignes, sommes et effets (« séances » ambigu) | Plafond ferme de qualités incluant SL, connu avant composition ; slot perdu au bust ou annulation | `session_effects.py`, `session_selector.py`, `session_resolution.py` | Remplacer les effets contradictoires par table des motifs ; retirer anciennes probabilités comme références | RESOLVED |
| D99, trois dés finaux | Ancien GDD n'explicitait que 4/5/6 dés | Le brief ne valide pas une table autonome pour trois dés | `session_effects.py` extrapole un cas trois dés | Table signalée comme convention de prototype, à confirmer en design ; voir conflit ci-dessous | OPEN / IMPLEMENTATION POLICY |
| Composition, répétitions | GDD S1–S3 supposait fréquences fixes et moyennes anciennes | EF répétables, entrée qualité unique ; SL qualité unique ; qualités ≤ EF du tour ; maximum sept | `session_selector.py`, tests D99/bust | Remplacer fréquence prescriptive et chiffres périmés par contraintes | RESOLVED |
| Catalogue | Ancien GDD S0 peu précis sur graphe | Déblocage normal distinct de qualité tentable au successeur immédiat, prédécesseur débloqué et réussi ≥1 ; EF inchangées | `sessions_catalog.py`, `progression.py` | Formaliser distinction et exemple Spec6→Spec7 | RESOLVED |
| SPEC | Expériences Position / Efficacité et AS42/AS21/AS10/AS5 pouvaient être lues comme une future baseline | SPEC est OPEN et non implémenté dans Race V2 | Le catalogue Training conserve des entrées `Spec*`, mais le chemin intégré n’en dépend pas | Marquer ces travaux comme sondes EXPERIMENTAL d'une question OPEN et exposer l'écart du catalogue | OPEN / IMPLEMENTATION GAP |
| RPE Max | GDD S0/B0/B4 : risque selon RPE fixe ou historique | Zone sûre ; qualités tentables au-dessus admises ; EF au-dessus interdites | `session_selector.py` filtre et accepte qualité risquée | Retirer le vieux seuil et documenter le choix volontaire | RESOLVED |
| Trigger bust | GDD B4–B7 : historique et surentraînement influençaient « blessure » | `k = RPE − RPE Max`, face brute du meilleur dé **persistant**, bust `≤ k`, arrêt au premier ; `k ≥ taille` exclu ; modificateur neutre | `session_risk.py`, `simulate_player.py`; caractérisation dans `experiments/current/bust_trigger/` | Remplacer déclencheur et isoler modulation EXPERIMENTAL | RESOLVED |
| Post-bust | GDD B8 : séance annulée, énergie perdue et pénalité au tour suivant | Séance busted perd énergie et slot ; risques ultérieurs annulés, leurs slots perdus et énergie redistribuable en EF ; séances sûres maintenues | `session_resolution.py` résout ces conséquences | Décrire ordre, séances comptées/réussies et pertes | RESOLVED |
| Choix EF post-bust | Ancien GDD ne décrivait pas la redistribution | **Choix du joueur** sous énergie, EF accessibles, RPE et sept places | `session_resolution.py` expose les options et valide un choix vide, partiel, multiple ou répété sans choisir les EF | Aligner le GDD ; séparer une future UI de la frontière de règle implémentée | RESOLVED |
| CTL et dépense | GDD ancien confondait budget de dés, charge, fatigue par séance | CTL = somme des RPE réussis ; Q/Recovery basés sur charge réellement réalisée après bust/EF | `simulate_player.py` utilise `resolution.energy_effective` pour CTL et fatigue simple | Définir « réalisé » avec exclusion de l'énergie busted | RESOLVED |
| Fatigue V1 | Pas de section 8 consolidée dans ancien GDD ; ancienne fatigue par séance ou courbes contradictoires | EXPERIMENTAL ; Q, Recovery, S séparés, tables corrigées ; borne `−meilleur dé` | `decision_engine.energy_and_fatigue` calcule une courbe simple, `simulate_player.py` ne maintient pas la dette V1 complète | Ajouter §8 sans présenter les paramètres comme définitifs | EXPERIMENTAL / IMPLEMENTATION GAP |
| Surentraînement/blessure | GDD B1–B9 précisait seuils, dé retiré, risque accru et blessure durable | Système de blessure et seuils définitifs non validés ; test de bust indépendant de la fatigue | Expériences historiques distinctes ; pas de modulation CURRENT dans `session_risk.py` | Déclasser les anciennes tables et effets | HISTORICAL ONLY / OPEN |
| P0 et Standard Training Player | Ambiguïté de nom avec les rubriques GDD P0–P4 ; chiffres anciens | P0 baseline technique conservatrice ; Standard Training Player EXPERIMENTAL | `session_selector.py` et politiques d'expérience | Séparer politique technique et comportement humain | RESOLVED / EXPERIMENTAL |
| SL | Ancienne priorité implicite dans le GDD et explicite dans sélecteur | Qualité, max une, valeur surtout liée à la course | `_prioritize_long_run` lui donne une priorité technique | Exposer écart et laisser arbitrage de politique | IMPLEMENTATION / POLICY GAP |
| Course et personnages | GDD C1–C7, P0–P2 et README donnaient phases, scoring, blessures et objectifs précis | Noyau Race V2 local intégré ; orchestration, Réserve, Form, SL et objectifs encore EXPERIMENTAL / OPEN | `physiology.py` et `race_v2.py` implémentent profil, coût et segment | Documenter le noyau sans réintroduire Mental / Pacing / Physique | RESOLVED / PARTIAL OPEN |
| Anciennes probabilités et études | GDD D99/S2–S3 et README présentent valeurs/estimations anciennes | Aucune ancienne métrique n'est baseline après les changements | `CURRENT_STATE.md` classe les campagnes antérieures historiques | Enlever leur portée normative ; recalcul ultérieur seulement sur question précise | HISTORICAL ONLY |
| README | Synthèse ancienne : bonus permanents, récupération séparée, course et blessure spécifiées | Synthèse courte de la boucle et des statuts V2 | README aligné sur le noyau intégré | Retirer les règles historiques sans dupliquer le GDD | RESOLVED |

## Conflits et décisions encore nécessaires

### CONFLICT — extrapolation D99 à trois dés finaux

**Source A :** ancien GDD documente les tables à 4/5/6 dés ; le brief prescrit de conserver D99 validé sans fournir les partitions à trois dés. **Source B :** `session_effects.py` possède une table technique à trois dés, dont le commentaire la dit extrapolée. **Impact :** plafond de qualité de certains lancers sans dé ajouté. **Decision required :** confirmer explicitement ou ajuster cette extrapolation de design. La table du GDD présente l'état utilisé avec ce statut ouvert ; elle n'en fait pas une décision nouvellement validée.

### CONFLICT — priorité SL

**Source A :** SL doit prendre son intérêt surtout dans la course, dont les seuils restent ouverts. **Source B :** `_prioritize_long_run` la sélectionne prioritairement lorsqu'une EF et une SL sont abordables. **Impact :** trajectoires simulées et interprétation de la valeur d'une SL. **Decision required :** arbitrer la politique de sélection après définition minimale de la course.

## Limites de la consolidation

La section 8 présente les paramètres expérimentaux retenus pour Fatigue V1 et les corrections éditoriales de la discussion ; elle ne prétend pas que la production maintient déjà cette dette. Le GDD ancien contenait de nombreuses propositions et tables endommagées ou devenues obsolètes ; leur version exacte reste dans l'historique Git plutôt que dans le corps CURRENT. Aucun calcul de probabilité ou résultat d'expérience n'a été régénéré pour cette tâche.

**Prochaine tâche recommandée : GAME DESIGN — comportement de Charge au-dessus de VMA et frontières encore OPEN de Race V2.**
