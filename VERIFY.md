# VERIFY

Repository: https://github.com/necat101/python-stdlib-batched-mini-batch-footgun-lab

Implementation commit (verified): `bb80b0d6df8e3f354cd4b67b515ed98e898dfc92`

Documentation commit (contains this VERIFY.md): later, not fresh-clone verified.

## Clean clone

```sh
git clone https://github.com/necat101/python-stdlib-batched-mini-batch-footgun-lab.git batched_verify
cd batched_verify
git checkout bb80b0d6df8e3f354cd4b67b515ed98e898dfc92
```

Interpreter discovery (`$PYTHON_BIN`, `python3.14`, `python3.13`, `python3.12`, `python3`, `python`):

- Selected: `python3.14` → `/python-lab/.local/bin/python3.14`

Environment:

- Python: 3.14.6
- Implementation: CPython
- Platform: Linux-6.17.0-1009-aws-x86_64-with-glibc2.39
- `itertools.batched` available: yes
- strict option available: yes
- strict behavior confirmed: yes
- `math.sumprod` available: yes

## Validation commands

```
python3.14 -m py_compile run_lab.py test_lab.py
# exit code 0

python3.14 run_lab.py
# Done. 100 rows. pass=14, expected_error=3, local_observation=9, context_only=1, not_applicable=73
# exit code 0

python3.14 -m unittest -v
# Ran 28 tests ... OK
# exit code 0
```

Post-VERIFY unittest rerun (artifact scanner includes VERIFY.md):

```
python3.14 -m unittest -q
# Ran 28 tests ... OK
# exit code 0
```

## Summary

- Cases: 20
- Methods: 5
- Rows: 100
- Classifications: pass=14, expected_error=3, local_observation=9, context_only=1, version_skip=0, not_applicable=73, fail=0
- Unittest count: 28, all pass
- Wall-clock (clone + checkout + compile + run + test): 2 seconds

Key observations (all via real `itertools.batched()`):
- exact_division: 2 batches of 4, tuples match
- incomplete_final: lengths [4,4,2], order preserved, no drops
- strict_incomplete: ValueError after 2 complete batches, stage=iteration
- strict_exact: pass, 2 batches, tuples match
- zero/negative_batch_size: ValueError at construction
- lazy_consumption: 3 items consumed
- single_pass: exhausted=true, order preserved
- naive_empty_batch: seen=true, classified `local_observation`
- token_counts_match: true (via `itertools.batched()`)
- batch_mean: global=2.0, weighted=2.0, unweighted=5.0 (via `itertools.batched()`)
- dropped_tail: count=1, ids=['r4'], global_pos=0.2, dropped_pos=0.0, batched_pos=0.2, dropped batch derived from real `batched()` output, order preserved, full retention verified
- score_equivalence: serial == batched, sumprod agrees (hash recorded), incomplete final batch retained (via `itertools.batched()`)

JSON, CSV, and RESULTS counts agree.
Artifact scan: no prohibited home-directory paths, temp paths, internal install paths, credentials, API keys, tokens, or path-bearing tracebacks in any committed JSON, CSV, or Markdown file, including VERIFY.md. 28 tests pass with VERIFY.md present.

Version skips: 0
Failures: 0
