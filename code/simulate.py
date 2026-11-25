"""Monte Carlo sanity check of the adaptive estimator of Section 3 (illustration only).

Standard library only. For one fixed conditionally independent law (n=3 experts, m=4 signal
values) and one fixed dependent law (a calibrated 2x2 interaction added to it), the script
draws T training cases, runs the estimator of Section 3 (offset fit by least squares on a fine
grid of the compactified offset, cellwise histogram, choice by validation on the second half)
and computes the exact excess risk. It reports T times the mean excess risk over repetitions.

Under conditional independence the theory predicts T * risk = O(log(1/delta)), so this number
should stay bounded as T grows. The check passes if, for the independent law, the largest
T * mean-risk across T in {250, 1000, 4000} is within a factor 3 of the smallest.
This is a finite illustration, not part of any proof. Floating-point tolerance: the pass
criterion is a factor-3 band, far wider than any cross-platform rounding difference.

Usage: python3 -I -B -O code/simulate.py --output results/simulation.json
"""
import argparse
import json
import sys
from itertools import product
from math import exp, log
from random import Random

N_EXPERTS, M_SIGNALS = 3, 4
PRIOR = 0.3
BAND = 3.0  # allowed ratio between largest and smallest T*risk


def make_law(dependent, seed=7):
    rng = Random(seed)
    lik = []
    for _y in (0, 1):
        rows = []
        for _i in range(N_EXPERTS):
            w = [rng.random() + 0.2 for _ in range(M_SIGNALS)]
            s = sum(w)
            rows.append([x / s for x in w])
        lik.append(rows)
    cells = list(product(range(M_SIGNALS), repeat=N_EXPERTS))
    joint = {}
    for x in cells:
        for y in (0, 1):
            pr = PRIOR if y else 1 - PRIOR
            for i in range(N_EXPERTS):
                pr *= lik[y][i][x[i]]
            joint[(x, y)] = pr
    if dependent:
        eps = 0.3 * min(joint.values())
        for x in cells:
            if x[0] < 2 and x[1] < 2:
                s = (-1) ** (x[0] + x[1])
                joint[(x, 1)] += s * eps
                joint[(x, 0)] -= s * eps
    # calibrated reports r_i(j) = P(Y=1 | X_i=j)
    rep = {}
    for i in range(N_EXPERTS):
        for j in range(M_SIGNALS):
            num = sum(v for (x, y), v in joint.items() if x[i] == j and y == 1)
            den = sum(v for (x, y), v in joint.items() if x[i] == j)
            rep[(i, j)] = num / den
    px = {x: joint[(x, 0)] + joint[(x, 1)] for x in cells}
    h = {x: joint[(x, 1)] / px[x] for x in cells}
    score = {x: sum(log(rep[(i, x[i])] / (1 - rep[(i, x[i])])) for i in range(N_EXPERTS)) for x in cells}
    keys = list(joint)
    weights = [joint[k] for k in keys]
    return keys, weights, px, h, score


def logistic(t):
    return 1 / (1 + exp(-t)) if t >= 0 else exp(t) / (1 + exp(t))


def run(dependent, T, reps, rng):
    keys, weights, px, h, score = make_law(dependent)
    grid = [-12 + 24 * g / 2400 for g in range(2401)]
    out = []
    for _ in range(reps):
        sample = rng.choices(keys, weights=weights, k=T)
        s = T // 2
        train, valid = sample[:s], sample[s:]
        counts = {}
        for x, y in train:
            c = counts.setdefault(x, [0, 0])
            c[0] += 1
            c[1] += y
        agg = {}
        for x, y in train:
            a = agg.setdefault(score[x], [0, 0])
            a[0] += 1
            a[1] += y
        best_b, best_loss = None, None
        for b in grid:
            loss = 0.0
            for sc, (cnt, ones) in agg.items():
                f = logistic(b + sc)
                loss += cnt * f * f - 2 * ones * f
            if best_loss is None or loss < best_loss:
                best_b, best_loss = b, loss

        def f_ls(x, b=best_b):
            return logistic(b + score[x])

        def f_hist(x):
            c = counts.get(x)
            return c[1] / c[0] if c else 0.5

        def vloss(f):
            return sum((f(x) - y) ** 2 for x, y in valid)
        f = f_ls if vloss(f_ls) <= vloss(f_hist) else f_hist
        out.append(sum(px[x] * (f(x) - h[x]) ** 2 for x in px))
    return sum(out) / len(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="results/simulation.json")
    args = ap.parse_args()
    rng = Random(20261124)
    res = {}
    for dependent in (False, True):
        rows = []
        for T in (250, 1000, 4000):
            risk = run(dependent, T, 40, rng)
            rows.append(dict(T=T, mean_excess_risk=round(risk, 7), T_times_risk=round(T * risk, 3)))
            print(f"{'dependent' if dependent else 'independent'} T={T}: mean excess risk {risk:.6f}, T*risk {T * risk:.3f}")
        res["dependent" if dependent else "independent"] = rows
    tr = [r["T_times_risk"] for r in res["independent"]]
    ok = max(tr) <= BAND * min(tr)
    res["criterion"] = "independent law: largest T*risk within a factor of three of the smallest, T in {250,1000,4000}"
    res["status"] = "PASS" if ok else "FAIL"
    with open(args.output, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    print(res["status"])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
