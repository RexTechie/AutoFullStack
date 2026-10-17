"""Verify the fixed Simple-only external comparison using independent synthetic data."""

from __future__ import annotations

import csv
import random
import unittest
from dataclasses import replace
from itertools import product
from pathlib import Path
from statistics import fmean, stdev
from tempfile import TemporaryDirectory

import numpy as np

from evaluation.scripts.experiment_data import APPROACHES, BENCHMARK_FILES, ProjectResult, load_project_results
from evaluation.scripts.experiment_external import (
    ExternalProjectResult,
    analyze_external_results,
    load_external_results,
)


METHODS = ("Incremental", "MetaGPT")
METRICS = ("E2E", "PFS", "MFS4")
ATTRIBUTES = {"E2E": "e2e_rate", "PFS": "project_functional_score", "MFS4": "mfs_at_4"}
FUNCTIONAL_HEADERS = ("ProjectID", "Category", "Approach", "Namespace", "ProjectName", "Module", "Score(0-5)", "Notes")
E2E_HEADERS = ("ProjectID", "Category", "Approach", "Namespace", "ProjectName", "Backend", "Frontend", "Notes")


def make_results(runs=(1, 2, 3), *, identical=False):
    """Create ten matched tasks with variable scores and valid recorded E2E states."""

    results = []
    for run in runs:
        for index in range(1, 11):
            for method_index, method in enumerate(METHODS):
                offset = 0 if identical else method_index
                score = float((index * (offset + 1) + run + offset) % 6)
                passed = score > 0 or index % 2 == 0
                results.append(ExternalProjectResult(
                    run=run,
                    project_id=f"proj_simple_{index:02d}",
                    approach=method,
                    project_name=f"{method} task {index:02d}",
                    score=score,
                    e2e_pass=passed,
                ))
    return results


def independent_oracle(results, *, bootstrap_samples, seed):
    """Calculate paired bootstrap intervals and exact label-swap p-values from raw scores."""

    # 1. Reduce only within each task, preserving every original threshold decision.
    ids = sorted({result.project_id for result in results})
    values = {}
    for method in METHODS:
        rows = []
        for project_id in ids:
            repeated = [result for result in results if result.approach == method and result.project_id == project_id]
            rows.append((fmean(float(result.e2e_pass) for result in repeated),
                         fmean(result.score for result in repeated),
                         fmean(float(result.score >= 4) for result in repeated)))
        values[method] = np.asarray(rows, dtype=float)

    # 2. Reuse each sampled task index across both methods and all three metrics.
    rng = np.random.default_rng(seed)
    indices = rng.choice(np.arange(len(ids)), size=(bootstrap_samples, len(ids)), replace=True)
    draws = {method: values[method][indices].mean(axis=1) for method in METHODS}
    intervals = {(method, metric): np.quantile(draws[method][:, index], [0.025, 0.975])
                 for method in METHODS for index, metric in enumerate(METRICS)}
    difference_intervals = {
        metric: np.quantile(draws["Incremental"][:, index] - draws["MetaGPT"][:, index], [0.025, 0.975])
        for index, metric in enumerate(METRICS)
    }

    # 3. Exchange complete task outcomes directly, rather than using production sign contributions.
    labels = np.asarray(list(product((False, True), repeat=len(ids))))
    left = np.where(labels[:, :, None], values["Incremental"][None], values["MetaGPT"][None])
    right = np.where(labels[:, :, None], values["MetaGPT"][None], values["Incremental"][None])
    null = left.mean(axis=1) - right.mean(axis=1)
    observed = values["Incremental"].mean(axis=0) - values["MetaGPT"].mean(axis=0)
    p_values = {}
    for index, metric in enumerate(METRICS):
        tolerance = max(1e-12, abs(observed[index]) * 100 * np.finfo(float).eps)
        extreme = np.count_nonzero(np.abs(null[:, index]) >= abs(observed[index]) - tolerance)
        p_values[metric] = extreme / len(labels)
    adjusted = {}
    running = 0.0
    for rank, metric in enumerate(sorted(METRICS, key=p_values.get)):
        running = max(running, min(1.0, (3 - rank) * p_values[metric]))
        adjusted[metric] = running
    return intervals, difference_intervals, p_values, adjusted


