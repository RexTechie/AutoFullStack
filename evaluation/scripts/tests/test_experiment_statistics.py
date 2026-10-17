"""Independently verify the repeated-run paper statistics on small paired data."""

from __future__ import annotations

import random
import unittest
from dataclasses import replace
from statistics import fmean, stdev

import numpy as np

from evaluation.scripts.experiment_data import (
    APPROACHES,
    CATEGORIES,
    METRIC_ATTRIBUTES,
    STATISTICAL_METRICS,
    ProjectResult,
)
from evaluation.scripts.experiment_statistics import (
    aggregate_projects,
    compute_repeated_statistics,
    compute_summary,
)


def make_results(runs: int = 3, *, identical: bool = False) -> list[ProjectResult]:
    """Build matched tasks with unequal module counts and varying run outcomes."""

    results = []
    module_counts = {"Simple": (1, 1), "Medium": (3, 4), "Complex": (6, 6)}
    for category_index, category in enumerate(CATEGORIES):
        for task_index, modules in enumerate(module_counts[category]):
            project_id = f"{category[0]}{task_index + 1}"
            for approach_index, approach in enumerate(APPROACHES):
                method_index = 0 if identical else approach_index
                for run in range(1, runs + 1):
                    failed = not identical and task_index == 1 and method_index == run
                    scores = tuple(
                        0.0 if failed else float((run + category_index + task_index + method_index + module) % 6)
                        for module in range(modules)
                    )
                    results.append(ProjectResult(
                        run=run,
                        project_id=project_id,
                        category=category,
                        approach=approach,
                        project_name=project_id,
                        scores=scores,
                        e2e_pass=not failed,
                        total_tokens=float(500 + 70 * category_index + 40 * task_index + 30 * method_index + 20 * run),
                    ))
    return results


def prepare_statistics(results: list[ProjectResult]):
    """Prepare the public statistics inputs without changing their source grain."""

    projects = aggregate_projects(results)
    run_summaries = [
        (f"Run {run}", compute_summary(aggregate_projects([result for result in results if result.run == run])))
        for run in sorted({result.run for result in results})
    ]
    return projects, run_summaries


def independent_bootstrap(results: list[ProjectResult], *, samples: int, seed: int):
    """Recompute task-cluster percentile intervals directly from raw run records."""

    # 1. Build task-level values independently of the production aggregators.
    project_ids = sorted({result.project_id for result in results})
    category_by_id = {result.project_id: result.category for result in results}
    values = {}
    for approach in APPROACHES:
        method_values = []
        for project_id in project_ids:
            repeated = [result for result in results if result.approach == approach and result.project_id == project_id]
            method_values.append((
                fmean(float(result.e2e_pass) for result in repeated),
                fmean(fmean(result.scores) for result in repeated),
                sum(score >= 4 for result in repeated for score in result.scores),
                sum(len(result.scores) for result in repeated),
                fmean(result.total_tokens for result in repeated),
            ))
        values[approach] = np.asarray(method_values, dtype=float)

    # 2. Reuse each sampled task index for every method and all retained runs.
    rng = np.random.default_rng(seed)
    strata = [np.asarray([index for index, project_id in enumerate(project_ids) if category_by_id[project_id] == category])
              for category in CATEGORIES]
    sampled_strata = [rng.choice(indices, size=(samples, len(indices)), replace=True) for indices in strata]
    sampled_ids = np.concatenate(sampled_strata, axis=1)
    intervals = {}
    bootstrap = {}
    for approach in APPROACHES:
        for category, indices in zip(CATEGORIES, sampled_strata):
            sampled = values[approach][indices]
            metric_samples = {
                "E2E": sampled[:, :, 0].mean(axis=1),
                "PFS": sampled[:, :, 1].mean(axis=1),
                "MFS4": sampled[:, :, 2].sum(axis=1) / sampled[:, :, 3].sum(axis=1),
                "Tokens": sampled[:, :, 4].mean(axis=1),
            }
            for metric, draws in metric_samples.items():
                intervals[(approach, category, metric)] = np.quantile(draws, [0.025, 0.975])
        sampled = values[approach][sampled_ids]
        bootstrap[approach] = {
            "E2E": sampled[:, :, 0].mean(axis=1),
            "PFS": sampled[:, :, 1].mean(axis=1),
            "MFS4": sampled[:, :, 2].sum(axis=1) / sampled[:, :, 3].sum(axis=1),
            "Tokens": sampled[:, :, 4].mean(axis=1),
        }
        for metric, draws in bootstrap[approach].items():
            intervals[(approach, "Overall", metric)] = np.quantile(draws, [0.025, 0.975])
    differences = {
        (comparator, metric): np.quantile(bootstrap["Incremental"][metric] - bootstrap[comparator][metric], [0.025, 0.975])
        for comparator in APPROACHES[1:]
        for metric in STATISTICAL_METRICS
    }
    return intervals, differences


