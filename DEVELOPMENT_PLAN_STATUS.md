# Addendum au plan de développement — Porte B

> Mise à jour documentaire au 6 novembre 2026. Cet addendum complète les statuts B du `DEVELOPMENT_PLAN.md` après les PR #29, #30 et #31. Il ne modifie aucune règle de Game Design et ne change pas le statut de B3 sans preuve de clôture.

## Statut vérifié

- **B1 — DONE (PR #25).** `plan_validation.validate_plan(...)` et ses tests restent la base de validation des plans.
- **B2 — DONE (PR #30).** Les lignes de séances de `simulate_player.py` attribuent les traces par occurrence et identifient les séances issues de la redistribution EF (`origin`).
- **B3 — IN PROGRESS.** Les tests D99 table-driven restent à compléter/valider pour chaque ligne CURRENT à 4/5/6 dés et à maintenir distincts de la politique ouverte à 3 dés. Ne pas déclarer la couverture complète sans vérifier les cas et leur exécution CI.
- **B4 — DONE côté implémentation et couverture de base (PR #29, #30, #31).** `Die.roll`, le contrôle du bust et la simulation Training acceptent un RNG injectable/local ; les tests ajoutés couvrent le rejeu de lancers et de simulation avec une seed, ainsi que l’absence de mutation de l’état aléatoire global. Cela garantit le rejeu dans le même environnement logiciel, sans promettre une séquence identique entre versions de Python.
- **B5 — DONE pour les invariants actuellement testés (PR #31).** Les tests couvrent les paliers CTL 50/100, l’ajout unique et plafonné de dés, les seuils et le plafond des améliorations, ainsi que l’application des gains au début du tour suivant. Ils vérifient les règles d’état sans spécifier la politique de sélection gloutonne.

## CI et portée des preuves

Le workflow `.github/workflows/tests.yml` exécute `python -m unittest discover -s tests -v`. Les fichiers de tests Training placés dans `tests/` sont donc découverts automatiquement ; aucun ajout séparé de commande n’est nécessaire pour ces tests unitaires. Les résultats d’exécution doivent être consultés dans les checks GitHub de la PR correspondante : la présence d’une commande CI ne suffit pas à prouver que les checks ont réussi.

Les tests B4/B5 sont des tests de régression du comportement CURRENT, pas une décision de design, ni une validation d’équilibrage. La policy de remplacement EF demeure une policy de simulation.

## Prochaines actions recommandées

1. Terminer l’audit de B3 et confirmer que les tests de toutes les lignes requises passent en CI ; garder la table à 3 dés explicitement OPEN.
2. Après B3, reprendre C1 puis C2 comme indiqué par la dépendance de gouvernance ; ne pas choisir A/B/C avant validation de la vision Game Design.

---

Ce document est un addendum de statut. En cas de divergence avec le tableau de `DEVELOPMENT_PLAN.md`, les statuts B ci-dessus reflètent les PR fusionnées citées dans l’en-tête ; le plan principal devra être consolidé lors d’une prochaine édition documentaire.