class ExternalStatisticsTests(unittest.TestCase):
    """Check the public external-analysis API without calling artifact generation."""

    def compute(self, results, *, samples=500, seed=37):
        """Run small deterministic bootstrap samples while retaining exact permutation tests."""

        return analyze_external_results(results, bootstrap_samples=samples, seed=seed)

    def test_summaries_counts_and_sample_run_sd(self):
        """Recompute quality means, observed counts, and sample run SD independently."""

        results = make_results()
        analysis = self.compute(results)
        self.assertEqual(len(analysis.results), 60)
        self.assertEqual(set(analysis.summary), set(METHODS))
        self.assertEqual(len(analysis.estimates), 6)
        self.assertEqual(len(analysis.comparisons), 3)
        self.assertEqual([label for label, _ in analysis.run_summaries], ["Run 1", "Run 2", "Run 3"])
        for method in METHODS:
            selected = [result for result in results if result.approach == method]
            summary = analysis.summary[method]
            expected = {"E2E": fmean(result.e2e_pass for result in selected),
                        "PFS": fmean(result.score for result in selected),
                        "MFS4": sum(result.score >= 4 for result in selected) / len(selected)}
            self.assertEqual((summary.projects, summary.project_runs), (10, 30))
            self.assertEqual(summary.passed_runs, sum(result.e2e_pass for result in selected))
            self.assertEqual(summary.modules_at_4, sum(result.score >= 4 for result in selected))
            self.assertFalse(hasattr(summary, "avg_tokens"))
            for metric in METRICS:
                attribute = ATTRIBUTES[metric]
                run_values = [getattr(summaries[method], attribute) for _, summaries in analysis.run_summaries]
                self.assertAlmostEqual(getattr(summary, attribute), expected[metric])
                estimate = analysis.estimates[(method, metric)]
                self.assertAlmostEqual(estimate.estimate, expected[metric])
                self.assertAlmostEqual(estimate.run_mean, fmean(run_values))
                self.assertAlmostEqual(estimate.run_sd, stdev(run_values))
            self.assertFalse(hasattr(selected[0], "total_tokens"))

    def test_bootstrap_and_exact_tests_match_independent_oracle(self):
        """Verify all six intervals, three paired intervals, exact p-values, and Holm corrections."""

        results = make_results()
        intervals, differences, p_values, adjusted = independent_oracle(results, bootstrap_samples=600, seed=41)
        analysis = self.compute(results, samples=600, seed=41)
        for key, estimate in analysis.estimates.items():
            np.testing.assert_allclose([estimate.ci_low, estimate.ci_high], intervals[key], atol=1e-12, rtol=0)
        for comparison in analysis.comparisons:
            np.testing.assert_allclose([comparison.ci_low, comparison.ci_high], differences[comparison.metric], atol=1e-12, rtol=0)
            self.assertEqual(comparison.p_value, p_values[comparison.metric])
            self.assertEqual(comparison.p_holm, adjusted[comparison.metric])
            self.assertEqual((comparison.projects, comparison.runs_per_project, comparison.project_runs), (10, 3, 30))
            self.assertEqual(comparison.higher + comparison.equal + comparison.lower, 10)

    def test_raw_score_threshold_and_task_cluster_bootstrap(self):
        """Threshold original runs, not mean scores, and never resample individual repetitions."""

        results = []
        for result in make_results():
            score = (5.0, 5.0, 2.0)[result.run - 1] if result.approach == "Incremental" else 4.0
            results.append(replace(result, score=score, e2e_pass=True))
        analysis = self.compute(results)
        summary = analysis.summary["Incremental"]
        self.assertEqual(summary.project_functional_score, 4.0)
        self.assertAlmostEqual(summary.mfs_at_4, 2 / 3)
        self.assertEqual(summary.modules_at_4, 20)
        estimate = analysis.estimates[("Incremental", "MFS4")]
        self.assertAlmostEqual(estimate.run_sd, stdev([1.0, 1.0, 0.0]))
        self.assertAlmostEqual(estimate.ci_low, 2 / 3)
        self.assertAlmostEqual(estimate.ci_high, 2 / 3)
        self.assertTrue(estimate.ci_degenerate)

    def test_constant_paired_difference_preserves_shared_task_samples(self):
        """Keep a paired interval fixed despite variable individual-method intervals."""

        results = []
        for result in make_results():
            index = int(result.project_id.rsplit("_", 1)[1])
            score = 3.0 + index % 2 + (result.run % 2)
            if result.approach == "MetaGPT":
                score -= 1
            results.append(replace(result, score=score, e2e_pass=True))
        analysis = self.compute(results)
        estimate = analysis.estimates[("Incremental", "PFS")]
        self.assertGreater(estimate.ci_high, estimate.ci_low)
        comparison = next(value for value in analysis.comparisons if value.metric == "PFS")
        self.assertAlmostEqual(comparison.difference, 1.0)
        self.assertAlmostEqual(comparison.ci_low, 1.0)
        self.assertAlmostEqual(comparison.ci_high, 1.0)
        self.assertTrue(comparison.ci_degenerate)
        self.assertEqual((comparison.higher, comparison.equal, comparison.lower), (10, 0, 0))

    def test_exact_floor_has_no_monte_carlo_plus_one_correction(self):
        """Return the exhaustive two-sided floor 2/1024 and one three-test Holm family."""

        results = [replace(result, score=5.0 if result.approach == "Incremental" else 0.0,
                           e2e_pass=result.approach == "Incremental") for result in make_results()]
        analysis = self.compute(results)
        for comparison in analysis.comparisons:
            self.assertEqual(comparison.p_value, 2 / 1024)
            self.assertEqual(comparison.p_holm, 6 / 1024)
            self.assertNotEqual(comparison.p_value, 3 / 1025)
            self.assertEqual((comparison.higher, comparison.equal, comparison.lower), (10, 0, 0))
        for estimate in analysis.estimates.values():
            self.assertTrue(estimate.ci_degenerate)

    def test_zero_scores_remain_observations_and_identical_methods_have_p_one(self):
        """Retain every zero score and report no evidence of a difference under identical outcomes."""

        results = [replace(result, score=0.0, e2e_pass=False) for result in make_results(identical=True)]
        analysis = self.compute(results)
        for summary in analysis.summary.values():
            self.assertEqual((summary.projects, summary.project_runs, summary.modules_at_4), (10, 30, 0))
            self.assertEqual((summary.e2e_rate, summary.project_functional_score, summary.mfs_at_4), (0.0, 0.0, 0.0))
        for comparison in analysis.comparisons:
            self.assertEqual((comparison.difference, comparison.ci_low, comparison.ci_high), (0.0, 0.0, 0.0))
            self.assertTrue(comparison.ci_degenerate)
            self.assertEqual((comparison.p_value, comparison.p_holm), (1.0, 1.0))
            self.assertEqual((comparison.higher, comparison.equal, comparison.lower), (0, 10, 0))

    def test_reproducible_seed_input_order_and_seed_independent_exact_p(self):
        """Keep deterministic outputs order-invariant and exact p-values independent of the analysis seed."""

        results = make_results()
        expected = self.compute(results)
        shuffled = list(results)
        random.Random(13).shuffle(shuffled)
        original_order = list(shuffled)
        self.assertEqual(self.compute(shuffled), expected)
        self.assertEqual(shuffled, original_order)
        changed_seed = self.compute(results, seed=99)
        self.assertEqual([value.p_value for value in changed_seed.comparisons],
                         [value.p_value for value in expected.comparisons])
        self.assertEqual([value.p_holm for value in changed_seed.comparisons],
                         [value.p_holm for value in expected.comparisons])

    def test_single_run_is_descriptive_only(self):
        """Avoid fabricated run SDs or inferential results when selecting only one run."""

        analysis = self.compute(make_results(runs=(3,)))
        self.assertEqual(analysis.estimates, {})
        self.assertEqual(analysis.comparisons, [])
        self.assertEqual([label for label, _ in analysis.run_summaries], ["Run 3"])
        for summary in analysis.summary.values():
            self.assertEqual((summary.projects, summary.project_runs), (10, 10))

    def test_two_selected_runs_keep_actual_labels_counts_and_sample_sd(self):
        """Support Run 1 plus Run 3 without inventing an unobserved Run 2."""

        analysis = self.compute(make_results(runs=(3, 1)))
        self.assertEqual([label for label, _ in analysis.run_summaries], ["Run 1", "Run 3"])
        for method in METHODS:
            self.assertEqual(analysis.summary[method].project_runs, 20)
            run_values = [summaries[method].project_functional_score for _, summaries in analysis.run_summaries]
            self.assertAlmostEqual(analysis.estimates[(method, "PFS")].run_sd, stdev(run_values))
        for comparison in analysis.comparisons:
            self.assertEqual((comparison.projects, comparison.runs_per_project, comparison.project_runs), (10, 2, 20))

    def test_rejects_incomplete_duplicate_wrong_size_and_unmatched_panels(self):
        """Reject pseudopaired or incomplete task panels rather than silently dropping records."""

        results = make_results()
        invalid_panels = (
            [],
            results[:-1],
            results + [results[0]],
            [result for result in results if not result.project_id.endswith("10")],
            [replace(result, project_id="unmatched") if result.approach == "MetaGPT" and result.project_id.endswith("10") else result for result in results],
        )
        for invalid in invalid_panels:
            with self.subTest(records=len(invalid)), self.assertRaises(ValueError):
                self.compute(invalid, samples=20)

    def test_rejects_bad_identity_score_state_and_changing_task_name(self):
        """Validate method identities, selected run IDs, scores, E2E states, and stable per-method names."""

        results = make_results()
        mutations = ({"approach": "Unknown"}, {"run": 4}, {"score": 4.5}, {"score": float("nan")},
                     {"e2e_pass": 1}, {"score": 4.0, "e2e_pass": False}, {"project_name": "Changed name"})
        for mutation in mutations:
            invalid = [replace(results[0], **mutation), *results[1:]]
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.compute(invalid, samples=20)

    def test_rejects_invalid_bootstrap_budgets(self):
        """Require a positive integer bootstrap sample count."""

        for samples in (0, -1, True, 1.5):
            with self.subTest(samples=samples), self.assertRaises(ValueError):
                self.compute(make_results(), samples=samples)


