"""
Journalisation structurée des simulations, pensée pour l'analyse game design
(tableur/notebook) plutôt que pour la lecture console.

Deux niveaux de granularité, volontairement séparés en deux fichiers :

- turns.csv     : une ligne par tour joué. Vue "résultat" : ce qui a été
                   décidé et obtenu au final. Utile pour des stats globales
                   (distribution d'énergie/fatigue/séances sur N tours,
                   fréquence de chaque action choisie, etc.).

- decisions.csv : une ligne par option ÉVALUÉE à chaque tour (keep, chaque
                   reroll, add, chaque add+reroll), avec son utilité et ses
                   métriques attendues. Vue "espace de décision" : permet de
                   voir à quel point un choix était net ou serré, quelles
                   options sont systématiquement dominées, etc. — essentiel
                   pour ajuster les poids (w_energy, w_sessions, w_fatigue,
                   w_rpe) en connaissance de cause.

Format volontairement simple (CSV via la stdlib, pas de dépendance externe)
pour rester facile à ouvrir dans un tableur ou à charger avec pandas plus
tard si besoin.
"""
import csv


def _format_value(value):
    """
    Convertit une valeur Python en représentation lisible par Excel FR :
    - float -> virgule décimale ("22.5" -> "22,5"), sinon Excel importe le
      nombre comme du texte (pas de tri/calcul possible) même si le
      séparateur de colonnes est correct.
    - bool -> VRAI/FAUX (reconnus nativement par Excel FR, contrairement à
      True/False qui seraient importés comme texte).
    - None -> chaîne vide plutôt que la chaîne littérale "None".
    """
    if isinstance(value, bool):
        return "VRAI" if value else "FAUX"
    if isinstance(value, float):
        return str(value).replace(".", ",")
    if value is None:
        return ""
    return value


def write_csv(path, rows, delimiter=";"):
    """
    Écrit une liste de dicts en CSV. Ne fait rien si `rows` est vide.

    Réglages pensés pour une lecture directe et exploitable dans Excel
    (notamment en localisation FR, cible principale pour l'analyse game
    design ici) :
    - delimiter=";" : Excel FR utilise la virgule comme séparateur décimal,
      donc un CSV séparé par virgules s'ouvre en une seule colonne au lieu
      d'une colonne par champ. Le point-virgule évite ce problème.
    - encoding="utf-8-sig" : ajoute un BOM UTF-8, qu'Excel utilise pour
      détecter l'encodage. Sans lui, les caractères accentués peuvent
      s'afficher incorrectement selon la version d'Excel.
    - _format_value() : convertit décimales et booléens au format attendu
      par Excel FR, pour que les colonnes numériques restent calculables
      (somme, moyenne, tri) une fois importées, pas juste lisibles.
    """
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: _format_value(v) for k, v in row.items()})
