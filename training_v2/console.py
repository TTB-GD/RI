"""Minimal interactive console for one-player Training V2 playtests.

This is a thin interface over the experimental rules engine. It does not
introduce an AI policy, alter costs, or mutate state before a choice is made.
"""
import random

from .engine import roll_pool, resolve_turn
from .programs import list_program_options
from .state import PlayerState


def _format_option(index, option):
    ef_dice = ", ".join(str(i + 1) for i in option.ef_indices)
    q_dice = ", ".join(str(i + 1) for i in option.quality_indices)
    qualities = ", ".join(option.qualities) if option.qualities else "aucune"
    costs = ", ".join(f"{name} {cost}" for name, cost in option.quality_costs)
    if not costs:
        costs = "aucun"
    return (
        f"{index}. EF dés [{ef_dice}] = {option.ef_energy} | "
        f"Q dés [{q_dice}] = {option.quality_energy} | "
        f"séances: {qualities} | coûts: {costs} | "
        f"SPEC restant: {option.spec_remainder}"
    )


def play_turn(state, *, input_fn=input, output_fn=print, rng=None, risk_faces=()):
    """Run one roll -> enumerate -> player choice -> resolution cycle.

    Returns the engine TurnResult. The supplied PlayerState is updated in place.
    input_fn and output_fn are injectable so the interaction can be tested
    without a terminal.
    """
    rng = rng if rng is not None else random.Random()
    roll = roll_pool(state, rng=rng)
    options = list_program_options(state, roll)
    if not options:
        raise RuntimeError("aucun programme valide pour ce lancer")

    output_fn(f"Tour {state.turns_played + 1} — lancer")
    output_fn(f"Dés conservés: {roll.final_values} | TN: {roll.tn:.1f}")
    output_fn("Programmes accessibles:")
    for index, option in enumerate(options, start=1):
        output_fn(_format_option(index, option))

    while True:
        raw_choice = input_fn(f"Choisir un programme (1-{len(options)}): ")
        try:
            selected_index = int(raw_choice) - 1
        except (TypeError, ValueError):
            output_fn("Saisie invalide: entrer un numéro.")
            continue
        if 0 <= selected_index < len(options):
            break
        output_fn(f"Choix invalide: entrer un numéro entre 1 et {len(options)}.")

    choice = options[selected_index]
    result = resolve_turn(
        state,
        roll.raw_faces,
        choice.ef_indices,
        choice.quality_indices,
        choice.qualities,
        risk_faces=risk_faces,
        rng=rng,
    )

    output_fn("Résolution:")
    output_fn(
        f"EF +{result.ef_energy} | Q réussie: {result.successful_qualities or 'aucune'} "
        f"| Q échouée: {result.busted_quality or 'aucune'} "
        f"| SPEC +{result.progression_spec_gained}"
    )
    output_fn(
        f"Profil EF/Seuil/VMA: {state.profile.ef}/{state.profile.threshold}/"
        f"{state.profile.vma} | progression EF/Q/SPEC: "
        f"{state.progression_ef}/{state.progression_q}/{state.progression_spec}"
    )
    output_fn(
        f"Fatigue: {result.fatigue_after} | dés au prochain tour: "
        f"{result.dice_pool_after}"
    )
    return result


def run_session(*, input_fn=input, output_fn=print, rng=None):
    """Run consecutive turns while preserving the same player's state."""
    rng = rng if rng is not None else random.Random()
    state = PlayerState()
    while True:
        play_turn(state, input_fn=input_fn, output_fn=output_fn, rng=rng)
        answer = input_fn("Entrée pour le tour suivant, q pour quitter: ")
        if isinstance(answer, str) and answer.strip().lower() == "q":
            return state


def main():
    run_session()


if __name__ == "__main__":
    main()
