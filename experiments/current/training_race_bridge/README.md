# Training V2 → Race V2 minimal bridge


> **EXPERIMENTAL SPEC PROBE — SPEC IS OPEN / NOT IMPLEMENTED.** This is not
> the integrated V2 baseline. SPEC is
> OPEN and not implemented in the active Race V2 path; Position, Efficacité and
> AS42/AS21/AS10/AS5 below are preserved experimental conventions only.

**EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN**

This isolated probe connects synthetic Training V2 SPEC allocations to the
existing experimental Race Engine V2 primitives. It changes neither production
code nor CURRENT tests, and it does not simulate training longitudinally.

## Scope and fixed fixtures

- Two contexts only: AS42 starts at 17 (`15 EF < 17 < 21 Seuil`) and AS10 at
  22 (`21 Seuil < 22 < 27 VMA`). These are probe parameters, not design values.
- One shared physiology (EF 15, Seuil 21, VMA 27), `6d6` pool, Curve B, six
  flat segments, CTL 100, freshness 0, and FORM_PATTERN.
- 20 shared seeds × 2 contexts × 3 builds = 120 courses.
- Four SPEC tiers per build: SPEED 4/0, BALANCED 2/2, ECONOMY 0/4
  (POSITION/EFFICIENCY). Impossible tiers are reported, never converted.
- `ECO_MAX = min(C0(AS)-C0(EF), C0(VMA)-C0(AS))`; effective ECO is capped by
  that envelope and applies at the exact active AS only. The cost floor is C0(EF).

## Reuse and experimental adapter

The harness imports the unchanged Race Engine V2 dice generation, persistent
pool fixture, subset enumeration, form classification, reserve mapping and
Curve B cost function. Since its normative runner has no cost-adapter hook, the
local runner preserves its segment order and reserve-finalization rule while
injecting effective cost only at exact AS.

`SPEC_TARGET_SUSTAINABLE` is the sole experimental policy. It selects the
highest rolled subset Production at or below active AS that leaves one EF-cost
unit per future segment; if none is sustainable it selects the cheapest payable
option. It contains no build label or bonus. Ties are deterministic. POSITION
changes only its AS target; it does not change pool, roll, reserve, freshness or
difficulty.

Run:

```bash
python -m experiments.current.training_race_bridge.harness
python -m unittest experiments.current.training_race_bridge.test_harness -v
```

`results.json` contains protocol, synthetic athletes, aggregate metrics, all
required seed-paired differences, and per-course traces.


## Training B → Race V2 — direct integration

The files `training_b_adapter.py`, `training_b_race_harness.py` and
`test_training_b_adapter.py` add a separate direct integration path from the
actual `training_v2.PlayerState` / completed Training B trajectory snapshot.

- EF, Seuil and VMA are copied one-to-one into Race V2's
  `PhysiologyProfile`; no hidden scale conversion is applied.
- The persistent Training B die sizes are copied one-to-one into Race V2's
  `DicePool`.
- A 16-turn Training B trajectory is then passed to Race V2 and resolved over
  six race segments. The harness runs three seeds across balanced, EF and
  quality training heuristics (nine paired preparation/race cases).
- CTL, freshness and long-run preparation remain explicit Race V2 inputs. The
  harness uses CTL 100, freshness 0 and no long-run preparation as declared
  experimental fixtures, not as Training B conversions.

Run:

```bash
python -m experiments.current.training_race_bridge.training_b_race_harness
python -m unittest experiments.current.training_race_bridge.test_training_b_adapter -v
```

**Calibration gap:** Training B's initial profile is EF 6 / Seuil 8 / VMA 10,
whereas prior Race V2 calibration probes commonly used EF 15 / Seuil 21 /
VMA 27. The adapter deliberately preserves the Training B values instead of
inventing a scale factor. Race completion and reserve adequacy must therefore
be evaluated before treating this vertical slice as balanced. The earlier
synthetic SPEC probe above remains separate and is not evidence of Training B
integration.
