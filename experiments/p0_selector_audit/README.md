# Audit décisionnel P0 / session selector

## FACT

- Protocole : 100 seeds × 16 tours ; poids inchangés `{'w_energy': 3.0, 'w_sessions': 1.5, 'w_fatigue': 0.25, 'w_rpe': 0.25}`.
- Le log candidat complet est externe au dépôt : `/tmp/p0-selector-audit-candidates.csv`.
- L'instrumentation affirme à chaque tour l'identité de sa sélection avec `choose_sessions_weighted`.

## OBSERVATION

- Énergie moyenne disponible/utilisée/restante : 18.033125 / 14.702500 / 3.330625.
- Tours avec énergie restante et candidat légal/productif/sans OT immédiat : 68.0 % / 68.0 % / 68.0 % / 68.0 %.
- Q/S/Recovery moyens : 0.034375 / 0.000000 / -1.985000.
- `marginal_utility_negative`: 1088 tours (68.0 %).
- `no_energy_affordable`: 512 tours (32.0 %).
- Meilleur candidat rejeté : score moyen -0.171055, toujours EF, terme négatif dominant toujours `delta_fatigue_term`.
- Barrière RPE : 934 observations, 750 compétitives, 750 premières, S potentiel cumulé 1312.
- Greedy contre optimum exact : 30 états, même utilité dans 30.0 %, écart moyen 1.598906, maximal 2.949405.

## INTERPRETATION

- La règle d'arrêt marginale explique directement 68 % des fins de sélection ; le coût de fatigue marginal domine les meilleurs rejets.
- L'écart à l'optimum de même utilité indique aussi un effet de l'ordre greedy/priorité SL, notamment lorsqu'une EF localement négative ouvrirait ensuite une séance de qualité.

## LIMITS

- Les 30 états exacts sont un échantillon déterministe (seeds 0–9, tours 1/8/16), pas tous les états.
- Le contre-factuel RPE est local et ne génère aucune trajectoire alternative.
- Cette politique simulée ne caractérise pas un joueur humain.

## DESIGN QUESTIONS

- Quelle part du comportement voulu doit relever de l'utilité globale, de la priorité SL et de l'arrêt marginal local ?
- La barrière RPE doit-elle rester analysée comme contrainte d'accès distincte des préférences du score ?
