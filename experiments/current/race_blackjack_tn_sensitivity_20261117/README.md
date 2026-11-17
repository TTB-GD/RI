# Reproduction

Depuis ce dossier :

```bash
python simulate_tn_sensitivity.py --runs 50000 --seed 20261117 --output results.json
```

Le modèle conserve une courbe énergie–soutenabilité fixe (EF=9, VMA=17). Le TN ne fait que plafonner la cible Blackjack du joueur ; la cible effective est le minimum entre TN et la cible de gestion long terme. Les résultats et limites sont détaillés dans `REPORT.md`.

Dépendance : NumPy.
