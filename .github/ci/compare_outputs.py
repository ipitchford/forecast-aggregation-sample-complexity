"""Compare regenerated outputs with the outputs recorded at release (25 November 2026).
Policy (declared before tagging; also in README.md, ENVIRONMENT.txt and REPLAY_RECEIPT.md):
- verification.json (exact rational checks, deterministic): byte-identical.
- simulation.json (floating point; Python's Mersenne Twister and math.exp/log): same structure, non-numeric values
  exactly, numbers within a relative 1e-6.
Interpreter versions and timings are not compared (neither file records them).
usage: compare_outputs.py NEWDIR RECORDEDDIR"""
# SPDX-License-Identifier: MIT
import json, sys
from pathlib import Path
new, rec = Path(sys.argv[1]), Path(sys.argv[2])
bad = []
if (new / 'verification.json').read_bytes() != (rec / 'verification.json').read_bytes(): bad.append('verification.json differs')
else: print('verification.json: identical')
REL = 1e-6; worst = [0.0]
def cmp(a, b, path):
    if isinstance(a, dict) and isinstance(b, dict):
        if sorted(a) != sorted(b): bad.append(f'{path}: keys differ'); return
        for k in a: cmp(a[k], b[k], f'{path}.{k}')
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b): bad.append(f'{path}: length differs'); return
        for i, (x, y) in enumerate(zip(a, b)): cmp(x, y, f'{path}[{i}]')
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        d = abs(a - b)
        if b != 0: worst[0] = max(worst[0], d / abs(b))
        if d > REL * abs(b): bad.append(f'{path}: {a} vs {b}')
    elif a != b: bad.append(f'{path}: {a!r} vs {b!r}')
cmp(json.loads((new / 'simulation.json').read_text()), json.loads((rec / 'simulation.json').read_text()), 'simulation')
print(f'simulation.json: largest relative difference {worst[0]:.2e}')
if bad: print('FAIL', bad); sys.exit(1)
print('PASS outputs agree with the recorded outputs under the declared policy')
