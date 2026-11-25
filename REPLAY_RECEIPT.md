# Replay receipt (release 0.1.0-candidate, 25 November 2026)

The publisher replayed the approved candidate from a fresh copy before adding the DOI line. Only `manuscript.tex`
(the DOI line under the author), the rebuilt `manuscript.pdf` and the release records changed afterwards; every
script and result file is byte-identical to the replayed copy (checked by SHA-256 in the frozen-archive gate).

Interpreters were printed inside the run (see [ENVIRONMENT.txt](ENVIRONMENT.txt)): `uv run --python 3.12` resolved
to CPython 3.14.7 through the host's python3 shim, so `verify.py` was also run under CPython 3.12.11 (same result).

## Runs (fresh copy, cwd = package root, macOS arm64, PYTHONDONTWRITEBYTECODE=1)

| Command | Exit | Time | Output |
|---|---|---|---|
| `python3 -I -B -O code/verify.py --output results/verification.json` | 0 | <1 s | `9075 checks, 0 failures: PASS`; results/verification.json byte-identical to the recorded file (also `9075 checks, 0 failures: PASS` under 3.12.11) |
| `python3 -I -B -O code/simulate.py --output results/simulation.json` | 0 | 6 s | `PASS`; conditionally independent law T × risk 0.429, 0.417, 0.393 at T = 250, 1000, 4000; results/simulation.json byte-identical to the recorded file |

Every run wrote nothing to stderr.

## Negative control (fresh copy, `python3 -I -B -O`)

| Mutation | Result |
|---|---|
| `verify.py`, Section 4.1 one-case KL check: constant 18 replaced by 1 | `FAILED: confidence(n=2) one-case KL <= 18 d^2 ...` lines, exit 1 |

## Comparison policy (declared before tagging; also in README.md, ENVIRONMENT.txt and the CI workflow)

- `results/verification.json` (exact rational checks; deterministic): byte-identical on every platform.
- `results/simulation.json` (floating point; Python's Mersenne Twister and math.exp/log): same structure and
  non-numeric values; numbers within a relative 1e-6.
- Interpreter versions and timings are not compared (neither output file records them).

The comparison script is `.github/ci/compare_outputs.py`.
