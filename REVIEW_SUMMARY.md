# Review summary (internal, AI-assisted)

This file records the internal checking of this candidate before release, without any ratings. It is not peer review,
independent reproduction or formal verification. All review steps were carried out by AI systems (Claude) under the
Evidence Press publication protocol; no external referee has seen the paper.

## What was done (24–25 November 2026)

1. **Combined five-role review** (editor, methodology, domain, perspective and devil's-advocate roles in one Claude
   review). The methodology role checked every proof and recomputed every load-bearing constant; all were
   conservative. No role found an error in a stated result. The objections concerned positioning, attribution and
   readability, not correctness.
2. **Exact checks and a simulation** by the lead: the source bundle's checks relied on `assert` (which `python -O`
   disables), so they were replaced by `code/verify.py` with explicit checks (9075, exact rational arithmetic); a
   negative control (one constant changed) makes it exit 1 under `-O`. A small simulation of the estimator
   (`code/simulate.py`) was added as an illustration.
3. **One revision round**: a context-first introduction with a table of known and new rates, a roadmap and section
   openers; the pooling formula credited to Bordley as Lin and Chen credit it (their Lemma 5.1); Lin and Chen's partial
   1/ε results (their Theorems 5.4, 5.5 and 7.1) listed; the localisation literature acknowledged and the
   conditional-independence contribution reworded as removal of a log T factor plus matching lower bounds; a comparison
   of the many-outcome bound with Lin and Chen's Theorem 6.1, including where theirs is smaller; the proof of the
   ordered least-squares lemma (Lemma 5) rewritten in full; an explicit lower constant 2^−17 in Theorem 1; the scope
   (binary, δ ≤ 1/32, exact reports) stated in the abstract; η named as the conditional total correlation; a
   discussion of practical meaning and open problems.
4. **Verification re-review** (every revision item traced in the source and PDF) and **proof audit of the new and
   rewritten mathematics** (Lemma 5, the explicit constants, Proposition 7, the validation step, the report-spacing
   claim, the simulation sentence). No critical or major finding; one arithmetic slip in a validation constant
   (2Ct/v corrected to 4Ct/v) and several wording items were applied by the lead.

No Astra/Codex review took place for this candidate.

## Main objections and how they were resolved

| Objection | Resolution |
|---|---|
| The conditional-independence endpoint largely follows from standard localisation (up to log T), so "closing the gap" overstates it | Abstract and Section 1 now say so plainly: the new content there is removing the log T factor (Lemma 5, using the pointwise order of the candidate rules) and the matching high-confidence lower bounds; the main novelty is placed in the dependence results |
| The pooling formula was attributed to the paper being improved | Credited to Bordley as Lin and Chen credit it (their Lemma 5.1) |
| Lin and Chen's partial 1/ε results were omitted | Theorems 5.4, 5.5 and 7.1 listed, with the statement that the new results need none of their informativeness or minimum-probability conditions |
| The many-outcome bound was not compared with the published one | Comparison paragraph in Section 6: the new bound is smaller whenever ε ≤ 1/k; for many outcomes and coarse accuracy Lin and Chen's can be smaller |
| A key lemma's proof was too compressed; constants unstated | Lemma 5 rewritten step by step with Bousquet's inequality quoted; explicit lower constant 2^−17 checked in verify.py |
| Readability: no introduction, motivation or roadmap | New Section 1, Table 1, roadmap and an opening sentence for every section |
| Checks would pass vacuously under `python -O` | Replaced by explicit checks with a negative control |

## What remains open or unchecked

- With k outcomes a factor of about k remains between the upper and lower bounds (Section 7, open problem 1); a
  bounded attempt to close it did not succeed.
- Rounded or noisy reports, extremised pooling and the partial-evidence model are not treated (Section 7).
- The constants are not optimised.
- The novelty check rests on searches of limited scope ([RESEARCH_GATES.json](RESEARCH_GATES.json)).
- No human specialist has checked the proofs.
