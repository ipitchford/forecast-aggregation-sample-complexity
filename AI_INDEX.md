# AI index: Learning to aggregate Bayesian forecasts (v0.1.0-candidate)

Machine-oriented map of claims, evidence and limits. Human readers should start with [README.md](README.md) ("What
this is about") and the paper [manuscript.pdf](manuscript.pdf) (source [manuscript.tex](manuscript.tex); Section 1
states the problem, why it matters, what was known, what is new and a roadmap). DOI 10.5281/zenodo.24532624 (concept
10.5281/zenodo.24532623). Status: unrefereed candidate; internal AI-assisted review only.

## Normalisation

Binary outcome Y in {0,1}; n >= 2 experts; expert i observes a signal S_i with at most m >= 2 values and reports the
exact posterior R_i = P(Y=1 | S_i) (calibrated). K = m^n. T independent training cases (R, Y). Bayesian aggregator
h(r) = P(Y=1 | R=r). Excess (Brier) risk R_P(f) = E(f(R) - h(R))^2. Dependence: conditional total correlation
I(P) = sum_y P(Y=y) KL(P_{R|y} || product of marginals); P_eta = {I(P) <= eta}. Minimax radius r_T(eta, delta): the
least u such that some learning rule has sup over P_eta of P(R_P(f_hat) > u) <= delta. Reference keys as in
[refs.bib](refs.bib): lc (Lin-Chen NeurIPS 2023, arXiv:2207.13126), poster, bordley, bbm, kol, baraud, agrawal,
bousquet, wulw, bg, glm, cpt.

## Claims and where they are proved

| ID | Claim | Location | Status / credit |
|---|---|---|---|
| 1 | For n, m >= 2, T >= 1, 0 < delta <= 1/32, 0 <= eta <= infinity, with b_T = min{1, log(1/delta)/T + min(eta, K/T)}: 2^-17 b_T <= r_T(eta, delta) <= C b_T for a universal C; one learning rule attains the upper bound for every eta, m, delta | Theorem 1; Sections 3-4 | written proof |
| 2 | Sample complexity of order log(1/delta)/eps under conditional independence and (m^n + log(1/delta))/eps under arbitrary dependence (eps below a universal constant) | Corollary 2; Table 1 | written proof; answers the 1/eps conjecture of lc (Section 7) for the binary model; raises the m^(n-2) lower bound of lc to m^n |
| 3 | Cost of assuming conditional independence: the best pooling-family rule has excess risk at most I(P)/2 | Lemma 4 | written proof; pooling formula lc Lemma 5.1, credited to Bordley |
| 4 | Log-free least squares over a pointwise-ordered family | Lemma 5 | written proof; localisation (bbm, kol) gives the bound with a log T factor (credited) |
| 5 | Histogram bound O((K + log(1/delta))/T) | Lemma 6 | written proof; uses agrawal Theorem I.3 |
| 6 | Validation between the pooling and histogram candidates attains the minimum of their bounds | Section 3.4 | written proof |
| 7 | Lower bounds: confidence term (Section 4.1); calibrated hard family with identical prior, expert calibration curves and report-vector law, reports on a dyadic grid of spacing 1/(LM) (Section 4.2); worked example m = n = 2 with reports 31/64 and 33/64 | Section 4 | written proof; finite algebra checked exactly in code/verify.py |
| 8 | Known prior: no cases needed if eta <= 2 eps; Theta((m^n + log(1/delta))/eps) if eta >= C eps | Proposition 7 | written proof |
| 9 | Unbounded alphabets: rate min{1, eta + log(1/delta)/T}; any fixed eta > 0 rules out uniform consistency, even with independent continuously distributed reports | Proposition 8 | written proof |
| 10 | k outcomes: O((k^2 + k log(1/delta))/eps) under conditional independence (Theorem 9) against a lower bound with a factor of order k less (Proposition 10); dependence interpolation for fixed k (Proposition 11); comparison with lc Theorem 6.1 | Section 6 | written proof; pairwise coupling of wulw (credited) |
| Open | k versus k^2 for many outcomes; rounded or noisy reports; extremised (two-parameter) pooling; partial-evidence model of bg | Section 7 | open |

## Evidence

| Check | Script | Scope |
|---|---|---|
| Report grids for (n,m) in {(2,2),(2,3),(3,4),(5,3),(2,7)}: calibration, unchanged prior and report law, baseline conditional independence, separation and divergence constants, I(P_theta) = KL(P_theta || Q), worked example; Section 4.1 constants for n in {2,3,10,100,1000}; continuous construction cell identities; coupling inequalities on random instances; explicit lower constant | [code/verify.py](code/verify.py) -> [results/verification.json](results/verification.json) | exact rational arithmetic (fractions) plus float KL comparisons with large slack; 9075 checks |
| Estimator illustration: n = 3, m = 4, offset grid of 2401 values in [-12, 12], 40 repetitions, T in {250, 1000, 4000}; T times mean excess risk 0.429, 0.417, 0.393 on the conditionally independent law | [code/simulate.py](code/simulate.py) -> [results/simulation.json](results/simulation.json) | floating point; illustration only |

Every check exits non-zero on failure without `assert`, also under `python -O`. Negative control (release replay and
CI): replacing the constant 18 by 1 in the Section 4.1 one-case KL check makes verify.py exit 1 under -O. Release
replay and environment: [REPLAY_RECEIPT.md](REPLAY_RECEIPT.md), [ENVIRONMENT.txt](ENVIRONMENT.txt).

Numbers quoted on the release page and in the audio: delta <= 1/32; rates log(1/delta)/eps and
(m^n + log(1/delta))/eps; m^(n-2) raised to m^n; the m = n = 2 example (reports 31/64 and 33/64); simulation T times
risk about 0.4 at T = 250 to 4000 (illustration only). All come from the paper and results/.

## Limits

Exact, honest, calibrated reports; rounding not covered. Worst case over all laws. Constants not optimised. A factor
of about k open for many outcomes. Literature search of limited scope ([RESEARCH_GATES.json](RESEARCH_GATES.json)).
Internal AI-assisted review only; see [REVIEW_SUMMARY.md](REVIEW_SUMMARY.md).
