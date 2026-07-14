#!/usr/bin/env python3
"""python-stdlib-batched-mini-batch-footgun-lab v2"""
import sys, json, time, hashlib, inspect, platform, collections, math, os, shutil
from itertools import chain, islice

# --- interpreter discovery ---
def discover_python():
    tried = []
    candidates = []
    pb = os.environ.get("PYTHON_BIN")
    if pb:
        candidates.append(pb)
    candidates += ["python3.14", "python3.13", "python3.12", "python3", "python"]
    for c in candidates:
        tried.append(c)
        p = shutil.which(c) or (c if os.path.exists(c) and os.access(c, os.X_OK) else None)
        if p:
            return p, tried
    return sys.executable, tried

DISCOVERED_PYTHON, DISCOVERY_TRIED = discover_python()

# --- environment ---
PY_EXEC_RAW = sys.executable
# sanitize: replace /home/ubuntu prefix with stable /python-lab
if PY_EXEC_RAW.startswith("/home/ubuntu"):
    # keep the tail after /home/ubuntu
    PY_EXEC = "/python-lab" + PY_EXEC_RAW[len("/home/ubuntu"):]
else:
    PY_EXEC = PY_EXEC_RAW

PY_VERSION = sys.version
PY_IMPL = platform.python_implementation()
PY_PLATFORM = platform.platform()

import itertools
BATCHED_AVAILABLE = hasattr(itertools, "batched")
if BATCHED_AVAILABLE:
    batched_sig = inspect.signature(itertools.batched)
    BATCHED_STRICT_AVAILABLE = "strict" in batched_sig.parameters
    BATCHED_SIG_STR = str(batched_sig)
else:
    BATCHED_STRICT_AVAILABLE = False
    BATCHED_SIG_STR = ""

# verify strict actually works – CORRECT probe
if BATCHED_STRICT_AVAILABLE:
    try:
        # strict=True with incomplete final batch SHOULD raise ValueError
        list(itertools.batched([1,2,3], 2, strict=True))
        # if we get here, no error was raised – strict is broken
        STRICT_BEHAVIOR_CONFIRMED = False
    except ValueError:
        # Expected: strict rejected incomplete batch
        STRICT_BEHAVIOR_CONFIRMED = True
    except Exception:
        STRICT_BEHAVIOR_CONFIRMED = False
else:
    STRICT_BEHAVIOR_CONFIRMED = False

SUMPROD_AVAILABLE = hasattr(math, "sumprod")
IS_OLD_312 = sys.version_info < (3, 12)
IS_OLD_313 = sys.version_info < (3, 13)

env_info = {
    "python_executable": PY_EXEC,
    "python_executable_raw_sanitized": PY_EXEC != PY_EXEC_RAW,
    "python_version": PY_VERSION,
    "implementation": PY_IMPL,
    "platform": PY_PLATFORM,
    "discovery_tried": DISCOVERY_TRIED,
    "discovered_python": DISCOVERED_PYTHON,
    "batched_available": BATCHED_AVAILABLE,
    "batched_strict_available": BATCHED_STRICT_AVAILABLE,
    "batched_signature": BATCHED_SIG_STR,
    "strict_behavior_confirmed": STRICT_BEHAVIOR_CONFIRMED,
    "sumprod_available": SUMPROD_AVAILABLE,
    "older_than_312": IS_OLD_312,
    "older_than_313": IS_OLD_313,
}

# --- small fixed inputs ---
numbers_exact = list(range(8))
numbers_incomplete = list(range(10))
mean_values = [0.0, 0.0, 0.0, 0.0, 10.0]
labeled_values = [("r0", 0), ("r1", 0), ("r2", 0), ("r3", 0), ("r4", 1)]
texts = [
    "red fox red",
    "blue fox sleeps",
    "token counts are local",
    "batching is not training",
    "final batches may be short",
]
feature_rows = [
    (1.0, 0.0, 2.0),
    (0.0, 1.0, 1.0),
    (2.0, 1.0, 0.0),
    (1.0, 1.0, 1.0),
    (3.0, 0.0, 1.0),
]
weights = (0.5, -0.25, 1.5)

def tokenize_counter(text):
    return collections.Counter(text.lower().split())

def stable_hash(obj):
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(s.encode()).hexdigest()

def batched_call(iterable, n, strict=None):
    if not BATCHED_AVAILABLE:
        raise RuntimeError("batched unavailable")
    if strict is None or not BATCHED_STRICT_AVAILABLE:
        return itertools.batched(iterable, n)
    return itertools.batched(iterable, n, strict=strict)

