# Learning to aggregate Bayesian forecasts: optimal sample complexity under bounded dependence

**How many resolved cases does forecast aggregation need?** Version 0.1.0-candidate. DOI
[10.5281/zenodo.24532624](https://doi.org/10.5281/zenodo.24532624) (all versions:
[10.5281/zenodo.24532623](https://doi.org/10.5281/zenodo.24532623)). Release page:
https://evidencepress.org/releases/forecast-aggregation-sample-complexity/

Unrefereed research candidate. Author: Anonymous. Text CC0-1.0; code MIT (see [LICENSE.md](LICENSE.md)).

## What this is about

Several forecasters each give a probability for the same yes/no event: rain tomorrow, a patient relapsing, an
election. Each has seen different evidence and reports honestly. The best possible combination is "the probability of
the event given all the reports together" (the *Bayesian aggregator*). But that depends on how the forecasters'
evidence overlaps, and nobody knows that in advance. An aggregator has to learn it from a track record of past cases
whose outcomes are known. How long must that track record be?

This matters because resolved cases are scarce and slow to collect. If the record needed grows exponentially with the
number of forecasters, one has to assume structure, for example that the forecasters' evidence is independent once the
outcome is known, and one should know what that assumption buys and what breaking it costs.

## What was known

Lin and Chen (NeurIPS 2023) set up the model: n experts, each with at most m possible signals, exact calibrated
probability reports, and T independent past cases. For experts whose evidence is conditionally independent given the
outcome, they showed that between about log(1/δ)/ε and 1/ε² cases are needed for accuracy ε with confidence 1 − δ. For
arbitrary dependence, between about m^(n−2)/ε and m^n/ε². They conjectured that 1/ε is the right dependence on the
accuracy, and their poster asked about the case between the two. Under conditional independence the ideal combination
is the classical multiplicative pooling formula (their Lemma 5.1, which they credit to Bordley).

## What is new

1. **The exact rate for every level of dependence** (Theorem 1). Measure dependence by the *conditional total
   correlation* η of the reports: how much the forecasters share beyond what each knows about the outcome. With
   failure probability δ ≤ 1/32, the minimax excess Brier risk after T cases is of order
   min{1, log(1/δ)/T + min(η, m^n/T)}, up to universal constants.
2. **Both endpoints** (Corollary 2). About log(1/δ)/ε cases are needed and suffice for conditionally independent
   experts, and about (m^n + log(1/δ))/ε under arbitrary dependence. This confirms Lin and Chen's 1/ε conjecture for
   the binary model and raises their m^(n−2) lower bound to m^n.
3. **One method that does not need to know η.** Fit the pooling formula, fit a lookup table, and keep whichever does
   better on held-out cases. With a short record the pooling formula wins and its bias is of size η; once the record
   is longer than about m^n/η cases, the joint structure can be learned.
4. **Hard cases invisible to every individual record** (Section 4.2). The worst cases keep every forecaster's own track record, the
   base rate and even the full pattern of reports identical, yet the right combination differs: the difficulty lies in
   interactions that no single forecaster's record can reveal.
5. **Further results.** What knowing the base rate is worth (Proposition 7); with continuous reports, any fixed
   dependence allowance rules out uniform consistency (Proposition 8); many outcomes (Section 6).

**Relation to standard tools.** For conditionally independent experts, standard localisation arguments from learning
theory already gave the upper bound up to a factor log T. The new parts there are removing that factor (Lemma 5, which
uses the fact that the candidate rules are pointwise ordered) and the matching lower bounds. The main new content is
the dependence trade-off and the worst-case construction.

## Limits

- Reports are exact, honest, calibrated probabilities. Rounding to whole percentages is not covered.
- The bounds are worst case over all laws; a particular group of forecasters may be much easier.
- The constants are universal but not optimised (the explicit lower constant is 2^−17).
- With k outcomes, a factor of about k between the upper and lower bounds remains open.
- Credit: the model, the conjecture, the confidence lower bound and partial 1/ε results in special cases are Lin and
  Chen's; the pooling formula is classical (Bordley, as credited by Lin and Chen).

## Contents

| Path | What it is |
|---|---|
| [manuscript.pdf](manuscript.pdf), [manuscript.tex](manuscript.tex) | The paper (16 pages; self-contained LaTeX source) |
| [code/verify.py](code/verify.py) | Exact-arithmetic checks of the finite algebra of the constructions (9075 checks; standard library) |
| [code/simulate.py](code/simulate.py) | Small simulation of the estimator on two laws (illustration only) |
| [results/verification.json](results/verification.json), [results/simulation.json](results/simulation.json) | Recorded outputs |
| [requirements.txt](requirements.txt) | Standard library only (Python 3.10 or later) |
| [refs.bib](refs.bib) | Bibliography of the paper |
| [AI_INDEX.md](AI_INDEX.md), [RESEARCH_GATES.json](RESEARCH_GATES.json), [REVIEW_SUMMARY.md](REVIEW_SUMMARY.md), [REPLAY_RECEIPT.md](REPLAY_RECEIPT.md), [ENVIRONMENT.txt](ENVIRONMENT.txt) | Machine-readable index, research-gate record, review summary, replay receipt, environment |
| [MANIFEST.sha256](MANIFEST.sha256) | SHA-256 of every file |

## Reproducing the checks

From the package root, with any Python 3.10 or later (standard library only):

```sh
python3 -I -B -O code/verify.py --output results/verification.json    # prints "9075 checks, 0 failures: PASS"
python3 -I -B -O code/simulate.py --output results/simulation.json    # a few seconds; prints PASS
```

Both scripts check explicitly (no `assert`) and exit 1 on failure, also under `python -O`. Comparison policy (declared
before tagging; the same in CI, ENVIRONMENT.txt and REPLAY_RECEIPT.md): `results/verification.json` must be
byte-identical; `results/simulation.json` must agree in structure and non-numeric values exactly and in numbers within
a relative 1e-6; interpreter versions are not compared. GitHub CI (`.github/workflows/replay.yml`) checks the
manifest, runs both scripts on Linux, compares the outputs under this policy and runs a negative control.

The proofs are complete without the scripts, which check finite algebra only. The simulation is an illustration, not
evidence for the theorems.

## Assurance

Internal AI-assisted review only: a combined five-role Claude review, the lead's exact checks with a negative control
and a small simulation, one revision round, then a re-review and a proof audit of the new and rewritten proofs. No
Astra/Codex review took place. This is not peer review, independent reproduction or formal verification. See
[REVIEW_SUMMARY.md](REVIEW_SUMMARY.md).

## Citation

Anonymous (2026). *Learning to aggregate Bayesian forecasts: optimal sample complexity under bounded dependence*
(version 0.1.0-candidate). Evidence Press. https://doi.org/10.5281/zenodo.24532624
