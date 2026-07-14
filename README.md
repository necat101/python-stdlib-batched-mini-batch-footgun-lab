# python-stdlib-batched-mini-batch-footgun-lab

A tiny, standard-library-only correctness lab for `itertools.batched()` (Python 3.12), incomplete final batches, the Python 3.13 `strict` option, lazy iterator consumption, hand-written batching bugs, and narrow deterministic mini-batching observations.

**No NumPy, no pandas, no scikit-learn, no model training, no GPU, no benchmarks, no downloads.**

## Results (Python 3.14.6)

- Interpreter discovery: `$PYTHON_BIN`, `python3.14`, `python3.13`, `python3.12`, `python3`, `python` → selected `python3.14`
- `itertools.batched` available: **yes**
- strict option available: **yes**
- strict behavior confirmed: **yes**
- `math.sumprod` available: **yes**
- Cases: 20 · Methods: 5 · Rows: 100
- pass: 14 · expected_error: 3 · local_observation: 9 · context_only: 1 · version_skip: 0 · not_applicable: 73 · fail: 0

Exact division (`range(8)`, n=4) → `[(0,1,2,3), (4,5,6,7)]`.
Incomplete final batch (`range(10)`, n=4) → lengths `[4,4,2]`, flattening reproduces input, no values dropped.
Strict incomplete rejection: `ValueError` after 2 complete batches, error stage: iteration.
Strict exact division: 2 batches, tuples match, order preserved.
Zero / negative batch size → `ValueError` at construction.
Lazy consumption: first batch consumes exactly 3 source items, source not pre-consumed.
Single-pass iterator: no duplication, source exhausted once.
Order preserved, flatten roundtrip holds.
Naive `range(len(vals)//n + 1)` recipe produces an extra empty batch on exact division – `itertools.batched()` does not. Classified as `local_observation`.
Token counts (via `itertools.batched()`): batched equals serial.
Batch means (via `itertools.batched()`): weighted aggregate matches global mean; unweighted aggregate does not (final batch shorter).
Dropped tail (via `itertools.batched()`): dropping the incomplete batch changes label proportion (0.2 → 0.0); normal non-strict `batched()` retains all 5 records, proportion unchanged at 0.2, order preserved.
Tiny linear scores (via `itertools.batched()`): `math.sumprod` matches manual dot product; serial equals batched; incomplete final batch retained.

**The lab does not prove** that batching makes Python code faster, that mini-batching improves model accuracy, that a particular batch size is optimal, that a shorter final batch should always be retained or always be dropped, that strict mode is preferable for every pipeline, that equal batch counts imply equal statistical weight, that averaging unweighted batch metrics is valid, that matching token counts prove a realistic preprocessing pipeline correct, that a tiny dot product is a trained or validated ML model, that batching makes parallel/distributed execution deterministic, that HN enthusiasm for `itertools.batched()` validates a machine-learning workflow, or that the Python 3.12 HN thread discussed the later Python 3.13 `strict` argument.

## Hacker News thread access

HN thread 37737519 ("Python 3.12") was read using:

```
python3 ./hackernews get-item --id 37737519
python3 ./hackernews get-item --id <comment_id>
```

via the bundled Hacker News CLI (`hackernews get-item --id <id>`) (real Hacker News Firebase API, no API key).

Evidence was captured in `hn_comments_sanitized.json` / `hn_thread_evidence.md` before the sentiment summary below was prepared.

### HN sentiment – `itertools.batched()`

Commenters welcomed `itertools.batched()` as a frequently reinvented helper:

- georgehotelling (37739502): "I'm just happy for itertools.batched for chunking iterables"
- philshem (37740297), replying to the above: "Yes. I've written explicit code that needed this 100s of times."
- kastden (37741068): "This is the greatest addition since f-strings!"
- miiiiiike (37757788): "Same but for the 'batch', 'ibatch', and 'abatch' functions I started writing back in 2008."

A handwritten range-based implementation immediately exposed an extra-empty-batch bug:

- intalentive (37743193) posted: `for i in range(len(lst) // batch_size + 1): batch = lst[i * batch_size : (i + 1) * batch_size]`
- hddqsb (37749075) replied: "You have a minor bug -- when len(lst) is a multiple of batch_size, this will have an extra iteration at the end with an empty batch. The fixed version is `range((len(lst) + batch_size - 1) // batch_size)`, which emulates `ceil(len(lst) / batch_size)`." They added: "Yet more proof that this should be part of stdlib :)"
- rossant (37750118): "Blatant reason why a native solution was long overdue."

hddqsb also compared slicing recipes with the `iter()` / `islice()` recipe: they suggested `for i in range(0, len(lst), batch_size): batch = lst[i:i+batch_size]` and noted "The docs give another pretty nice implementation using iter() and islice() in a loop (but it uses the walrus operator `:=` so it requires Python 3.8+ as written)." Slicing works for sequence types with known length; the `iter()` / `islice()` recipe works for arbitrary single-pass iterables.

`more-itertools` came up twice:

- ehsankia (37754712): "99% of my more_itertools imports are exactly for this."
- abyesilyurt (37762840): "Checkout more-itertools for more variants: https://pypi.org/project/more-itertools/"

Ruby's long-standing batching support came up:

- zem (37743832): "yeah! that's been in the ruby stdlib practically from day one, no idea why python was so resistant to it."

A small standard-library convenience can still remove recurring correctness mistakes: the extra empty batch in intalentive's posted code is exactly the kind of off-by-one error that a shared, tested stdlib function eliminates. The convenience function leaves policy decisions about incomplete batches to the caller – Python 3.12's `itertools.batched()` allows a short final batch by default.

The original Python 3.12 behavior allowed a short final batch. The `strict` keyword argument (rejecting incomplete final batches with `ValueError`) belongs to **Python 3.13**, not Python 3.12, and should not be attributed to the original release discussion at HN 37737519. No committed HN comment from thread 37737519 discusses the `strict` argument.

### HN – Python version adoption / installation friction

Separate from the batching discussion, the broader Python 3.12 release thread contained comments about Python version adoption and installation friction. The thread's top comment summarized breaking changes including the removal of `distutils` (PEP 632), `smtpd`, `asynchat`, `asyncore`, and `imp`, with a note that `setuptools` continues to provide `distutils` for users who need it (Python 3.12 release, 2023-10). Commenters discussed subinterpreter availability ("Too bad there's no Python API available yet :(" – scheduled for 3.13), typing improvements (PEP 692 `Unpack`, PEP 695 generic class syntax), performance improvements (~5% overall, PEP 709, BOLT), instrumentation / debugging (PEP 669 `sys.monitoring`), and packaging changes (distutils removal, `venv` no longer pre-installing `setuptools`). These version-adoption, packaging, typing, performance, instrumentation, and subinterpreter discussions are separate from the `itertools.batched()` discussion and should not be presented as commentary about batching specifically.

Batching records is relevant to data preparation but does not validate model training, accuracy, throughput, or statistical methodology. Excitement about a batching helper on HN does not prove that batching makes machine-learning training faster, statistically valid, deterministic, or free from data-loss and weighting bugs.

## Scope

- 20 deterministic cases, 5 methods, 100 rows
- Python stdlib only
- < 10 seconds runtime
- No network, no downloads, no training
- All ML-adjacent observations use real `itertools.batched()` calls

See RESULTS.md for full classification counts.

## Verify

```sh
python3 -m py_compile run_lab.py test_lab.py
python3 run_lab.py
python3 -m unittest -v
```

See VERIFY.md for clean-clone verification.
