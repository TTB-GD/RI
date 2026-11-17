# Reproduction

## Analyse TN × réserve de soutenabilité

Le script autonome `simulate_tn_sustainability_sensitivity.py` utilise uniquement la bibliothèque standard Python (aucune dépendance à installer).

Depuis ce dossier :

```bash
python simulate_tn_sustainability_sensitivity.py --runs 50000 --seed 20261117 --reserves 8 16 24 --turns 8 --rerolls 8 --output tn_sustainability_sensitivity_results.json
```

Cela lance 18 configurations (TN 9 à 14 × réserves 8, 16 et 24), soit 900 000 courses avec les paramètres par défaut. Le script affiche un tableau récapitulatif dans le terminal et écrit les résultats détaillés, intervalles de confiance compris, dans le JSON.

Les paramètres sont modifiables :
- `--runs` : nombre de courses par configuration ;
- `--seed` : graine de base ;
- `--reserves` : une ou plusieurs réserves initiales ;
- `--turns` : nombre de tours ;
- `--rerolls` : réserve commune de relances ;
- `--output` : chemin du JSON de sortie.

Chaque couple réserve/TN utilise un flux aléatoire déterministe indépendant, dérivé de la graine de base. Les résultats sont donc reproductibles et l'ajout d'une configuration ne décale pas les tirages des autres configurations.

## Modèle

La courbe énergie–soutenabilité reste fixe (EF=9, VMA=17). Le TN ne fait que plafonner la cible Blackjack ; la cible effective est le minimum entre TN et la cible de gestion long terme. La stratégie, les règles de relance et de perte de dé sont décrites dans le rapport de l'expérience.

Le script existant `simulate_tn_sensitivity.py` reproduit l'expérience initiale avec une réserve de 8. Le nouveau script permet de faire varier cette réserve sans dépendance externe.
