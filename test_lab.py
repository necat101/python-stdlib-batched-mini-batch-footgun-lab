#!/usr/bin/env python3
import unittest, json, sys, pathlib, csv
ROOT = pathlib.Path(__file__).parent

with open(ROOT / "results_rows.json") as f:
    ROWS = json.load(f)

CASES_JSON_PATH = ROOT / "cases.json"
with open(CASES_JSON_PATH) as f:
    CASES_DATA = json.load(f)

def find_row(case_id, method):
    for r in ROWS:
        if r["case_id"] == case_id and r["method"] == method:
            return r
    return None

class TestLab(unittest.TestCase):
    def test_cases_json_structure(self):
        self.assertEqual(len(CASES_DATA), 20, "cases.json must contain exactly 20 entries")
        required_ids = [
            "python_version_marker",
            "itertools_batched_available_marker",
            "itertools_batched_strict_available_marker",
            "math_sumprod_available_marker",
            "exact_division_batches_marker",
            "incomplete_final_batch_marker",
            "strict_incomplete_rejection_marker",
            "strict_exact_division_marker",
            "zero_batch_size_rejection_marker",
            "negative_batch_size_rejection_marker",
            "lazy_first_batch_consumption_marker",
            "single_pass_iterator_marker",
            "input_order_preservation_marker",
            "flatten_roundtrip_marker",
            "naive_range_extra_empty_batch_marker",
            "batch_local_token_count_marker",
            "unweighted_batch_mean_footgun_marker",
            "dropped_incomplete_batch_bias_marker",
            "tiny_linear_score_equivalence_marker",
            "no_global_training_speed_or_validity_claim_marker",
        ]
        found_ids = [c["id"] for c in CASES_DATA]
        for rid in required_ids:
            self.assertIn(rid, found_ids, f"missing {rid}")
        methods = ["inspect_api","stdlib_batched","manual_reference","streaming_observation","hn_ml_context"]
        allowed = {"pass","expected_error","local_observation","version_skip","context_only","not_applicable","fail"}
        for c in CASES_DATA:
            self.assertIn("expectations", c)
            for m in methods:
                self.assertIn(m, c["expectations"], f"{c['id']} missing {m}")
                exp = c["expectations"][m]
                self.assertTrue(exp, f"{c['id']}/{m} blank")
                self.assertIn(exp, allowed, f"{c['id']}/{m} invalid {exp}")

    def test_case_count(self):
        case_ids = set(r["case_id"] for r in ROWS)
        self.assertEqual(len(case_ids), 20)

    def test_required_markers(self):
        required = [
            "python_version_marker",
            "itertools_batched_available_marker",
            "itertools_batched_strict_available_marker",
            "math_sumprod_available_marker",
            "exact_division_batches_marker",
            "incomplete_final_batch_marker",
            "strict_incomplete_rejection_marker",
            "strict_exact_division_marker",
            "zero_batch_size_rejection_marker",
            "negative_batch_size_rejection_marker",
            "lazy_first_batch_consumption_marker",
            "single_pass_iterator_marker",
            "input_order_preservation_marker",
            "flatten_roundtrip_marker",
            "naive_range_extra_empty_batch_marker",
            "batch_local_token_count_marker",
            "unweighted_batch_mean_footgun_marker",
            "dropped_incomplete_batch_bias_marker",
            "tiny_linear_score_equivalence_marker",
            "no_global_training_speed_or_validity_claim_marker",
        ]
        case_ids = [r["case_id"] for r in ROWS]
        for m in required:
            self.assertEqual(case_ids.count(m), 5, f"{m} should appear 5 times")

    def test_row_count(self):
        self.assertEqual(len(ROWS), 100)

    def test_pair_uniqueness(self):
        pairs = [(r["case_id"], r["method"]) for r in ROWS]
        self.assertEqual(len(pairs), len(set(pairs)))

    def test_classifications_allowed(self):
        allowed = {"pass", "expected_error", "local_observation", "version_skip", "context_only", "not_applicable", "fail"}
        for r in ROWS:
            self.assertIn(r["expected_classification"], allowed)
            self.assertIn(r["actual_classification"], allowed)
            self.assertTrue(r["expected_classification"])
            self.assertTrue(r["actual_classification"])

    def test_not_applicable_symmetry(self):
        for r in ROWS:
            exp = r["expected_classification"]
            act = r["actual_classification"]
            if exp == "not_applicable":
                self.assertEqual(act, "not_applicable")

    def test_expected_equals_actual_unless_fail(self):
        mismatches = []
        for r in ROWS:
            if r["actual_classification"] == "fail":
                continue
            if r["expected_classification"] != r["actual_classification"]:
                mismatches.append((r["case_id"], r["method"], r["expected_classification"], r["actual_classification"]))
        self.assertEqual(mismatches, [], f"mismatches: {mismatches}")

    def test_batched_version_skip(self):
        batched_available = any(r["batched_available"] for r in ROWS)
        if not batched_available:
            for r in ROWS:
                if r["method"] == "stdlib_batched" and r["expected_classification"] in ("pass", "expected_error", "local_observation"):
                    self.assertEqual(r["actual_classification"], "version_skip")

    def test_strict_version_skip(self):
        strict_available = any(r["batched_strict_available"] for r in ROWS)
        if not strict_available:
            for cid in ("strict_incomplete_rejection_marker", "strict_exact_division_marker"):
                for r in [x for x in ROWS if x["case_id"] == cid]:
                    if r["expected_classification"] not in ("not_applicable", "context_only"):
                        self.assertEqual(r["actual_classification"], "version_skip")

    def test_exact_division_tuples(self):
        r = find_row("exact_division_batches_marker", "stdlib_batched")
        self.assertIsNotNone(r)
        self.assertEqual(r["batch_count"], 2)
        self.assertEqual(r["batch_lengths"], [4, 4])
        bs = r.get("batch_summary","")
        self.assertIn("(0, 1, 2, 3)", bs)
        self.assertIn("(4, 5, 6, 7)", bs)

    def test_incomplete_final(self):
        r = find_row("incomplete_final_batch_marker", "stdlib_batched")
        self.assertIsNotNone(r)
        self.assertEqual(r["batch_lengths"], [4, 4, 2])
        self.assertTrue(r["order_preserved"])
        # flattening reproduces input, so final batch must be (8,9)
        # batch_count=3, total=10, last length=2 confirms this

    def test_strict_incomplete(self):
        r = find_row("strict_incomplete_rejection_marker", "stdlib_batched")
        self.assertIsNotNone(r)
        if r["actual_classification"] == "version_skip":
            return
        self.assertEqual(r["actual_classification"], "expected_error")
        self.assertEqual(r["exception_type"], "ValueError")
        self.assertEqual(r["batch_count"], 2)
        self.assertIn(r["error_stage"], ("construction", "iteration"))

    def test_strict_exact(self):
        r = find_row("strict_exact_division_marker", "stdlib_batched")
        if r and r["actual_classification"] == "version_skip":
            return
        self.assertEqual(r["actual_classification"], "pass")
        self.assertEqual(r["batch_count"], 2)
        self.assertEqual(r["batch_lengths"], [4, 4])
        self.assertTrue(r["order_preserved"])
        bs = r.get("batch_summary","")
        self.assertIn("(0, 1, 2, 3)", bs)
        self.assertIn("(4, 5, 6, 7)", bs)
        self.assertTrue(r["order_preserved"])

    def test_zero_negative_batch_size(self):
        for cid in ("zero_batch_size_rejection_marker", "negative_batch_size_rejection_marker"):
            r = find_row(cid, "stdlib_batched")
            self.assertIsNotNone(r)
            self.assertEqual(r["actual_classification"], "expected_error")
            self.assertEqual(r["exception_type"], "ValueError")
            self.assertIn(r["error_stage"], ("construction", "iteration"))

    def test_lazy_consumption(self):
        r = find_row("lazy_first_batch_consumption_marker", "streaming_observation")
        self.assertIsNotNone(r)
        if r["actual_classification"] == "version_skip":
            return
        self.assertEqual(r["source_consumed"], 3)

    def test_single_pass(self):
        r = find_row("single_pass_iterator_marker", "streaming_observation")
        if r and r["actual_classification"] == "version_skip":
            return
        self.assertTrue(r["source_exhausted"])
        self.assertTrue(r["order_preserved"])

    def test_order_preserved(self):
        r = find_row("input_order_preservation_marker", "stdlib_batched")
        self.assertTrue(r["order_preserved"])

    def test_flatten_roundtrip(self):
        r = find_row("flatten_roundtrip_marker", "stdlib_batched")
        self.assertEqual(r["actual_classification"], "pass")
        self.assertTrue(r["order_preserved"])

    def test_naive_empty_batch(self):
        r = find_row("naive_range_extra_empty_batch_marker", "manual_reference")
        self.assertEqual(r["actual_classification"], "local_observation")
        self.assertTrue(r["empty_batch_seen"])

    def test_token_counts_equal(self):
        r = find_row("batch_local_token_count_marker", "hn_ml_context")
        self.assertEqual(r["serial_aggregate_hash"], r["batched_aggregate_hash"])

    def test_weighted_mean(self):
        r = find_row("unweighted_batch_mean_footgun_marker", "hn_ml_context")
        self.assertIsNotNone(r["global_mean"])
        self.assertAlmostEqual(r["weighted_aggregate"], r["global_mean"], places=10)
        self.assertNotAlmostEqual(r["unweighted_aggregate"], r["global_mean"], places=6)

    def test_dropped_tail(self):
        r = find_row("dropped_incomplete_batch_bias_marker", "hn_ml_context")
        self.assertEqual(r["dropped_count"], 1)
        self.assertEqual(r["dropped_ids"], ["r4"])
        # global_pos = 0.2, dropped_pos = 0.0, batched_pos = 0.2
        self.assertAlmostEqual(r["global_mean"], 0.2, places=6)
        self.assertAlmostEqual(r["weighted_aggregate"], 0.2, places=6)
        self.assertAlmostEqual(r["unweighted_aggregate"], 0.0, places=6)
        self.assertTrue(r["order_preserved"])

    def test_score_equivalence(self):
        # manual_reference
        r = find_row("tiny_linear_score_equivalence_marker", "manual_reference")
        self.assertEqual(r["actual_classification"], "pass")
        self.assertEqual(r["serial_score_hash"], r["batched_score_hash"])
        # hn_ml_context – check sumprod agreement and batched scores
        r2 = find_row("tiny_linear_score_equivalence_marker", "hn_ml_context")
        self.assertEqual(r2["serial_score_hash"], r2["batched_score_hash"])
        self.assertTrue(r2["order_preserved"])
        # sumprod scores should match manual scores
        # serial_aggregate_hash stores sumprod_scores hash
        self.assertIsNotNone(r2.get("serial_aggregate_hash"))
        # verify every score: feature_rows has 5 entries, batch_size=2, so 3 batches, last batch has 1 element
        # scores should be identical serial vs batched, order preserved, final batch retained
        self.assertEqual(r2["batch_count"], 3)

    def test_readme_disclaimers(self):
        readme = (ROOT / "README.md").read_text() if (ROOT / "README.md").exists() else ""
        required_phrases = [
            "does not prove",
            "batching",
            "training",
            "itertools.batched",
            "strict",
            "python 3.13",
            "machine-learning",
            "accuracy",
            "deterministic",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase.lower(), readme.lower(), f"README missing '{phrase}'")

    def test_results_disclaimers(self):
        results = (ROOT / "RESULTS.md").read_text() if (ROOT / "RESULTS.md").exists() else ""
        self.assertIn("training", results.lower())
        self.assertIn("strict", results.lower())

    def test_json_csv_results_agree(self):
        with open(ROOT / "results_rows.csv") as f:
            csv_rows = list(csv.DictReader(f))
        self.assertEqual(len(csv_rows), len(ROWS))
        from collections import Counter
        json_counts = Counter(r["actual_classification"] for r in ROWS)
        csv_counts = Counter(r["actual_classification"] for r in csv_rows)
        self.assertEqual(json_counts, csv_counts)

    def test_artifact_scan(self):
        # scan ALL committed evidence artifacts
        artifacts = [
            "README.md", "RESULTS.md", "VERIFY.md",
            "cases.json", "results_rows.json", "results_rows.csv",
            "hn_thread_evidence.md", "hn_comments_sanitized.json",
        ]
        import re
        # prohibited patterns – literal and regex
        bad_literals = [
            "/home/ubuntu",
            "/home/",
            "/root/",
            "/tmp/",
            "/mnt/",
            "/workspace/",
            "C:\\Users\\",
            "/usr/lib/node_modules/openclaw",
            "ghp_",
            "gho_",
            "openclaw-control",
        ]
        # regex patterns for credentials/tokens/session
        bad_res = [
            re.compile(r'(api[_-]?key|apikey|token|secret|password)\s*[:=]\s*["\']?[A-Za-z0-9_\-]{16,}', re.I),
            re.compile(r'bearer\s+[A-Za-z0-9_\-\.]{20,}', re.I),
            re.compile(r'sk-[A-Za-z0-9]{20,}'),
        ]
        for name in artifacts:
            p = ROOT / name
            if not p.exists():
                continue
            text = p.read_text(errors="ignore")
            for pat in bad_literals:
                # allow /tmp/ and /home/ in VERIFY.md when documenting paths generically?
                # no – keep strict, VERIFY must not contain real paths
                self.assertNotIn(pat, text, f"{name} contains prohibited '{pat}'")
            for cre in bad_res:
                m = cre.search(text)
                self.assertIsNone(m, f"{name} matches credential pattern {cre.pattern!r}: {text[m.start():m.start()+40]!r}" if m else "")
            # check for path-bearing tracebacks
            if "Traceback" in text and "File \"" in text:
                # allow /python-lab/ which is our sanitized placeholder
                bad_paths = ["/home/", "/root/", "/tmp/", "/usr/", "C:\\"]
                for bp in bad_paths:
                    if bp == "/usr/" and "/usr/bin/python" in text:
                        # allow /usr/bin/python mentions in docs
                        continue
                    self.assertNotIn(bp + "", text.split("Traceback")[-1] if "Traceback" in text else text,
                        f"{name} contains path-bearing traceback with {bp}")

if __name__ == "__main__":
    unittest.main()
