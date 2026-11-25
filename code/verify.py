"""Finite exact checks for "How many resolved forecasts does an aggregator need?".

Standard library only (Python 3.10+). Every check is explicit (no `assert`), so the
script also fails correctly under `python -O`. Rational arithmetic (fractions) is used
for every identity the paper relies on; the few floating-point quantities (logarithms in
KL divergences) are compared against rational bounds with an explicit margin.

Usage:  python3 -I -B -O code/verify.py --output results/verification.json
Exit status 0 if every check passes, 1 otherwise.

These checks verify the finite algebra of the constructions in Sections 4-6 at the
listed parameters. They do not replace the proofs, which cover all parameters.
"""
import argparse
import json
import sys
from fractions import Fraction as F
from itertools import product
from math import e, exp, log, prod, sqrt
from random import Random

FAILURES = []
COUNT = [0]


def check(condition, label):
    COUNT[0] += 1
    if not condition:
        FAILURES.append(label)


def bernoulli_kl(p, q):
    """KL(Bern(p) || Bern(q)) in nats, as a float."""
    return sum(float(x) * log(float(x) / float(y))
               for x, y in ((p, q), (1 - p, 1 - q)) if x)


def power_two_at_least(n):
    return 1 << (n - 1).bit_length()


# ---------------------------------------------------------------- Section 4.2 / 4.3
def grid_family(n, m, a):
    """Calibrated interaction family of Section 4.2 on the fixed dyadic grid."""
    K = m ** n
    L, M = power_two_at_least(8 * n), power_two_at_least(m)
    w = [F(2 * j - m + 1, L * M) for j in range(m)]   # w_j for j = 1..m (0-based here)
    r = [(1 + x) / 2 for x in w]                        # expert report for symbol j
    cells = list(product(range(m), repeat=n))
    plus = {x: prod(1 + w[j] for j in x) for x in cells}
    minus = {x: prod(1 - w[j] for j in x) for x in cells}
    B = {x: (plus[x] + minus[x]) / 2 for x in cells}
    mass = {x: B[x] / K for x in cells}
    h0 = {x: plus[x] / (2 * B[x]) for x in cells}
    even = m - m % 2
    blocks = sorted({(x[0] // 2, x[1] // 2) + x[2:] for x in cells
                     if x[0] < even and x[1] < even})

    def law(signs):
        out = {}
        for x in cells:
            if x[0] < even and x[1] < even:
                key = (x[0] // 2, x[1] // 2) + x[2:]
                s = (-1) ** (x[0] + x[1])          # 2x2 pattern (+1,-1;-1,+1)
                out[x] = h0[x] + a * signs[key] * s / B[x]
            else:
                out[x] = h0[x]
        return out
    return dict(K=K, L=L, M=M, w=w, r=r, cells=cells, B=B, mass=mass, h0=h0,
                blocks=blocks, law=law)


def check_grid(n, m, a=F(1, 16)):
    g = grid_family(n, m, a)
    K, cells, mass, B, h0, r = g["K"], g["cells"], g["mass"], g["B"], g["h0"], g["r"]
    blocks = g["blocks"]
    tag = f"grid(n={n},m={m})"
    spacing = F(1, g["L"] * g["M"])
    check(all(y - x == spacing for x, y in zip(r, r[1:])), tag + " report spacing 1/(LM)")
    check(all((2 * g["L"] * g["M"] * v).denominator == 1 for v in r), tag + " reports on dyadic grid")
    check(all(F(7, 8) <= B[x] <= F(8, 7) for x in cells), tag + " B in [7/8,8/7]")
    check(all(F(49, 113) <= h0[x] <= F(64, 113) for x in cells), tag + " h0 in [49/113,64/113]")
    check(len(blocks) == (m // 2) ** 2 * m ** (n - 2), tag + " number of blocks")
    check(9 * len(blocks) >= K, tag + " b >= K/9")
    check(sum(mass.values()) == 1, tag + " design is a probability law")
    signs = {key: (-1) ** i for i, key in enumerate(blocks)}
    h = g["law"](signs)
    flipped = dict(signs)
    flipped[blocks[0]] *= -1
    nb = g["law"](flipped)
    allp = g["law"](dict.fromkeys(blocks, 1))
    allm = g["law"](dict.fromkeys(blocks, -1))
    # probabilities stay in [1/4,3/4] even at the largest allowed amplitude a = 1/8
    hmax = g["law"](dict.fromkeys(blocks, 1)) if a == F(1, 8) else grid_family(n, m, F(1, 8))["law"](dict.fromkeys(blocks, 1))
    check(all(F(1, 4) <= v <= F(3, 4) for v in hmax.values()), tag + " h in [1/4,3/4] at a=1/8")
    for name, lw in (("h0", h0), ("h", h), ("neighbour", nb), ("all+", allp), ("all-", allm)):
        check(sum(mass[x] * lw[x] for x in cells) == F(1, 2), tag + f" prior 1/2 under {name}")
        for i in range(n):
            for j in range(m):
                sub = [x for x in cells if x[i] == j]
                joint = sum(mass[x] * lw[x] for x in sub)
                marg = sum(mass[x] for x in sub)
                check(marg == F(1, m), tag + f" symbol law uniform ({name},i={i},j={j})")
                check(joint / marg == r[j], tag + f" expert calibrated ({name},i={i},j={j})")
    # conditional-product structure of the baseline Q: Q(x,y) = prod_i Q(x_i,y)/Q(y)^{n-1}
    for y in (0, 1):
        q = {x: mass[x] * (h0[x] if y else 1 - h0[x]) for x in cells}
        mg = [{j: sum(v for x, v in q.items() if x[i] == j) for j in range(m)} for i in range(n)]
        check(all(q[x] == prod(mg[i][x[i]] for i in range(n)) / F(1, 2) ** (n - 1) for x in cells),
              tag + f" baseline is conditionally independent (y={y})")
    sep = sum(mass[x] * (h[x] - nb[x]) ** 2 for x in cells)
    check(sep >= 14 * a * a / K, tag + " one-bit separation >= 14a^2/K")
    chi_nb = sum(mass[x] * (h[x] - nb[x]) ** 2 / (nb[x] * (1 - nb[x])) for x in cells)
    check(chi_nb <= 128 * a * a / K, tag + " one-bit chi-square <= 128a^2/K")
    chi_base = sum(mass[x] * (h[x] - h0[x]) ** 2 / (h0[x] * (1 - h0[x])) for x in cells)
    check(chi_base <= 16 * a * a, tag + " chi-square to baseline <= 16a^2")
    gsep = sum(mass[x] * (allp[x] - allm[x]) ** 2 for x in cells)
    check(gsep >= 14 * len(blocks) * a * a / K, tag + " global separation >= 14ba^2/K")
    gchi = sum(mass[x] * (allp[x] - allm[x]) ** 2 / (allm[x] * (1 - allm[x])) for x in cells)
    check(gchi <= 32 * a * a, tag + " global chi-square <= 32a^2")
    # total correlation equals KL to the baseline (Pythagorean identity), float with margin
    direct_kl = sum(float(mass[x]) * bernoulli_kl(h[x], h0[x]) for x in cells)
    tc = 0.0
    for y in (0, 1):
        py = {x: mass[x] * (h[x] if y else 1 - h[x]) for x in cells}
        prior = F(1, 2)
        mg = [{j: sum(v for x, v in py.items() if x[i] == j) for j in range(m)} for i in range(n)]
        for x, v in py.items():
            prodq = prod(mg[i][x[i]] / prior for i in range(n)) * prior
            tc += float(v) * log(float(v / prodq))
    check(abs(tc - direct_kl) < 1e-12, tag + " I(P) equals KL(P||Q)")
    check(tc <= float(chi_base) + 1e-12, tag + " I(P) <= chi-square bound")
    out = dict(n=n, m=m, K=K, hidden_signs=len(blocks), report_spacing=str(spacing),
               I_P=round(tc, 8), chi_square_bound=round(float(chi_base), 8))
    if (n, m) == (2, 2):
        ok = (r == [F(31, 64), F(33, 64)] and mass[(0, 0)] == F(1025, 4096)
              and mass[(0, 1)] == F(1023, 4096) and h0[(0, 0)] == F(961, 2050)
              and {h[(0, 0)], nb[(0, 0)]} == {F(1089, 2050), F(833, 2050)})
        check(ok, tag + " worked example 31/64, 33/64, 1025/4096, (961 +- 128)/2050")
        out["worked_example"] = dict(reports=["31/64", "33/64"], diagonal_profile="1025/4096",
                                     off_diagonal_profile="1023/4096", low_low_baseline="961/2050",
                                     low_low_alternatives=["833/2050", "1089/2050"])
    return out


# ---------------------------------------------------------------- Section 4.1
def confidence_family(n, z):
    p = (1 - z / n) / 2
    u = p / (1 - p)
    return p, u, p / (p + (1 - p) * u ** n)


def check_confidence(n):
    tag = f"confidence(n={n})"
    zs = [F(1, 4) + F(j, 32) for j in range(9)]           # grid of [1/4,1/2]
    for z in zs:
        p, u, hz = confidence_family(n, z)
        check(p / (p + (1 - p) * u) == F(1, 2), tag + f" regular report is calibrated (z={z})")
        check(p + (1 - p) * u ** n >= F(3, 8), tag + f" all-regular profile mass >= 3/8 (z={z})")
        arg = (n - 1) * log(float((n + z) / (n - z)))
        check(0 <= arg <= 1, tag + f" logistic argument in [0,1] (z={z})")
    worst = 0.0
    for z0 in zs:
        for z1 in zs:
            if z1 <= z0:
                continue
            d = z1 - z0
            p0, u0, h0 = confidence_family(n, z0)
            p1, u1, h1 = confidence_family(n, z1)
            check(h1 - h0 >= d / 6, tag + f" separation >= d/6 ({z0},{z1})")
            kl = bernoulli_kl(p0, p1) + float(1 - p0) * n * bernoulli_kl(u0, u1)
            check(kl <= 18 * float(d * d), tag + f" one-case KL <= 18 d^2 ({z0},{z1})")
            worst = max(worst, kl / float(d * d))
    p0, u0, h0 = confidence_family(n, F(1, 4))
    p1, u1, h1 = confidence_family(n, F(1, 2))
    return dict(n=n, gap_quarter_to_half=round(float(h1 - h0), 8),
                max_KL_over_d2_on_grid=round(worst, 6))


# ---------------------------------------------------------------- Section 5
def check_continuous(n, m, a=F(1, 8)):
    """Cell-level exact check of the atomless construction (m even)."""
    tag = f"continuous(n={n},m={m})"
    cells = list(product(range(m), repeat=n))
    K = m ** n
    centre = [F(2 * j + 1, 2 * m) for j in range(m)]
    blocks = sorted({(x[0] // 2, x[1] // 2) + x[2:] for x in cells})
    signs = {key: (-1) ** i for i, key in enumerate(blocks)}
    pert = {x: a * signs[(x[0] // 2, x[1] // 2) + x[2:]] * (-1) ** (x[0] + x[1]) for x in cells}
    # the perturbation averages to zero over the cells sharing one coordinate value
    for i in range(n):
        for j in range(m):
            check(sum(pert[x] for x in cells if x[i] == j) == 0, tag + f" zero conditional mean (i={i},j={j})")
    # range: |h0 - 1/2| <= a and |pert| = a, so h in [1/2-2a, 1/2+2a] = [1/4,3/4] at a=1/8
    check(F(1, 2) - 2 * a >= F(1, 4), tag + " h in [1/4,3/4]")
    # exact E(h-1/2)^2 over the uniform cube: linear part plus cellwise constant
    var1 = F(1, 3)                     # Var-free second moment of (2X-1) for X ~ U[0,1]
    lin2 = (a / n) ** 2 * n * var1     # E[((a/n) sum (2X_i-1))^2]
    cross = sum(F(1, K) * pert[x] * (a / n) * sum(2 * centre[x[i]] - 1 for i in range(n)) for x in cells)
    p2 = sum(F(1, K) * pert[x] ** 2 for x in cells)
    second = lin2 + 2 * cross + p2
    check(4 * second <= 16 * a * a, tag + " 4E(h-1/2)^2 <= 16a^2")
    return dict(n=n, m=m, four_second_moment_over_a2=str(4 * second / (a * a)))


# ---------------------------------------------------------------- Section 6
def check_multiclass(seed=19631122):
    rng = Random(seed)
    out = {}
    for k in (2, 3, 4, 7, 12):
        tag = f"multiclass(k={k})"
        edges = [(i, j) for i in range(k) for j in range(i + 1, k)]
        for colour in range(k):
            verts = [v for i, j in edges if (i + j) % k == colour for v in (i, j)]
            check(len(verts) == len(set(verts)), tag + f" colour {colour} is a matching")
        for _ in range(100):
            def simplex():
                w = [rng.randrange(3) for _ in range(k)]
                if sum(w) == 0:
                    w[0] = 1
                return [F(x, sum(w)) for x in w]
            p, z = simplex(), simplex()
            q = [F(rng.randrange(8), 7) for _ in edges]
            d = [x - y for x, y in zip(z, p)]
            res = [d[i] - (d[i] + d[j]) * qe for (i, j), qe in zip(edges, q)]
            check(sum(x * x for x in d) <= 2 * k * sum(x * x for x in res), tag + " ||d||^2 <= 2k sum L^2")
            u, v = [sqrt(x) for x in p], [sqrt(x) for x in z]

            def obj(vec):
                return sum((vec[i] * sqrt(1 - qe) - vec[j] * sqrt(qe)) ** 2 for (i, j), qe in zip(edges, q))
            wedge = sum((u[i] * v[j] - u[j] * v[i]) ** 2 for i, j in edges)
            overlap = sum(x * y for x, y in zip(u, v))
            check(abs(wedge - (1 - overlap ** 2)) < 1e-12, tag + " Lagrange identity")
            check(wedge <= 2 * (obj(u) + obj(v)) + 1e-12, tag + " wedge <= 2[F(u)+F(v)]")
            check(sum(x * x for x in d) <= 2 * (1 - overlap ** 2) + 1e-12, tag + " squared error <= 2(1-<u,v>^2)")
        out[str(k)] = "100 random instances"
    return out


# ---------------------------------------------------------------- Section 3 algebra
def check_upper_algebra(seed=20261124):
    rng = Random(seed)
    for _ in range(2000):
        d = F(rng.randrange(1, 50), 50)
        e_ = F(rng.randrange(0, 50), 50)
        a1, b1 = F(rng.randrange(0, 101), 100), F(rng.randrange(0, 101), 100)
        alpha = sqrt(a1 * b1) + sqrt((1 - a1) * (1 - b1))
        lhs = float(d + e_) - 2 * sqrt(float(d * e_)) * alpha
        check(lhs + 1e-12 >= float(d) * (1 - alpha ** 2), "histogram cell inequality")
        check(float((a1 - b1) ** 2) <= 1 - alpha ** 2 + 1e-12, "squared TV <= 1 - affinity^2")
    for _ in range(500):
        n = rng.randrange(2, 9)
        base = [F(rng.randrange(0, 20), 20) for _ in range(n)]
        incs = [[F(rng.randrange(0, 5), 20) for _ in range(n)] for _ in range(rng.randrange(1, 8))]
        chain = [base]
        for inc in incs:
            chain.append([x + y for x, y in zip(chain[-1], inc)])
        tot = sum((x - y) ** 2 for x, y in zip(chain[-1], chain[0]))
        steps = sum(sum((x - y) ** 2 for x, y in zip(c2, c1)) for c1, c2 in zip(chain, chain[1:]))
        check(steps <= tot, "ordered chain: squared increments add subadditively")
    check(e / (1 + e) ** 2 > 1 / 6, "logistic'(1) > 1/6")


def check_explicit_lower_constant():
    """Algebra of the explicit constant c = 2^-17 in Theorem 1 on a parameter grid."""
    c = 2.0 ** -17
    worst = float("inf")
    for T in [1, 2, 3, 10, 100, 10 ** 3, 10 ** 5, 10 ** 8]:
        for delta in [1 / 32, 1e-2, 1e-4, 1e-10, 1e-40]:
            for K in [4, 9, 64, 10 ** 3, 10 ** 6]:
                for eta in [0.0, 1e-8, 1e-4, 1e-2, 0.1, 1.0, float("inf")]:
                    d2 = min(1 / 16, log(1 / (8 * delta)) / (18 * T))
                    A = d2 / 384
                    Bv = 0.0
                    if eta > 0:
                        a2 = min(1 / 64, eta / 16, K / (2048 * T))
                        Bv = a2 / 24
                    b = min(1.0, log(1 / delta) / T + min(eta, K / T))
                    ratio = max(A, Bv) / b
                    worst = min(worst, ratio)
                    check(max(A, Bv) >= c * b, f"explicit c at T={T},delta={delta},K={K},eta={eta}")
    return dict(c="2^-17", min_ratio_lower_over_bT=worst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="results/verification.json")
    args = ap.parse_args()
    results = {"grids": [], "confidence": [], "continuous": []}
    for n, m in [(2, 2), (2, 3), (3, 4), (5, 3), (2, 7)]:
        g = check_grid(n, m)
        results["grids"].append(g)
        print(f"grid n={n}, m={m}: {g['K']} profiles, {g['hidden_signs']} hidden signs, "
              f"spacing {g['report_spacing']}, I={g['I_P']:.8f}, chi-square bound {g['chi_square_bound']:.8f}")
    for n in (2, 3, 10, 100, 1000):
        c = check_confidence(n)
        results["confidence"].append(c)
        print(f"confidence n={n}: gap={c['gap_quarter_to_half']:.8f}, max KL/d^2 on grid={c['max_KL_over_d2_on_grid']}")
    for n, m in [(2, 2), (2, 4), (3, 4)]:
        c = check_continuous(n, m)
        results["continuous"].append(c)
        print(f"continuous n={n}, m={m}: 4E(h-1/2)^2/a^2 = {c['four_second_moment_over_a2']}")
    results["multiclass"] = check_multiclass()
    print("multiclass k=2,3,4,7,12: coupling and matching checks done")
    check_upper_algebra()
    print("upper-bound algebra (histogram cell inequality, ordered chain) done")
    results["explicit_lower_constant"] = check_explicit_lower_constant()
    print(f"explicit lower constant c=2^-17: min ratio {results['explicit_lower_constant']['min_ratio_lower_over_bT']:.3e}")
    results["checks_run"] = COUNT[0]
    results["failures"] = FAILURES
    results["status"] = "PASS" if not FAILURES else "FAIL"
    with open(args.output, "w") as fh:
        json.dump(results, fh, indent=1, sort_keys=True)
    print(f"{COUNT[0]} checks, {len(FAILURES)} failures: {results['status']}")
    for f in FAILURES[:20]:
        print("FAILED:", f)
    sys.exit(0 if not FAILURES else 1)


if __name__ == "__main__":
    main()
