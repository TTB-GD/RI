# DEVELOPMENT_PLAN_STATUS.md — addendum historique (supersédé)

> **Statut : ARCHIVÉ depuis le 6 novembre 2026.** Ce fichier est conservé pour
> la traçabilité de la consolidation de la porte B ; il n'est plus une source
> active de statuts. Le seul document de pilotage actif est
> [`DEVELOPMENT_PLAN.md`](DEVELOPMENT_PLAN.md).

## Historique de la mise à jour

Cet addendum avait été créé pour suivre les PR #25 et #29–#31. Son statut B3
était resté en retard sur les travaux fusionnés et sur la vérification CI.

Depuis sa rédaction :

- **B1 — DONE :** validation structurée indépendante du sélecteur (PR #25).
- **B2 — DONE :** traces par occurrence et origine de la redistribution
  (PR #28, consolidée dans le flux de simulation par PR #30).
- **B3 — DONE pour les signatures CURRENT à 4/5/6 dés :** les 23 signatures
  du GDD sont couvertes par des fixtures indépendantes dans
  `tests/test_d99_table.py`. Le workflow
  [Tests #42254642083](https://github.com/TTB-GD/RI/actions/runs/42254642083)
  a réussi sur `main` au commit `40151114`, le 6 novembre 2026. La convention
  à 3 dés reste séparément **OPEN / IMPLEMENTATION POLICY**.
- **B4 — DONE :** RNG local/injectable et tests de rejeu / isolation de l'état
  aléatoire global (PR #29–#31).
- **B5 — DONE pour les invariants testés :** transitions CTL, ajout de dés et
  progression des améliorations protégés par tests (PR #31).

## Référence active

Les statuts consolidés, les dépendances et les prochaines actions sont
maintenus exclusivement dans [`DEVELOPMENT_PLAN.md`](DEVELOPMENT_PLAN.md).
Ne pas réintroduire ici de tableau de statuts parallèle.

Cette archive ne modifie aucune règle de Game Design, aucune valeur CURRENT et
aucune convention expérimentale.