def independent_label_swap_p_values(results: list[ProjectResult], *, bootstrap_samples: int, permutations: int, seed: int):
    """Swap complete paired task outcomes and calculate two-sided Monte Carlo tails."""

    # 1. Retain each task's full repeated-run average and pooled module counts.
    project_ids = sorted({result.project_id for result in results})
    categories = {result.project_id: result.category for result in results}
    values = {}
    for approach in APPROACHES:
        rows = []
        for project_id in project_ids:
            repeated = [result for result in results if result.approach == approach and result.project_id == project_id]
            rows.append((
                fmean(float(result.e2e_pass) for result in repeated),
                fmean(fmean(result.scores) for result in repeated),
                sum(score >= 4 for result in repeated for score in result.scores),
                sum(len(result.scores) for result in repeated),
                fmean(result.total_tokens for result in repeated),
            ))
        values[approach] = np.asarray(rows, dtype=float)

    # 2. Follow the documented random stream, then swap each whole task pair.
    rng = np.random.default_rng(seed)
    for category in CATEGORIES:
        indices = np.asarray([index for index, project_id in enumerate(project_ids) if categories[project_id] == category])
        rng.choice(indices, size=(bootstrap_samples, len(indices)), replace=True)
    labels = rng.integers(0, 2, size=(permutations, len(project_ids)), dtype=np.int8).astype(bool)
    p_values = {}
    left = values["Incremental"]
    for comparator in APPROACHES[1:]:
        right = values[comparator]
        swapped_left = np.where(labels[:, :, None], left[None], right[None])
        swapped_right = np.where(labels[:, :, None], right[None], left[None])
        observed = {
            "E2E": left[:, 0].mean() - right[:, 0].mean(),
            "PFS": left[:, 1].mean() - right[:, 1].mean(),
            "MFS4": left[:, 2].sum() / left[:, 3].sum() - right[:, 2].sum() / right[:, 3].sum(),
            "Tokens": left[:, 4].mean() - right[:, 4].mean(),
        }
        null = {
            "E2E": swapped_left[:, :, 0].mean(axis=1) - swapped_right[:, :, 0].mean(axis=1),
            "PFS": swapped_left[:, :, 1].mean(axis=1) - swapped_right[:, :, 1].mean(axis=1),
            "MFS4": swapped_left[:, :, 2].sum(axis=1) / swapped_left[:, :, 3].sum(axis=1)
            - swapped_right[:, :, 2].sum(axis=1) / swapped_right[:, :, 3].sum(axis=1),
            "Tokens": swapped_left[:, :, 4].mean(axis=1) - swapped_right[:, :, 4].mean(axis=1),
        }
        for metric in STATISTICAL_METRICS:
            tolerance = max(1e-12, abs(observed[metric]) * 100 * np.finfo(float).eps)
            extreme = np.count_nonzero(np.abs(null[metric]) >= abs(observed[metric]) - tolerance)
            p_values[(comparator, metric)] = (extreme + 1) / (permutations + 1)
    return p_values


