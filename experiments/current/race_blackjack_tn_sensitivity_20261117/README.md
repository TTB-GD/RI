# Reproduction

## Simulateur monolithique : pools de dés × profils de soutenabilité

Le fichier `simulate_tn_sustainability_sensitivity.py` est autonome et n'utilise que la bibliothèque standard Python. Il embarque directement les **33 pools de dés** et les **27 profils de soutenabilité** transcrits depuis `FEEDBACK.md`. Aucun fichier de données externe n'est requis.

### Vérification rapide

```bash
python simulate_tn_sustainability_sensitivity.py --self-test
python simulate_tn_sustainability_sensitivity.py --runs 1000 --pool-ids 1 --profile-ids "conf 3-2"
```

Le second exemple exécute les 18 cellules TN 9–14 × réserves 8, 16 et 24. Il produit un JSON et un CSV portant le même nom de base.

### Sélection des configurations

```bash
python simulate_tn_sustainability_sensitivity.py \
  --runs 50000 --seed 20261117 \
  --pool-ids 1 2 3 --profile-ids "conf 3-2" "conf 4-4" \
  --tns 9 10 11 12 13 14 --reserves 8 16 24 \
  --turns 8 --rerolls 8 \
  --output results.json --csv-output results.csv
```

- `--pool-ids` : identifiants de 1 à 33.
- `--profile-ids` : noms exacts des profils, par exemple `"conf 3-2"`.
- `--tns` : valeurs de TN (9 à 14 par défaut).
- `--reserves` : réserves initiales de soutenabilité (8, 16, 24 par défaut).
- `--ef-energy` : énergie à laquelle ancrer la première valeur de chaque profil (9 par défaut).
- `--turns`, `--rerolls`, `--runs`, `--seed` : paramètres de simulation.
- `--output`, `--csv-output` : chemins des exports JSON et CSV.

Pour éviter un lancement accidentel de plusieurs milliards de tours simulés, les valeurs par défaut sélectionnent uniquement le pool 1 et le profil `conf 3-2`. Les TN et réserves par défaut restent respectivement 9–14 et 8/16/24.

### Interprétation de la courbe

Le premier coût de chaque profil est positionné à l'énergie EF choisie par `--ef-energy`. Les valeurs suivantes s'appliquent aux énergies successives. Les profils conservent leur longueur réelle ; au-delà de leur dernière valeur, le dernier coût est maintenu. Sous EF, le coût est nul et l'énergie produite est plafonnée à EF−1. Le TN plafonne uniquement la cible Blackjack et ne déplace ni ne modifie la courbe.

### Règles de simulation

- Blackjack : lancer N−2 dés, puis ajouter les dés un par un ; chaque dé ne peut être relancé qu'une fois par tour.
- La réserve de relances est commune à toute la course ; une relance remplace le résultat précédent.
- La cible long terme est l'énergie la plus élevée dont le coût est compatible avec le budget moyen restant, puis plafonnée par le TN.
- Si le coût du résultat dépasse la soutenabilité restante, le tour produit EF−1 sans dépense de soutenabilité.
- Lorsque la réserve atteint exactement zéro, le dé ayant le moins de faces est retiré définitivement (d6 avant d8, d10 puis d12). Les tours suivants sont verrouillés à EF−1.

La politique est une heuristique explicite, pas un solveur optimal. L'hypothèse de retrait du dé le plus faible est documentée dans les métadonnées JSON.

## Expérience initiale

Les scripts et résultats de l'expérience initiale TN × courbe fixe sont conservés comme référence historique. Ils ne doivent pas être confondus avec les nouvelles simulations utilisant les 27 profils et les 33 pools.
