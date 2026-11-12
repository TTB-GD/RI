# Run It

Run It est un jeu tactique de préparation à la course. Le joueur construit une
préparation physiologique et un pool de dés pendant le Training, puis met ce
profil à l'épreuve dans une course où il arbitre dépense, soutenabilité et
opportunités tactiques.

## État du projet

- **Training :** Training B est la cible de développement validée ; son prototype
  est encore partiel et n'est pas encore raccordé de bout en bout à Race.
- **Race V2 :** les règles sont consolidées dans le GDD et dans
  [la spécification détaillée](docs/game-design/RACE_V2_DESIGN.md). Un prototype
  expérimental multi-secteur, incluant dés et relances, existe dans
  `experiments/current/race_v2_prototype/`.
- **Intégration :** aucune boucle complète Training B → Race V2 n'est revendiquée.
  Le profil physiologique, l'AS, le crédit initial de soutenabilité `S0` et le
  palier d'affûtage doivent encore être dérivés d'un état Training réel.
- **Équilibrage :** les calibrations et les expériences restent distinctes des
  règles validées.

## Sources de référence

| Besoin | Document |
|---|---|
| Règles normatives et décisions validées | [Run It - GDD.md](Run%20It%20-%20GDD.md) |
| Spécification détaillée Race V2 | [docs/game-design/RACE_V2_DESIGN.md](docs/game-design/RACE_V2_DESIGN.md) |
| État exact du code | [CURRENT_STATE.md](CURRENT_STATE.md) |
| Ordre des chantiers et écarts | [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) |
| Historique des divergences documentaires | [DOCUMENTATION_AUDIT.md](DOCUMENTATION_AUDIT.md) |

## Règle de gouvernance

Une décision de design n'implique pas son implémentation. Un prototype ou un
harness expérimental ne transforme pas une hypothèse en règle validée. En cas
de divergence, les décisions utilisateur explicites et le GDD prévalent pour le
design ; le code et CURRENT_STATE décrivent séparément le comportement réel.