class RepeatedStatisticsTests(unittest.TestCase):
    """Exercise weighting, repeated-run variation, pairing, and test correction."""

    def compute(self, results, *, bootstrap_samples: int = 400, permutation_samples: int = 999, seed: int = 17):
        """Run the public statistics API with small reproducible resample budgets."""

        projects, summaries = prepare_statistics(results)
        return compute_repeated_statistics(
            projects,
            summaries,
            bootstrap_samples=bootstrap_samples,
            permutation_samples=permutation_samples,
            seed=seed,
        )

    def test_point_estimates_and_sample_run_sd(self):
        """Keep combined point estimates distinct from the sample SD of run means."""

        results = make_results()
        projects, summaries = prepare_statistics(results)
        combined = compute_summary(projects)
        estimates, comparisons = self.compute(results)
        self.assertEqual(len(estimates), 3 * 4 * 4)
        self.assertEqual(len(comparisons), 8)
        for key, estimate in estimates.items():
            approach, scope, metric = key
            attribute = METRIC_ATTRIBUTES[metric]
            repeated = [getattr(summary[(approach, scope)], attribute) for _, summary in summaries]
            self.assertAlmostEqual(estimate.estimate, getattr(combined[(approach, scope)], attribute))
            self.assertAlmostEqual(estimate.run_mean, fmean(repeated))
            self.assertAlmostEqual(estimate.run_sd, stdev(repeated))

    def test_module_weighted_mfs_is_not_equal_task_mean(self):
        """Pool module counts without replacing MFS@4 by the mean project ratio."""

        results = [replace(result, scores=(5.0,) * len(result.scores) if result.project_id == "M1" else (0.0,) * len(result.scores))
                   for result in make_results(identical=True)]
        estimates, _ = self.compute(results)
        for approach in APPROACHES:
            self.assertAlmostEqual(estimates[(approach, "Medium", "MFS4")].estimate, 3 / 7)
            self.assertNotAlmostEqual(estimates[(approach, "Medium", "MFS4")].estimate, 0.5)

    def test_pooled_mfs_and_mean_run_mfs_remain_distinct(self):
        """Keep the pooled estimate when module denominators vary across runs."""

        results = []
        for result in make_results(identical=True):
            if result.category == "Medium":
                modules = {"M1": (3, 4, 4), "M2": (3, 3, 4)}[result.project_id][result.run - 1]
                score = 5.0 if result.project_id == "M1" and result.run == 1 else 0.0
                result = replace(result, scores=(score,) * modules)
            results.append(result)
        estimates, _ = self.compute(results)
        for approach in APPROACHES:
            estimate = estimates[(approach, "Medium", "MFS4")]
            self.assertAlmostEqual(estimate.estimate, 3 / 21)
            self.assertAlmostEqual(estimate.run_mean, fmean([3 / 6, 0.0, 0.0]))
            self.assertAlmostEqual(estimate.run_sd, stdev([3 / 6, 0.0, 0.0]))
            self.assertNotAlmostEqual(estimate.estimate, estimate.run_mean)

    def test_bootstrap_matches_independent_raw_record_oracle(self):
        """Retain all repeats and use paired stratified task-cluster resampling."""

        results = make_results()
        intervals, differences = independent_bootstrap(results, samples=500, seed=41)
        estimates, comparisons = self.compute(results, bootstrap_samples=500, seed=41)
        for key, estimate in estimates.items():
            np.testing.assert_allclose([estimate.ci_low, estimate.ci_high], intervals[key], atol=1e-12, rtol=0)
        for comparison in comparisons:
            np.testing.assert_allclose(
                [comparison.ci_low, comparison.ci_high], differences[(comparison.comparator, comparison.metric)], atol=1e-12, rtol=0,
            )

    def test_permutation_matches_independent_whole_task_label_swaps(self):
        """Compare production p-values against direct task-pair label exchanges."""

        results = make_results()
        expected = independent_label_swap_p_values(results, bootstrap_samples=200, permutations=499, seed=31)
        _, comparisons = self.compute(results, bootstrap_samples=200, permutation_samples=499, seed=31)
        for comparison in comparisons:
            self.assertEqual(comparison.p_value, expected[(comparison.comparator, comparison.metric)])

    def test_bootstrap_preserves_pairing_for_constant_project_differences(self):
        """Produce a zero-width paired interval even when individual methods vary."""

        results = []
        for result in make_results():
            task_base = 2 if result.project_id.endswith("1") else 4
            method_offset = APPROACHES.index(result.approach)
            run_offset = (0, 1, -1)[result.run - 1]
            results.append(replace(result, scores=(float(task_base - method_offset + run_offset),) * len(result.scores), e2e_pass=True))
        estimates, comparisons = self.compute(results)
        self.assertGreater(estimates[("Incremental", "Overall", "PFS")].ci_high,
                           estimates[("Incremental", "Overall", "PFS")].ci_low)
        comparison = next(item for item in comparisons if item.comparator == "Waterfall" and item.metric == "PFS")
        self.assertAlmostEqual(comparison.difference, 1.0)
        self.assertAlmostEqual(comparison.ci_low, 1.0)
        self.assertAlmostEqual(comparison.ci_high, 1.0)
        self.assertTrue(comparison.ci_degenerate)
        self.assertEqual((comparison.higher, comparison.equal, comparison.lower), (6, 0, 0))

    def test_task_cluster_bootstrap_does_not_resample_individual_runs(self):
        """Leave intervals degenerate when identical tasks have varying raw runs."""

        results = []
        for result in make_results(identical=True):
            passed = result.run != 2
            results.append(replace(result, scores=((5.0 if passed else 0.0),) * len(result.scores), e2e_pass=passed))
        estimates, _ = self.compute(results)
        estimate = estimates[("Incremental", "Overall", "E2E")]
        self.assertAlmostEqual(estimate.estimate, 2 / 3)
        self.assertAlmostEqual(estimate.run_sd, stdev([1.0, 0.0, 1.0]))
        self.assertAlmostEqual(estimate.ci_low, 2 / 3)
        self.assertAlmostEqual(estimate.ci_high, 2 / 3)
        self.assertTrue(estimate.ci_degenerate)

    def test_identical_methods_have_no_evidence_of_a_difference(self):
        """Return p=1, zero paired differences, and flagged point-mass intervals."""

        _, comparisons = self.compute(make_results(identical=True))
        for comparison in comparisons:
            self.assertEqual(comparison.difference, 0.0)
            self.assertEqual((comparison.ci_low, comparison.ci_high), (0.0, 0.0))
            self.assertTrue(comparison.ci_degenerate)
            self.assertEqual(comparison.p_value, 1.0)
            self.assertEqual(comparison.p_holm, 1.0)
            self.assertEqual((comparison.higher, comparison.equal, comparison.lower), (0, 6, 0))

    def test_all_successes_flag_degenerate_e2e_interval(self):
        """Mark an all-success bootstrap as degenerate instead of hiding the limit."""

        results = [replace(result, e2e_pass=True) for result in make_results()]
        estimates, _ = self.compute(results)
        for approach in APPROACHES:
            estimate = estimates[(approach, "Overall", "E2E")]
            self.assertEqual((estimate.estimate, estimate.ci_low, estimate.ci_high), (1.0, 1.0, 1.0))
            self.assertEqual(estimate.run_sd, 0.0)
            self.assertTrue(estimate.ci_degenerate)

    def test_holm_uses_the_complete_eight_comparison_family(self):
        """Recompute the step-down Holm correction independently for all tests."""

        _, comparisons = self.compute(make_results())
        ordered = sorted(comparisons, key=lambda item: item.p_value)
        running_max = 0.0
        self.assertEqual(len(ordered), 8)
        for rank, comparison in enumerate(ordered):
            running_max = max(running_max, min(1.0, (8 - rank) * comparison.p_value))
            self.assertAlmostEqual(comparison.p_holm, running_max)
            self.assertGreaterEqual(comparison.p_holm, comparison.p_value)

    def test_monte_carlo_p_values_use_plus_one_bounds_and_resolution(self):
        """Ensure no sampled permutation test reports a zero p-value."""

        permutations = 99
        _, comparisons = self.compute(make_results(), permutation_samples=permutations)
        for comparison in comparisons:
            self.assertGreaterEqual(comparison.p_value, 1 / (permutations + 1))
            self.assertLessEqual(comparison.p_value, 1.0)
            scaled = comparison.p_value * (permutations + 1)
            self.assertAlmostEqual(scaled, round(scaled))

    def test_seed_and_input_order_are_reproducible(self):
        """Keep the results fixed when input order changes but the seed does not."""

        results = make_results()
        expected = self.compute(results)
        shuffled = list(results)
        random.Random(19).shuffle(shuffled)
        projects, summaries = prepare_statistics(shuffled)
        random.Random(23).shuffle(projects)
        actual = compute_repeated_statistics(projects, list(reversed(summaries)), bootstrap_samples=400,
                                             permutation_samples=999, seed=17)
        self.assertEqual(expected, actual)

    def test_two_runs_use_two_run_sample_sd_and_report_correct_counts(self):
        """Allow selected repeated-run subsets without pretending they contain three."""

        results = make_results(runs=2)
        estimates, comparisons = self.compute(results)
        _, summaries = prepare_statistics(results)
        observed = [summary[("Incremental", "Overall")].project_functional_score for _, summary in summaries]
        self.assertAlmostEqual(estimates[("Incremental", "Overall", "PFS")].run_sd, stdev(observed))
        for comparison in comparisons:
            self.assertEqual((comparison.projects, comparison.runs_per_project, comparison.project_runs), (6, 2, 12))

    def test_rejects_mismatched_task_sets_and_duplicate_task_metrics(self):
        """Reject broken task pairing and duplicate combined project records."""

        projects, summaries = prepare_statistics(make_results())
        missing_task = [project for project in projects if not (project.approach == "Waterfall" and project.project_id == "M1")]
        for invalid in (missing_task, projects + [projects[0]]):
            with self.subTest(records=len(invalid)), self.assertRaises(ValueError):
                compute_repeated_statistics(invalid, summaries, bootstrap_samples=20, permutation_samples=19)

    def test_rejects_mismatched_categories_run_counts_and_method_denominators(self):
        """Reject incompatible project clusters before calculating inference."""

        projects, summaries = prepare_statistics(make_results())
        target = next(index for index, project in enumerate(projects) if project.approach == "Waterfall" and project.project_id == "M1")
        mutations = (
            {"category": "Complex"},
            {"runs": 2},
            {"module_records": projects[target].module_records + 1},
        )
        for mutation in mutations:
            invalid = list(projects)
            invalid[target] = replace(invalid[target], **mutation)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                compute_repeated_statistics(invalid, summaries, bootstrap_samples=20, permutation_samples=19)

    def test_rejects_single_run_repeated_statistics(self):
        """Do not invent a repeated-run SD when only one run was selected."""

        projects, summaries = prepare_statistics(make_results(runs=1))
        with self.assertRaises(ValueError):
            compute_repeated_statistics(projects, summaries, bootstrap_samples=20, permutation_samples=19)


if __name__ == "__main__":
    unittest.main()
