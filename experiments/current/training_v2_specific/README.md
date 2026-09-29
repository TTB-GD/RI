# Training V2 — rôle du Spécifique

**EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN.**

Expérience isolée D1–D3 sur une chaîne où EF/Seuil/VMA ouvrent seulement les
frontières physiologiques, tandis que SPEC seul modifie les comparaisons de
coût de course. Le harnais réutilise la résolution de lancer, les coûts de
qualité et Curve B des expériences existantes, sans modifier la production, le
GDD, Fatigue V1, Race Engine V2, ni le harnais Training V2 minimal.

Conventions expérimentales principales : AS42 commence à 7, AS10 à 9; une
saturation Vitesse force ECO; chaque qualité est tentée au plus une fois par
tour; le choix de partition maximise Q avec tie-break déterministe; C2 arrondit
le demi-bonus ECO à l'entier supérieur. Le rapport distingue les règles locales
des observations et de leur interprétation.

```bash
python -m experiments.current.training_v2_specific.harness
python -m unittest experiments.current.training_v2_specific.test_harness -v
```

`results.json` contient les agrégats reproductibles (seeds 0–49), les six états
D2 et la grille déterministe D3. `REPORT.md` contient la synthèse décisionnelle.