def make_internal_results(external):
    """Build complete legacy method panels with real cost fields for loader isolation tests."""

    references = {(result.run, result.project_id): result for result in external if result.approach == "Incremental"}
    results = []
    for run in sorted({result.run for result in external}):
        for approach in APPROACHES:
            for category in ("Simple", "Medium", "Complex"):
                for index in range(1, 11):
                    project_id = f"proj_{category.lower()}_{index:02d}"
                    reference = references.get((run, project_id))
                    modules = {"Simple": 1, "Medium": 3, "Complex": 6}[category]
                    results.append(ProjectResult(
                        run=run, project_id=project_id, category=category, approach=approach,
                        project_name=reference.project_name if reference else f"{category} task {index:02d}",
                        scores=(reference.score,) if reference else (3.0,) * modules,
                        e2e_pass=reference.e2e_pass if reference else True,
                        total_tokens=float(1000 + 100 * run + index),
                    ))
    return results


def make_input_rows(internal, external):
    """Construct separate functional and recorded E2E CSV rows without external token measurements."""

    functional, e2e = {}, {}
    for run in sorted({result.run for result in internal}):
        functional[run], e2e[run] = [], []
    for result in internal:
        common = {"ProjectID": result.project_id, "Category": result.category,
                  "Approach": result.approach, "ProjectName": result.project_name}
        for index, score in enumerate(result.scores):
            functional[result.run].append({**common, "Module": f"Module{index + 1}", "Score(0-5)": str(score)})
        e2e[result.run].append({**common, "Backend": "Pass" if result.e2e_pass else "Failure", "Frontend": "Pass"})
    for result in external:
        if result.approach != "MetaGPT":
            continue
        common = {"ProjectID": result.project_id, "Category": "Simple", "Approach": "MetaGPT", "ProjectName": result.project_name}
        functional[result.run].append({**common, "Module": "Feature", "Score(0-5)": str(result.score)})
        e2e[result.run].append({**common, "Backend": "Pass" if result.e2e_pass else "Failure", "Frontend": "Pass"})
    return functional, e2e


