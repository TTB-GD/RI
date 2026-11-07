"""Minimal interactive console for one-player Training B playtests."""
import random

from .engine import roll_pool, resolve_turn
from .programs import list_program_options
from .state import PlayerState


def _format_option(index, option):
    parts = []
    for allocation in option.allocations:
        dice = ",".join(str(i + 1) for i in allocation.die_indices)
        parts.append(f"{allocation.session_key}[{dice}]={allocation.energy}")
    return (
        f"{index}. " + " + ".join(parts)
        + f" | EF {option.ef_energy} / Qualité {option.quality_energy}"
        + f" | coûts {option.session_costs}"
    )


def play_turn(state, *, input_fn=input, output_fn=print, rng=None, risk_faces=()):
    rng = rng if rng is not None else random.Random()
    roll = roll_pool(state, rng=rng)
    options = list_program_options(state, roll)
    if not options:
        raise RuntimeError("aucun programme valide pour ce lancer")
    output_fn(f"Tour {state.turns_played + 1} — lancer")
    output_fn(f"Dés conservés: {roll.final_values} | TN: {roll.tn:.1f}")
    output_fn("Compositions de séances accessibles:")
    for index, option in enumerate(options, start=1):
        output_fn(_format_option(index, option))
    while True:
        raw_choice = input_fn(f"Choisir une composition (1-{len(options)}): ")
        try:
            selected_index = int(raw_choice) - 1
        except (TypeError, ValueError):
            output_fn("Saisie invalide: entrer un numéro.")
            continue
        if 0 <= selected_index < len(options):
            break
        output_fn(f"Choix invalide: entrer un numéro entre 1 et {len(options)}.")
    result = resolve_turn(
        state, roll.raw_faces, options[selected_index].allocations,
        risk_faces=risk_faces, rng=rng,
    )
    output_fn("Résolution:")
    output_fn(
        f"Séances réussies: {[x.session_key for x in result.successful_sessions]} "
        f"| bust: {result.busted_session or 'aucun'}"
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
