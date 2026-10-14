# Training V2 minimal

**EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN.**

This isolated harness probes the proposed EF/Quality dice partition, true
multi-quality composition, Q-spent/SPEC accounting, 16-turn progression, and
Speed/Economy SPEC profiles. It imports only the existing D99 pattern signature
and Race Engine V2 Curve B cost boundary; it does not call or change the
production decision engine, Fatigue V1, or a complete race.

## A1 / F9 traceability status

The malformed artifact at the A1 audit HEAD had Git blob
`4186bd91c4c3ad71d6832277bc819fb791a2eb9d`: a duplicated opening for `B`
made the JSON invalid. The last intact artifact is Git blob
`1634c05364ccb51d37d8ad7fe25d744492a53fff` from commit `1f8ea1b`. A1 restored
that intact blob byte-for-byte before verifying every block against the current
generator. No historical value was inferred or silently replaced.

| Block | Historical presence | Status | Provenance | Limitation |
|---|---|---|---|---|
| A | Present | `REPRODUCIBLE` | `experiment_a()`; exhaustive 1,296 `4d6` outcomes; exact comparison with blob `1634c05…` | Experimental partition probe, not CURRENT rules |
| A2 | Present | `REPRODUCIBLE` | `experiment_a2()`; same 1,296 outcomes; exact comparison with blob `1634c05…` | REPORT conclusions still require the separate A2 roadmap review |
| B | Present | `REPRODUCIBLE` | `experiment_b()`; seeds `0..199`, three policies, 16 turns; exact comparison with blob `1634c05…` | Policy trajectories are not human behavior |
| B2 | Present | `REPRODUCIBLE` | `experiment_b2()`; seeds `0..99`, two policies × two variants, 16 turns; exact comparison with blob `1634c05…` | Uses its documented non-CURRENT post-bust convention |
| C | Present | `REPRODUCIBLE` | `experiment_c()`; fixed analytical fixtures; exact comparison with blob `1634c05…` | SPEC and Curve B remain experimental fixtures |

`results.json` preserves the verified intact historical artifact. The detailed
experimental conclusions remain in `REPORT.md`; A1 does not revalidate them.

## Reproduction commands

From the repository root, the normal module entry point regenerates **only
A2/B2**, validates the existing JSON and the presence of the preserved
first-pass blocks A/B/C before writing, and then updates `results.json`:

```bash
python -m experiments.current.training_v2_minimal.harness
```

If `results.json` is missing, malformed, or lacks A/B/C, this command fails
explicitly and does not overwrite the artifact. It does not rerun B's 9,600
historical turns.

Full regeneration is explicit and writes only the requested temporary file:

```bash
python -c 'import json; from experiments.current.training_v2_minimal.harness import run_all; print(json.dumps(run_all(), indent=2, ensure_ascii=False))' > /tmp/training_v2_minimal-results.json
```

Compare that temporary file with the committed artifact before replacing any
evidence. Run the targeted tests with:

```bash
python -m unittest experiments.current.training_v2_minimal.test_harness -v
```
