# Notes de nettoyage

## Passe 2 — simplification + sortie structurée

**Supprimé :**
- `action_evaluator.py` (ancien système à seuils sur l'écart au TN) : n'était
  gardé que pour comparaison dans les logs, plus utilisé nulle part comme
  décision effective. Le moteur pondéré (`decision_engine.py`) est désormais
  la seule source de décision.
- `pattern_probabilities.py` : n'était importé que par `action_evaluator.py`
  (analyse exploratoire non branchée à la décision). Supprimé avec lui.

**Simplifié :**
- `decision_engine.py` : `print_weighted_analysis()` (formatage console) a
  été remplacé par `rank_to_records()`, une fonction pure qui retourne des
  dicts plats — même information, mais exploitable en dehors de la console.

**Nouveau : sortie structurée (`game_logger.py`)**

Tous les `print()` de debug de `main.py` sont remplacés par deux fichiers
CSV générés à chaque run :

- **`turns.csv`** — une ligne par tour joué : TN, motif initial/final,
  action choisie, séances/énergie/fatigue obtenues, et `utility_gap` (écart
  d'utilité entre le meilleur choix et le second, un indicateur direct de
  "à quel point la décision était évidente" — utile pour repérer si le
  moteur hésite beaucoup sur certaines configurations).

- **`decisions.csv`** — une ligne par option évaluée à chaque tour (keep,
  chaque reroll possible, add, chaque add+reroll), avec ses métriques
  attendues et son utilité. C'est l'espace de décision complet : permet de
  voir si certaines options sont systématiquement dominées, de tracer
  l'effet d'un changement de poids (`w_energy`, `w_sessions`, `w_fatigue`,
  `w_rpe`) sur les choix, etc.

Les deux tables partagent la colonne `turn`, donc jointes facilement dans
un tableur ou pandas pour croiser "quelle était la meilleure alternative
non retenue" avec le résultat effectif du tour.

Pour lancer une simulation avec d'autres paramètres :

```python
from main import run_simulation
from game_logger import write_csv

turns, decisions = run_simulation(n_turns=200, weights={
    "w_energy": 1.0, "w_sessions": 1.5, "w_fatigue": 2.0, "w_rpe": 0.5,
})
write_csv("turns.csv", turns)
write_csv("decisions.csv", decisions)
```


## Fichiers supprimés (code mort confirmé)

- **`game_state.py`** (classe `GameState`) : définie mais jamais instanciée
  ni importée nulle part dans le projet. `decision_engine.py` et `main.py`
  font circuler l'état sous forme de variables séparées (`active`, `faces`,
  `values`, `tn`, `max_dice`...), pas via cette classe.

- **`action_simulator.py`** (fonctions `simulate_keep`, `simulate_add`,
  `simulate_reroll`, `simulate_add_reroll`, `simulate_action`) : jamais
  importées ni appelées. `decision_engine.py` réimplémente sa propre
  énumération des issues via `_enumerate_outcomes()`, indépendamment de
  ce module.

Vérifié par recherche de références (`grep`) sur tout le projet avant
suppression : aucune occurrence de `GameState`, `game_state`,
`action_simulator` ou `simulate_*` en dehors de ces deux fichiers.

Le projet a été ré-exécuté après suppression (`python3 main.py`) : sortie
identique, aucune régression.

## Ce qui reste à trancher (pas fait ici, décision de conception)

Ces deux fichiers ont un rôle qui *pourrait* redevenir utile :

- `GameState` pourrait remplacer les tuples/dicts actuels si vous voulez
  typer proprement l'état du tour (utile dès que le projet grossit ou
  qu'une UI/API vient consommer cet état).
- `action_simulator.py` fait un travail proche de celui de
  `decision_engine._enumerate_outcomes`, mais retourne des états complets
  (avec pattern/session) plutôt que juste les faces. S'il doit revenir,
  il faudrait fusionner les deux plutôt que les garder en parallèle
  (aujourd'hui ils dupliquent la même logique d'énumération).

Je n'ai pas tranché cette question à votre place — juste supprimé le code
qui n'était appelé par rien. Dites-moi si vous préférez plutôt intégrer
ces deux fichiers que les supprimer, et je referai le nettoyage dans ce sens.