def write_csv(path, headers, rows):
    """Write only disposable test CSVs inside a TemporaryDirectory."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


class ExternalLoaderTests(unittest.TestCase):
    """Verify explicit method partitioning and quality-only external input validation."""

    def setUp(self):
        """Create complete disposable source fixtures without benchmark CSVs by default."""

        temporary = TemporaryDirectory(prefix="external-comparison-test-")
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.external = make_results()
        self.internal = make_internal_results(self.external)
        self.functional, self.e2e = make_input_rows(self.internal, self.external)
        self.save_inputs()

    def save_inputs(self):
        """Save the current fixture row lists into their temporary run directories."""

        for run in (1, 2, 3):
            write_csv(self.folder / f"run_{run}" / "eval_functional_correctness.csv", FUNCTIONAL_HEADERS, self.functional[run])
            write_csv(self.folder / f"run_{run}" / "eval_e2e_executability.csv", E2E_HEADERS, self.e2e[run])

    def load(self, runs=(1, 2, 3)):
        """Load only fixture data through the public external loader."""

        return load_external_results(runs, self.folder, self.internal)

    def test_loads_without_any_external_or_internal_benchmark_files(self):
        """Require no token file when matching external quality outcomes to supplied legacy results."""

        self.assertEqual(self.load(), sorted(self.external, key=lambda result: (result.run, result.approach, result.project_id)))
        self.assertEqual(list(self.folder.rglob("benchmark*.csv")), [])
        self.assertEqual(len(self.load(runs=(3,))), 20)

    def test_absent_metagpt_returns_empty_results(self):
        """Treat an entirely absent external experiment as optional rather than synthesizing failures."""

        for run in (1, 2, 3):
            self.functional[run] = [row for row in self.functional[run] if row["Approach"] != "MetaGPT"]
            self.e2e[run] = [row for row in self.e2e[run] if row["Approach"] != "MetaGPT"]
        self.save_inputs()
        self.assertEqual(self.load(), [])

    def test_partial_run_or_source_never_silently_drops_tasks(self):
        """Reject a missing MetaGPT run or missing functional/E2E counterpart."""

        for target in ("functional", "e2e", "both"):
            self.functional, self.e2e = make_input_rows(self.internal, self.external)
            if target in ("functional", "both"):
                self.functional[2] = [row for row in self.functional[2] if row["Approach"] != "MetaGPT"]
            if target in ("e2e", "both"):
                self.e2e[2] = [row for row in self.e2e[2] if row["Approach"] != "MetaGPT"]
            self.save_inputs()
            with self.subTest(source=target), self.assertRaises(ValueError):
                self.load()

    def test_rejects_duplicate_or_non_simple_external_rows(self):
        """Require one functional module and one E2E row per Simple task."""

        for source in ("functional", "e2e"):
            for mutation in ("duplicate", "category"):
                self.functional, self.e2e = make_input_rows(self.internal, self.external)
                rows = self.functional[1] if source == "functional" else self.e2e[1]
                row = next(row for row in rows if row["Approach"] == "MetaGPT")
                if mutation == "duplicate":
                    rows.append(dict(row))
                else:
                    row["Category"] = "Medium"
                self.save_inputs()
                with self.subTest(source=source, mutation=mutation), self.assertRaises(ValueError):
                    self.load()

    def test_rejects_invalid_score_blank_status_and_failed_positive_score(self):
        """Never infer missing statuses or accept inconsistent score/E2E combinations."""

        cases = ("fraction", "blank_backend", "blank_frontend", "lowercase", "failed_positive")
        for case in cases:
            self.functional, self.e2e = make_input_rows(self.internal, self.external)
            score = next(row for row in self.functional[1] if row["Approach"] == "MetaGPT")
            state = next(row for row in self.e2e[1] if row["Approach"] == "MetaGPT")
            if case == "fraction":
                score["Score(0-5)"] = "4.5"
            elif case == "blank_backend":
                state["Backend"] = ""
            elif case == "blank_frontend":
                state["Frontend"] = ""
            elif case == "lowercase":
                state["Backend"] = "pass"
            else:
                score["Score(0-5)"] = "4"
                state["Backend"] = "Failure"
            self.save_inputs()
            with self.subTest(case=case), self.assertRaises(ValueError):
                self.load()

    def test_rejects_foreign_task_ids_even_with_ten_rows_in_both_sources(self):
        """Check task identity, not merely matching source row counts."""

        for rows in (self.functional[1], self.e2e[1]):
            row = next(row for row in rows if row["Approach"] == "MetaGPT")
            row["ProjectID"] = "foreign_simple_task"
        self.save_inputs()
        with self.assertRaises(ValueError):
            self.load()

    def test_rejects_unknown_method_even_when_metagpt_is_absent(self):
        """Do not let optional external loading silently swallow unrecognized method labels."""

        for run in (1, 2, 3):
            self.functional[run] = [row for row in self.functional[run] if row["Approach"] != "MetaGPT"]
            self.e2e[run] = [row for row in self.e2e[run] if row["Approach"] != "MetaGPT"]
        unknown = dict(self.functional[1][0])
        unknown["Approach"] = "MetGPT"
        self.functional[1].append(unknown)
        self.save_inputs()
        with self.assertRaises(ValueError):
            self.load()

    def test_legacy_loader_partitions_metagpt_before_score_and_status_validation(self):
        """Keep the original three-method path usable while external values await confirmation."""

        for run in (1, 2, 3):
            for row in self.functional[run]:
                if row["Approach"] == "MetaGPT":
                    row["Score(0-5)"] = "pending"
            for row in self.e2e[run]:
                if row["Approach"] == "MetaGPT":
                    row["Backend"] = ""
                    row["Frontend"] = ""
        self.save_inputs()
        for method, filename in BENCHMARK_FILES[1].items():
            rows = [{"Approach": result.approach, "ProjectID": result.project_id,
                     "Category": result.category, "TotalTokens": result.total_tokens}
                    for result in self.internal if result.run == 1 and result.approach == method]
            write_csv(self.folder / "run_1" / filename, ("Approach", "ProjectID", "Category", "TotalTokens"), rows)
        loaded = load_project_results(1, self.folder)
        self.assertEqual(len(loaded), 90)
        self.assertEqual({result.approach for result in loaded}, set(APPROACHES))
        self.assertEqual(APPROACHES, ("Incremental", "Waterfall", "Incremental-NoSelfRefinement"))

    def test_legacy_loader_rejects_unknown_methods_in_both_sources(self):
        """Reject misspelled methods before any benchmark join instead of silently skipping them."""

        for source in ("functional", "e2e"):
            self.functional, self.e2e = make_input_rows(self.internal, self.external)
            rows = self.functional[1] if source == "functional" else self.e2e[1]
            rows[0]["Approach"] = "MetGPT"
            self.save_inputs()
            with self.subTest(source=source), self.assertRaisesRegex(ValueError, "unknown method"):
                load_project_results(1, self.folder)


class ExternalExportTests(unittest.TestCase):
    """Check paper exports for truthful statistical metadata and selected-run scope."""

    def test_exports_actual_analysis_parameters_and_separate_exact_test_family(self):
        """Export the seed and sample count actually used, with exact unrounded p-values."""

        from evaluation.scripts.experiment_rendering import export_external_results

        analysis = analyze_external_results(make_results(), bootstrap_samples=123, seed=29)
        with TemporaryDirectory(prefix="external-export-test-") as directory:
            folder = Path(directory)
            export_external_results(folder, analysis, tables_only=True)
            with (folder / "combined" / "data" / "external_simple_paired_comparisons.csv").open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 3)
            for row, comparison in zip(rows, analysis.comparisons):
                self.assertEqual((row["BootstrapSamples"], row["AnalysisSeed"]), ("123", "29"))
                self.assertEqual((row["ExactPermutations"], row["FamilySize"]), ("1024", "3"))
                self.assertEqual((row["Family"], row["Category"]), ("external_simple_quality", "Simple"))
                self.assertEqual(float(row["PValue"]), comparison.p_value)
                self.assertNotIn("Tokens", row)
            notes = (folder / "combined" / "tables" / "external_simple_paired_comparisons_table.tex").read_text(encoding="utf-8")
            self.assertIn("123 paired", notes)
            self.assertIn("seed 29", notes)
            self.assertNotIn("2^", notes)
            self.assertTrue((folder / "combined" / "data" / "external_simple_metric_estimates.csv").is_file())
            self.assertTrue((folder / "run_comparison" / "data" / "external_simple_project_runs.csv").is_file())
            self.assertTrue((folder / "run_comparison" / "data" / "external_simple_summary_values.csv").is_file())
            self.assertTrue((folder / "run_comparison" / "tables" / "external_simple_run_comparison_table.tex").is_file())
            self.assertTrue((folder / "combined" / "preview" / "external_simple_table.csv").is_file())
            self.assertFalse((folder / "statistics").exists())
            self.assertFalse(list(folder.rglob("*.png")))
            self.assertFalse(list(folder.rglob("*.pdf")))

    def test_single_run_exports_no_combined_or_inferential_outputs(self):
        """Keep single-run output descriptive and free of fabricated uncertainty or comparisons."""

        from evaluation.scripts.experiment_rendering import export_external_results

        analysis = analyze_external_results(make_results(runs=(3,)))
        with TemporaryDirectory(prefix="external-export-test-") as directory:
            folder = Path(directory)
            export_external_results(folder, analysis, tables_only=True)
            self.assertTrue((folder / "runs" / "run_3" / "tables" / "external_simple_table.tex").is_file())
            self.assertFalse((folder / "runs" / "run_1").exists())
            self.assertFalse((folder / "combined").exists())
            self.assertFalse((folder / "statistics").exists())
            self.assertFalse(list(folder.rglob("external_simple_metric_estimates.csv")))
            self.assertFalse(list(folder.rglob("external_simple_paired_comparisons.csv")))
            with (folder / "run_comparison" / "data" / "external_simple_summary_values.csv").open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 2)
            self.assertTrue(all(row["Run"] == "Run 3" and row["ProjectRuns"] == "10" for row in rows))


if __name__ == "__main__":
    unittest.main()