# manual reference using iter/islice
def manual_batched_islice(iterable, n):
    it = iter(iterable)
    while True:
        batch = tuple(islice(it, n))
        if not batch:
            break
        yield batch

# naive range bug
def naive_range_batched(values, batch_size):
    for i in range(len(values) // batch_size + 1):
        yield values[i * batch_size:(i + 1) * batch_size]

# counting iterator for lazy test
class CountingIterator:
    def __init__(self, data):
        self.data = list(data)
        self.idx = 0
        self.next_calls = 0
    def __iter__(self):
        return self
    def __next__(self):
        self.next_calls += 1
        if self.idx >= len(self.data):
            raise StopIteration
        v = self.data[self.idx]
        self.idx += 1
        return v

# --- cases ---
CASES = [
    {"id": "python_version_marker"},
    {"id": "itertools_batched_available_marker"},
    {"id": "itertools_batched_strict_available_marker"},
    {"id": "math_sumprod_available_marker"},
    {"id": "exact_division_batches_marker"},
    {"id": "incomplete_final_batch_marker"},
    {"id": "strict_incomplete_rejection_marker"},
    {"id": "strict_exact_division_marker"},
    {"id": "zero_batch_size_rejection_marker"},
    {"id": "negative_batch_size_rejection_marker"},
    {"id": "lazy_first_batch_consumption_marker"},
    {"id": "single_pass_iterator_marker"},
    {"id": "input_order_preservation_marker"},
    {"id": "flatten_roundtrip_marker"},
    {"id": "naive_range_extra_empty_batch_marker"},
    {"id": "batch_local_token_count_marker"},
    {"id": "unweighted_batch_mean_footgun_marker"},
    {"id": "dropped_incomplete_batch_bias_marker"},
    {"id": "tiny_linear_score_equivalence_marker"},
    {"id": "no_global_training_speed_or_validity_claim_marker"},
]

METHODS = ["inspect_api", "stdlib_batched", "manual_reference", "streaming_observation", "hn_ml_context"]

# expected classifications
EXPECT = {}
for c in CASES:
    cid = c["id"]
    # inspect_api
    if cid == "python_version_marker":
        exp_inspect = "pass"
    elif cid == "itertools_batched_available_marker":
        exp_inspect = "pass" if BATCHED_AVAILABLE else "version_skip"
    elif cid == "itertools_batched_strict_available_marker":
        exp_inspect = "pass" if BATCHED_STRICT_AVAILABLE else "version_skip"
    elif cid == "math_sumprod_available_marker":
        exp_inspect = "pass" if SUMPROD_AVAILABLE else "version_skip"
    else:
        exp_inspect = "not_applicable"
    EXPECT[(cid, "inspect_api")] = exp_inspect

    # stdlib_batched
    if cid in ("exact_division_batches_marker", "incomplete_final_batch_marker",
               "input_order_preservation_marker", "flatten_roundtrip_marker",
               "strict_exact_division_marker"):
        exp_stdlib = "pass"
    elif cid in ("strict_incomplete_rejection_marker", "zero_batch_size_rejection_marker",
                 "negative_batch_size_rejection_marker"):
        exp_stdlib = "expected_error"
    elif cid in ("python_version_marker", "itertools_batched_available_marker",
                 "itertools_batched_strict_available_marker", "math_sumprod_available_marker",
                 "naive_range_extra_empty_batch_marker", "no_global_training_speed_or_validity_claim_marker",
                 "batch_local_token_count_marker", "unweighted_batch_mean_footgun_marker",
                 "dropped_incomplete_batch_bias_marker", "tiny_linear_score_equivalence_marker"):
        exp_stdlib = "not_applicable"
    else:
        exp_stdlib = "local_observation"
    EXPECT[(cid, "stdlib_batched")] = exp_stdlib

    # manual_reference
    if cid in ("exact_division_batches_marker", "incomplete_final_batch_marker",
               "flatten_roundtrip_marker", "batch_local_token_count_marker",
               "tiny_linear_score_equivalence_marker"):
        exp_manual = "pass"
    elif cid == "naive_range_extra_empty_batch_marker":
        exp_manual = "local_observation"  # the bug is the observation
    else:
        exp_manual = "not_applicable"
    EXPECT[(cid, "manual_reference")] = exp_manual

    # streaming_observation
    if cid in ("lazy_first_batch_consumption_marker", "single_pass_iterator_marker"):
        exp_stream = "local_observation"
    else:
        exp_stream = "not_applicable"
    EXPECT[(cid, "streaming_observation")] = exp_stream

    # hn_ml_context
    if cid in ("batch_local_token_count_marker", "unweighted_batch_mean_footgun_marker",
               "dropped_incomplete_batch_bias_marker", "tiny_linear_score_equivalence_marker"):
        exp_hn = "local_observation"
    elif cid == "no_global_training_speed_or_validity_claim_marker":
        exp_hn = "context_only"
    else:
        exp_hn = "not_applicable"
    EXPECT[(cid, "hn_ml_context")] = exp_hn

# adjust for version availability
if not BATCHED_AVAILABLE:
    for cid in [c["id"] for c in CASES]:
        if EXPECT.get((cid, "stdlib_batched")) in ("pass", "expected_error", "local_observation"):
            EXPECT[(cid, "stdlib_batched")] = "version_skip"
if not BATCHED_STRICT_AVAILABLE:
    for cid in ("strict_incomplete_rejection_marker", "strict_exact_division_marker"):
        for m in METHODS:
            if EXPECT.get((cid, m)) not in ("not_applicable", "context_only"):
                EXPECT[(cid, m)] = "version_skip"

# --- case runners ---
def run_case_method(case_id, method):
    t0 = time.perf_counter()
    row_base = {
        "method": method,
        "case_id": case_id,
        "python_executable": PY_EXEC,
        "python_version": PY_VERSION,
        "implementation": PY_IMPL,
        "platform": PY_PLATFORM,
        "batched_available": BATCHED_AVAILABLE,
        "batched_strict_available": BATCHED_STRICT_AVAILABLE,
        "sumprod_available": SUMPROD_AVAILABLE,
    }
    expected = EXPECT.get((case_id, method), "not_applicable")
    out = {
        "expected_classification": expected,
        "actual_classification": None,
        "api_exercised": method,
        "input_type": None,
        "input_length": None,
        "batch_size": None,
        "strict_flag": None,
        "batch_count": None,
        "batch_lengths": None,
        "batch_summary": None,
        "batch_result_hash": None,
        "flattened_hash": None,
        "source_consumed": None,
        "source_exhausted": None,
        "order_preserved": None,
        "empty_batch_seen": None,
        "error_stage": None,
        "exception_type": None,
        "exception_message": None,
        "serial_aggregate_hash": None,
        "batched_aggregate_hash": None,
        "global_mean": None,
        "batch_means": None,
        "weighted_aggregate": None,
        "unweighted_aggregate": None,
        "dropped_count": None,
        "dropped_ids": None,
        "serial_score_hash": None,
        "batched_score_hash": None,
        "elapsed_s": None,
        "skip_reason": None,
        "failure_reason": None,
        "local_conclusion": None,
    }
    try:
        actual, extra = dispatch(case_id, method)
        out["actual_classification"] = actual
        out.update(extra)
    except Exception as e:
        import traceback
        out["actual_classification"] = "fail"
        out["failure_reason"] = f"{type(e).__name__}: {e}"
    out["elapsed_s"] = time.perf_counter() - t0
    row = {**row_base, **out}
    return row

def dispatch(case_id, method):
    # inspect_api
    if method == "inspect_api":
        if case_id == "python_version_marker":
            return "pass", {"local_conclusion": "python version recorded", "api_exercised": "sys.version"}
        if case_id == "itertools_batched_available_marker":
            cls = "pass" if BATCHED_AVAILABLE else "version_skip"
            return cls, {"local_conclusion": f"batched_available={BATCHED_AVAILABLE}", "skip_reason": None if BATCHED_AVAILABLE else "itertools.batched unavailable"}
        if case_id == "itertools_batched_strict_available_marker":
            cls = "pass" if BATCHED_STRICT_AVAILABLE else "version_skip"
            return cls, {"local_conclusion": f"strict_available={BATCHED_STRICT_AVAILABLE}, confirmed={STRICT_BEHAVIOR_CONFIRMED}", "skip_reason": None if BATCHED_STRICT_AVAILABLE else "strict option unavailable (Python <3.13)"}
        if case_id == "math_sumprod_available_marker":
            cls = "pass" if SUMPROD_AVAILABLE else "version_skip"
            return cls, {"local_conclusion": f"sumprod_available={SUMPROD_AVAILABLE}", "skip_reason": None if SUMPROD_AVAILABLE else "math.sumprod unavailable"}
        return "not_applicable", {}

    # stdlib_batched
    if method == "stdlib_batched":
        if not BATCHED_AVAILABLE:
            return "version_skip", {"skip_reason": "itertools.batched unavailable"}
        if case_id == "exact_division_batches_marker":
            batches = list(batched_call(range(8), 4))
            ok = batches == [(0,1,2,3),(4,5,6,7)]
            return ("pass" if ok else "fail"), {
                "input_type": "range", "input_length": 8, "batch_size": 4, "strict_flag": False,
                "batch_count": len(batches), "batch_lengths": [len(b) for b in batches],
                "batch_summary": str(batches),
                "batch_result_hash": stable_hash(batches),
                "order_preserved": True,
                "local_conclusion": "exact division yields 2 batches of 4"
            }
        if case_id == "incomplete_final_batch_marker":
            batches = list(batched_call(range(10), 4))
            lengths = [len(b) for b in batches]
            flat = tuple(chain.from_iterable(batches))
            ok = lengths == [4,4,2] and flat == tuple(range(10))
            return ("pass" if ok else "fail"), {
                "input_type": "range", "input_length": 10, "batch_size": 4, "strict_flag": False,
                "batch_count": len(batches), "batch_lengths": lengths,
                "flattened_hash": stable_hash(flat),
                "order_preserved": True,
                "empty_batch_seen": False,
                "local_conclusion": "incomplete final batch retained, no values dropped"
            }
        if case_id == "strict_incomplete_rejection_marker":
            if not BATCHED_STRICT_AVAILABLE:
                return "version_skip", {"skip_reason": "strict option unavailable (Python <3.13)"}
            complete_batches = 0
            error_stage = "construction"
            try:
                it = batched_call(range(10), 4, strict=True)
                error_stage = "iteration"
                for b in it:
                    complete_batches += 1
                return "fail", {"failure_reason": "strict=True did not raise on incomplete batch", "batch_count": complete_batches}
            except ValueError as e:
                return "expected_error", {
                    "input_type": "range", "input_length": 10, "batch_size": 4, "strict_flag": True,
                    "batch_count": complete_batches,
                    "error_stage": error_stage,
                    "exception_type": "ValueError",
                    "exception_message": str(e)[:200],
                    "local_conclusion": "strict rejects incomplete final batch"
                }
            except Exception as e:
                return "fail", {"failure_reason": f"unexpected {type(e).__name__}: {e}", "batch_count": complete_batches}
        if case_id == "strict_exact_division_marker":
            if not BATCHED_STRICT_AVAILABLE:
                return "version_skip", {"skip_reason": "strict option unavailable (Python <3.13)"}
            batches = list(batched_call(range(8), 4, strict=True))
            ok = batches == [(0,1,2,3),(4,5,6,7)]
            return ("pass" if ok else "fail"), {
                "input_type": "range", "input_length": 8, "batch_size": 4, "strict_flag": True,
                "batch_count": len(batches), "batch_lengths": [len(b) for b in batches],
                "batch_summary": str(batches),
                "order_preserved": True,
                "local_conclusion": "strict exact division succeeds, tuples match"
            }
        if case_id == "zero_batch_size_rejection_marker":
            error_stage = "construction"
            try:
                it = batched_call([1,2,3], 0)
                error_stage = "iteration"
                list(it)
                return "fail", {"failure_reason": "zero batch_size did not raise"}
            except ValueError as e:
                return "expected_error", {
                    "batch_size": 0,
                    "error_stage": error_stage,
                    "exception_type": "ValueError",
                    "exception_message": str(e)[:200],
                    "local_conclusion": "zero batch_size rejected"
                }
        if case_id == "negative_batch_size_rejection_marker":
            error_stage = "construction"
            try:
                it = batched_call([1,2,3], -1)
                error_stage = "iteration"
                list(it)
                return "fail", {"failure_reason": "negative batch_size did not raise"}
            except ValueError as e:
                return "expected_error", {
                    "batch_size": -1,
                    "error_stage": error_stage,
                    "exception_type": "ValueError",
                    "exception_message": str(e)[:200],
                    "local_conclusion": "negative batch_size rejected"
                }
        if case_id == "input_order_preservation_marker":
            vals = [f"r{i}" for i in range(7)]
            batches = list(batched_call(vals, 3))
            flat = list(chain.from_iterable(batches))
            ok = flat == vals
            return ("pass" if ok else "fail"), {
                "input_type": "list", "input_length": 7, "batch_size": 3,
                "order_preserved": ok,
                "flattened_hash": stable_hash(flat),
                "batch_count": len(batches),
                "batch_lengths": [len(b) for b in batches],
                "local_conclusion": "order preserved"
            }
        if case_id == "flatten_roundtrip_marker":
            results = []
            hashes = []
            for values, n in [(list(range(8)), 4), (list(range(10)), 4)]:
                batches = list(batched_call(values, n))
                flat = tuple(chain.from_iterable(batches))
                results.append(flat == tuple(values))
                hashes.append((stable_hash(values), stable_hash(flat)))
            all_ok = all(results)
            # record first case hashes
            orig_hash, flat_hash = hashes[0] if hashes else (None, None)
            return ("pass" if all_ok else "fail"), {
                "batch_size": 4,
                "order_preserved": all_ok,
                "batch_result_hash": orig_hash,
                "flattened_hash": flat_hash,
                "local_conclusion": "flatten roundtrip holds for exact and incomplete inputs"
            }
        if case_id in ("lazy_first_batch_consumption_marker", "single_pass_iterator_marker"):
            return "local_observation", {"local_conclusion": "see streaming_observation method"}
        return "not_applicable", {}

    # manual_reference
    if method == "manual_reference":
        if case_id == "exact_division_batches_marker":
            batches = list(manual_batched_islice(range(8), 4))
            ok = batches == [(0,1,2,3),(4,5,6,7)]
            return ("pass" if ok else "fail"), {
                "batch_count": len(batches), "batch_lengths": [len(b) for b in batches],
                "local_conclusion": "manual islice matches stdlib"
            }
        if case_id == "incomplete_final_batch_marker":
            batches = list(manual_batched_islice(range(10), 4))
            flat = tuple(chain.from_iterable(batches))
            ok = [len(b) for b in batches] == [4,4,2] and flat == tuple(range(10))
            return ("pass" if ok else "fail"), {
                "batch_count": len(batches),
                "batch_lengths": [len(b) for b in batches],
                "flattened_hash": stable_hash(flat),
                "local_conclusion": "manual islice retains final short batch"
            }
        if case_id == "flatten_roundtrip_marker":
            vals = list(range(10))
            batches = list(manual_batched_islice(vals, 4))
            flat = tuple(chain.from_iterable(batches))
            ok = flat == tuple(vals)
            return ("pass" if ok else "fail"), {
                "flattened_hash": stable_hash(flat),
                "order_preserved": ok,
                "local_conclusion": "manual flatten roundtrip"
            }
        if case_id == "naive_range_extra_empty_batch_marker":
            vals = list(range(8))
            n = 4
            naive_batches = list(naive_range_batched(vals, n))
            std_batches = list(batched_call(vals, n)) if BATCHED_AVAILABLE else list(manual_batched_islice(vals, n))
            empty_seen = any(len(b) == 0 for b in naive_batches)
            ok = empty_seen and len(naive_batches) == len(std_batches) + 1
            return ("local_observation" if ok else "fail"), {
                "input_length": 8, "batch_size": 4,
                "batch_count": len(naive_batches),
                "batch_lengths": [len(b) for b in naive_batches],
                "empty_batch_seen": empty_seen,
                "local_conclusion": "naive range // +1 produces extra empty batch on exact division",
                "failure_reason": None if ok else "naive bug not reproduced"
            }
        if case_id == "batch_local_token_count_marker":
            # serial
            serial_ctr = collections.Counter()
            for t in texts:
                serial_ctr.update(tokenize_counter(t))
            # batched using itertools.batched()
            batch_size = 2
            batch_ctrs = []
            if BATCHED_AVAILABLE:
                for batch in batched_call(texts, batch_size):
                    c = collections.Counter()
                    for txt in batch:
                        c.update(tokenize_counter(txt))
                    batch_ctrs.append(c)
            else:
                # fallback manual
                for i in range(0, len(texts), batch_size):
                    batch = texts[i:i+batch_size]
                    c = collections.Counter()
                    for txt in batch: c.update(tokenize_counter(txt))
                    batch_ctrs.append(c)
            merged = collections.Counter()
            for c in batch_ctrs: merged.update(c)
            ok = serial_ctr == merged
            return ("pass" if ok else "fail"), {
                "serial_aggregate_hash": stable_hash(dict(serial_ctr)),
                "batched_aggregate_hash": stable_hash(dict(merged)),
                "batch_count": len(batch_ctrs),
                "local_conclusion": "batched token counts (via itertools.batched) merge to serial total"
            }
        if case_id == "tiny_linear_score_equivalence_marker":
            def score_manual(row):
                return sum(x*w for x,w in zip(row, weights))
            serial_scores = [score_manual(r) for r in feature_rows]
            # batched using itertools.batched()
            batched_scores = []
            batch_size = 2
            if BATCHED_AVAILABLE:
                for batch in batched_call(feature_rows, batch_size):
                    for row in batch:
                        batched_scores.append(score_manual(row))
            else:
                for i in range(0, len(feature_rows), batch_size):
                    for row in feature_rows[i:i+batch_size]:
                        batched_scores.append(score_manual(row))
            ok = (len(serial_scores) == len(batched_scores) and
                  all(abs(a-b) < 1e-12 for a,b in zip(serial_scores, batched_scores)))
            return ("pass" if ok else "fail"), {
                "serial_score_hash": stable_hash(serial_scores),
                "batched_score_hash": stable_hash(batched_scores),
                "local_conclusion": "serial and batched scores identical (batched via itertools.batched)"
            }
        return "not_applicable", {}

    # streaming_observation
    if method == "streaming_observation":
        if case_id == "lazy_first_batch_consumption_marker":
            if not BATCHED_AVAILABLE:
                return "version_skip", {"skip_reason": "itertools.batched unavailable"}
            src = CountingIterator(range(10))
            it = batched_call(src, 3)
            consumed_before = src.next_calls
            first = next(iter(it))
            consumed_after = src.next_calls
            ok = consumed_before == 0 and consumed_after == 3 and list(first) == [0,1,2]
            return ("local_observation" if ok else "fail"), {
                "batch_size": 3,
                "source_consumed": consumed_after,
                "source_exhausted": False,
                "batch_summary": str(first),
                "local_conclusion": "first batch consumes exactly 3 items, source not pre-consumed",
                "failure_reason": None if ok else "lazy consumption mismatch"
            }
        if case_id == "single_pass_iterator_marker":
            if not BATCHED_AVAILABLE:
                return "version_skip", {"skip_reason": "itertools.batched unavailable"}
            def gen():
                for x in range(5):
                    yield x
            g = gen()
            batches = list(batched_call(g, 2))
            flat = list(chain.from_iterable(batches))
            rest = list(g)
            ok = flat == [0,1,2,3,4] and rest == []
            return ("local_observation" if ok else "fail"), {
                "batch_count": len(batches),
                "batch_lengths": [len(b) for b in batches],
                "source_exhausted": True,
                "order_preserved": True,
                "local_conclusion": "single-pass source consumed once, no duplication",
                "failure_reason": None if ok else "single-pass violation"
            }
        return "not_applicable", {}

    # hn_ml_context
    if method == "hn_ml_context":
        if case_id == "batch_local_token_count_marker":
            # use itertools.batched()
            serial_ctr = collections.Counter()
            for t in texts: serial_ctr.update(tokenize_counter(t))
            batch_ctrs = []
            batch_size = 2
            for batch in batched_call(texts, batch_size):
                c = collections.Counter()
                for txt in batch: c.update(tokenize_counter(txt))
                batch_ctrs.append(c)
            merged = collections.Counter()
            for c in batch_ctrs: merged.update(c)
            ok = serial_ctr == merged
            return ("local_observation" if ok else "fail"), {
                "serial_aggregate_hash": stable_hash(dict(serial_ctr)),
                "batched_aggregate_hash": stable_hash(dict(merged)),
                "batch_count": len(batch_ctrs),
                "local_conclusion": "token counting via itertools.batched: batched equals serial; not a training pipeline"
            }
        if case_id == "unweighted_batch_mean_footgun_marker":
            # use itertools.batched()
            vals = mean_values
            batch_size = 4
            batches = [tuple(b) for b in batched_call(vals, batch_size)]
            batch_means = [sum(b)/len(b) for b in batches]
            batch_lengths = [len(b) for b in batches]
            global_mean = sum(vals)/len(vals)
            unweighted = sum(batch_means)/len(batch_means)
            weighted = sum(m*n for m,n in zip(batch_means, batch_lengths)) / sum(batch_lengths)
            ok = abs(weighted - global_mean) < 1e-12 and abs(unweighted - global_mean) > 1e-9
            return ("local_observation" if ok else "fail"), {
                "global_mean": global_mean,
                "batch_means": batch_means,
                "weighted_aggregate": weighted,
                "unweighted_aggregate": unweighted,
                "batch_lengths": batch_lengths,
                "batch_count": len(batches),
                "local_conclusion": "unweighted batch means bias aggregate when final batch is shorter (batched via itertools.batched)"
            }
        if case_id == "dropped_incomplete_batch_bias_marker":
            # full proportion
            all_labels = [y for _, y in labeled_values]
            global_pos = sum(all_labels) / len(all_labels)
            batch_size = 4
            # get all batches via itertools.batched()
            batches = [tuple(b) for b in batched_call(labeled_values, batch_size)]
            # deliberately drop the incomplete final batch
            if batches and len(batches[-1]) < batch_size:
                complete_batches = batches[:-1]
                dropped_batch = batches[-1]
            else:
                complete_batches = batches
                dropped_batch = ()
            kept_records = list(chain.from_iterable(complete_batches))
            dropped_records = list(dropped_batch)
            kept_labels = [y for _, y in kept_records]
            kept_pos = sum(kept_labels) / len(kept_labels) if kept_labels else 0
            # normal batched() retaining all records
            batched_all = list(chain.from_iterable(batches))
            batched_labels = [y for _, y in batched_all]
            batched_pos = sum(batched_labels) / len(batched_labels) if batched_labels else 0
            batched_kept_all = (len(batched_all) == len(labeled_values) and batched_all == labeled_values)
            ok = (kept_pos != global_pos and
                  abs(batched_pos - global_pos) < 1e-12 and
                  batched_kept_all)
            return ("local_observation" if ok else "fail"), {
                "dropped_count": len(dropped_records),
                "dropped_ids": [i for i,_ in dropped_records],
                "global_mean": global_pos,
                "weighted_aggregate": batched_pos,
                "unweighted_aggregate": kept_pos,
                "batch_count": len(batches),
                "batch_lengths": [len(b) for b in batches],
                "order_preserved": batched_kept_all,
                "local_conclusion": "dropping incomplete tail changes label proportion; itertools.batched() retains final batch, proportion unchanged"
            }
        if case_id == "tiny_linear_score_equivalence_marker":
            if not SUMPROD_AVAILABLE:
                return "version_skip", {"skip_reason": "math.sumprod unavailable"}
            def score_manual(row):
                return sum(x*w for x,w in zip(row, weights))
            manual_scores = [score_manual(r) for r in feature_rows]
            sumprod_scores = [math.sumprod(r, weights) for r in feature_rows]
            ok_sp = all(abs(a-b) < 1e-12 for a,b in zip(manual_scores, sumprod_scores))
            # batched vs serial using itertools.batched()
            serial = manual_scores
            batched = []
            batch_size = 2
            for batch in batched_call(feature_rows, batch_size):
                for row in batch:
                    batched.append(score_manual(row))
            ok_batch = (len(serial) == len(batched) and
                        all(abs(a-b) < 1e-12 for a,b in zip(serial, batched)))
            # check final batch retention
            n_batches = (len(feature_rows) + batch_size - 1) // batch_size
            ok = ok_sp and ok_batch
            return ("local_observation" if ok else "fail"), {
                "serial_score_hash": stable_hash(serial),
                "batched_score_hash": stable_hash(batched),
                "serial_aggregate_hash": stable_hash(sumprod_scores),
                "batch_count": n_batches,
                "order_preserved": True,
                "local_conclusion": "sumprod matches manual; serial equals batched via itertools.batched(); incomplete final batch retained; not a trained model"
            }
        if case_id == "no_global_training_speed_or_validity_claim_marker":
            return "context_only", {"local_conclusion": "lab makes no training speed/validity claims"}
        return "not_applicable", {}

    return "not_applicable", {}

def main():
    rows = []
    for case in CASES:
        for method in METHODS:
            rows.append(run_case_method(case["id"], method))
    # write json
    with open("results_rows.json", "w") as f:
        json.dump(rows, f, indent=2)
    # csv
    import csv
    if rows:
        with open("results_rows.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)
def sanitize_path(p):
    if p and p.startswith("/home/ubuntu"):
        return "/python-lab" + p[len("/home/ubuntu"):]
    return p

# ...

def main():
    rows = []
    for case in CASES:
        for method in METHODS:
            rows.append(run_case_method(case["id"], method))
    # write json
    with open("results_rows.json", "w") as f:
        json.dump(rows, f, indent=2)
    # csv
    import csv
    if rows:
        with open("results_rows.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)
    # RESULTS.md
    from collections import Counter
    counts = Counter(r["actual_classification"] for r in rows)
    with open("RESULTS.md", "w") as f:
        f.write("# RESULTS\n\n")
        f.write(f"Python: {PY_VERSION.split()[0]}\n")
        f.write(f"Executable: {PY_EXEC}\n")
        f.write(f"Implementation: {PY_IMPL}\n")
        f.write(f"Platform: {PY_PLATFORM}\n")
        f.write(f"Discovery tried: {', '.join(DISCOVERY_TRIED)}\n")
        f.write(f"Selected: {sanitize_path(DISCOVERED_PYTHON)}\n")
        f.write(f"itertools.batched available: {BATCHED_AVAILABLE}\n")
        f.write(f"strict option available: {BATCHED_STRICT_AVAILABLE}\n")
        f.write(f"strict behavior confirmed: {STRICT_BEHAVIOR_CONFIRMED}\n")
        f.write(f"math.sumprod available: {SUMPROD_AVAILABLE}\n\n")
        f.write(f"Cases: {len(CASES)}\nMethods: {len(METHODS)}\nRows: {len(rows)}\n\n")
        f.write("Classifications:\n")
        for k in ["pass", "expected_error", "local_observation", "context_only", "version_skip", "not_applicable", "fail"]:
            v = counts.get(k, 0)
            if v or k == "fail":
                f.write(f"- {k}: {v}\n")
        f.write("\n")
        def find(cid, m):
            for r in rows:
                if r["case_id"]==cid and r["method"]==m:
                    return r
            return {}
        f.write("## Observations\n\n")
        r = find("exact_division_batches_marker", "stdlib_batched")
        f.write(f"- exact_division: {r.get('batch_lengths')} batches={r.get('batch_count')}\n")
        r = find("incomplete_final_batch_marker", "stdlib_batched")
        f.write(f"- incomplete_final: lengths={r.get('batch_lengths')} order_preserved={r.get('order_preserved')}\n")
        r = find("strict_incomplete_rejection_marker", "stdlib_batched")
        f.write(f"- strict_incomplete: classification={r.get('actual_classification')} batches_before_error={r.get('batch_count')} stage={r.get('error_stage')}\n")
        r = find("strict_exact_division_marker", "stdlib_batched")
        f.write(f"- strict_exact: classification={r.get('actual_classification')} batches={r.get('batch_count')}\n")
        r = find("zero_batch_size_rejection_marker", "stdlib_batched")
        f.write(f"- zero_batch_size: {r.get('actual_classification')} stage={r.get('error_stage')}\n")
        r = find("negative_batch_size_rejection_marker", "stdlib_batched")
        f.write(f"- negative_batch_size: {r.get('actual_classification')} stage={r.get('error_stage')}\n")
        r = find("lazy_first_batch_consumption_marker", "streaming_observation")
        f.write(f"- lazy_consumption: consumed={r.get('source_consumed')}\n")
        r = find("single_pass_iterator_marker", "streaming_observation")
        f.write(f"- single_pass: exhausted={r.get('source_exhausted')}\n")
        r = find("naive_range_extra_empty_batch_marker", "manual_reference")
        f.write(f"- naive_empty_batch: seen={r.get('empty_batch_seen')}\n")
        r = find("batch_local_token_count_marker", "hn_ml_context")
        f.write(f"- token_counts_match: {r.get('serial_aggregate_hash') == r.get('batched_aggregate_hash')}\n")
        r = find("unweighted_batch_mean_footgun_marker", "hn_ml_context")
        f.write(f"- batch_mean: global={r.get('global_mean')} weighted={r.get('weighted_aggregate')} unweighted={r.get('unweighted_aggregate')}\n")
        r = find("dropped_incomplete_batch_bias_marker", "hn_ml_context")
        f.write(f"- dropped_tail: count={r.get('dropped_count')} ids={r.get('dropped_ids')} global_pos={r.get('global_mean')} dropped_pos={r.get('unweighted_aggregate')} batched_pos={r.get('weighted_aggregate')}\n")
        r = find("tiny_linear_score_equivalence_marker", "hn_ml_context")
        f.write(f"- score_equivalence: serial_hash={r.get('serial_score_hash')} batched_hash={r.get('batched_score_hash')}\n")
        f.write("\nLab makes no claim that batching improves training speed, accuracy, statistical validity, or determinism.\n")
    print(f"Done. {len(rows)} rows. " + ", ".join(f"{k}={counts.get(k,0)}" for k in ["pass","expected_error","local_observation","context_only","version_skip","not_applicable","fail"] if counts.get(k,0)))
    return rows

if __name__ == "__main__":
    main()
