# RESULTS

Python: 3.14.6
Executable: /python-lab/.local/bin/python3.14
Implementation: CPython
Platform: Linux-6.17.0-1009-aws-x86_64-with-glibc2.39
Discovery tried: python3.14
Selected: /python-lab/.local/bin/python3.14
itertools.batched available: True
strict option available: True
strict behavior confirmed: True
math.sumprod available: True

Cases: 20
Methods: 5
Rows: 100

Classifications:
- pass: 14
- expected_error: 3
- local_observation: 9
- context_only: 1
- not_applicable: 73
- fail: 0

## Observations

- exact_division: [4, 4] batches=2
- incomplete_final: lengths=[4, 4, 2] order_preserved=True
- strict_incomplete: classification=expected_error batches_before_error=2 stage=iteration
- strict_exact: classification=pass batches=2
- zero_batch_size: expected_error stage=construction
- negative_batch_size: expected_error stage=construction
- lazy_consumption: consumed=3
- single_pass: exhausted=True
- naive_empty_batch: seen=True
- token_counts_match: True
- batch_mean: global=2.0 weighted=2.0 unweighted=5.0
- dropped_tail: count=1 ids=['r4'] global_pos=0.2 dropped_pos=0.0 batched_pos=0.2
- score_equivalence: serial_hash=a6254221507eb9037927cbd07603abb48e433928332883a75734d531fa12d08a batched_hash=a6254221507eb9037927cbd07603abb48e433928332883a75734d531fa12d08a

Lab makes no claim that batching improves training speed, accuracy, statistical validity, or determinism.
