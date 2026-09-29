# Run It

Run It est un jeu tactique de préparation à la course : le joueur construit un
pool de dés, compose ses entraînements sous contraintes d'énergie et de risque,
puis convertit sa préparation en performance lors d'une course finale.

## Boucle actuelle

1. **Préparation** — le pool persistant commence à `4d6`. Le lancer fournit le
   budget d'énergie, la frontière sûre `RPE Max` et, via D99, le nombre maximal
   de qualités. EF est répétable ; les qualités font progresser le catalogue et
   les dés (`d6 → d8 → d10 → d12`). Le CTL ajoute un d6 aux seuils 50 et 100.
2. **Risque** — tenter une qualité au-dessus de `RPE Max` peut provoquer un
   bust. La séance busted ne produit ni CTL ni progression ; la redistribution
   post-bust en EF suit les règles détaillées du GDD.
3. **Course V2** — chaque segment choisit une Production. Sa Difficulty locale
   forme `Charge = Production + Difficulty`; le score gagne seulement la
   Production et la Réserve perd le coût physiologique de la Charge.

## Profil physiologique V2

La frontière intégrée entre un futur Training et Race V2 est un profil ordonné
`EF < Seuil < VMA` : EF est l'origine du coût, Seuil son changement de régime,
et VMA la borne haute du domaine physiologique intégré. La courbe native est
continue et utilise actuellement des pentes 2 puis 3. Ces deux valeurs sont une
**CALIBRATION EXPERIMENTAL**, pas un équilibrage définitif.

## Statuts importants

- **CURRENT / INTÉGRÉ :** profil EF/Seuil/VMA, calcul pur du coût, et résolution
  locale Production + Difficulty → Charge → coût / score.
- **EXPERIMENTAL :** pentes 2/3, construction de la Réserve, Form, politiques de
  course, Fatigue V1 et politiques automatiques d'entraînement.
- **OPEN :** légalité et coût au-dessus de VMA, conversion complète du Training
  vers le profil, rôle concret de SL en course et SPEC. SPEC n'est pas implémenté
  dans le chemin Race V2 ; Position, Efficacité et AS42/AS21/AS10/AS5 ne sont pas
  des mécanismes actifs de cette baseline.

Le document normatif et les distinctions de statut se trouvent dans
[`Run It - GDD.md`](Run%20It%20-%20GDD.md). L'état exact du prototype est résumé
dans [`CURRENT_STATE.md`](CURRENT_STATE.md).
