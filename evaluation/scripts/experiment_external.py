"""Evaluate the fixed Simple-only MetaGPT comparison without token-cost assumptions."""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from statistics import fmean, stdev
from typing import Sequence

if __package__:
    from .experiment_data import (
        APPROACHES, METRIC_ATTRIBUTES, MetricEstimate, PairedComparison, ProjectResult, read_csv_rows,
    )
    from .experiment_statistics import ANALYSIS_SEED, BOOTSTRAP_SAMPLES, _holm_adjust
else:
    from experiment_data import (
        APPROACHES, METRIC_ATTRIBUTES, MetricEstimate, PairedComparison, ProjectResult, read_csv_rows,
    )
    from experiment_statistics import ANALYSIS_SEED, BOOTSTRAP_SAMPLES, _holm_adjust


EXTERNAL_APPROACHES = ("Incremental", "MetaGPT")
QUALITY_METRICS = ("E2E", "PFS", "MFS4")


@dataclass(frozen=True)
class ExternalProjectResult:
    """Store one Simple task run with its single module score and recorded E2E status."""

    run: int
    project_id: str
    approach: str
    project_name: str
    score: float
    e2e_pass: bool


@dataclass(frozen=True)
class ExternalSummary:
    """Store quality means and denominators for the ten matched Simple tasks."""

    e2e_rate: float
    project_functional_score: float
    mfs_at_4: float
    projects: int
    project_runs: int
    passed_runs: int
    modules_at_4: int


@dataclass(frozen=True)
class ExternalAnalysis:
    """Carry validated external results and their descriptive and paired statistics."""

    results: list[ExternalProjectResult]
    run_summaries: list[tuple[str, dict[str, ExternalSummary]]]
    summary: dict[str, ExternalSummary]
    estimates: dict[tuple[str, str], MetricEstimate]
    comparisons: list[PairedComparison]
    bootstrap_samples: int = BOOTSTRAP_SAMPLES
    analysis_seed: int = ANALYSIS_SEED


def _validate_external_results(
    results: Sequence[ExternalProjectResult],
) -> tuple[dict[str, dict[str, list[ExternalProjectResult]]], list[str], list[int]]:
    """Require ten complete task pairs with identical selected runs before any resampling."""

    panel: dict[str, dict[str, list[ExternalProjectResult]]] = {
        approach: defaultdict(list) for approach in EXTERNAL_APPROACHES
    }
    keys = set()
    for result in results:
        key = (result.approach, result.project_id, result.run)
        if (result.approach not in panel or not result.project_id or not result.project_name
                or isinstance(result.run, bool) or not isinstance(result.run, int)
                or result.run not in (1, 2, 3)):
            raise ValueError(f"Invalid external task identity: {key}.")
        if key in keys:
            raise ValueError(f"Duplicate external task run: {key}.")
        if (result.score not in range(6) or not isinstance(result.e2e_pass, bool)
                or (not result.e2e_pass and result.score > 0)):
            raise ValueError(f"Invalid external score or E2E status: {key}.")
        keys.add(key)
        panel[result.approach][result.project_id].append(result)

    ids = sorted(panel[EXTERNAL_APPROACHES[0]])
    runs = sorted({result.run for result in results})
    if len(ids) != 10 or any(set(panel[approach]) != set(ids) for approach in EXTERNAL_APPROACHES):
        raise ValueError("External comparison requires exactly ten matched Simple tasks under both methods.")
    for approach in EXTERNAL_APPROACHES:
        for project_id in ids:
            repeated = panel[approach][project_id]
            if {result.run for result in repeated} != set(runs):
                raise ValueError(f"External task has missing runs: {(approach, project_id)}.")
            if len({result.project_name for result in repeated}) != 1:
                raise ValueError(f"External task name differs across runs: {(approach, project_id)}.")
            repeated.sort(key=lambda result: result.run)
    return panel, ids, runs


def load_external_results(
    runs: Sequence[int], results_dir: Path, internal_results: Sequence[ProjectResult],
) -> list[ExternalProjectResult]:
    """Load optional MetaGPT records and match all selected runs to Incremental Simple tasks.

    E2E requires both Backend and Frontend to pass build/compilation and startup.
    No external token measurements or unobserved complexity levels are synthesized.
    """

    if (not runs or len(set(runs)) != len(runs)
            or any(isinstance(run, bool) or not isinstance(run, int) or run not in (1, 2, 3) for run in runs)):
        raise ValueError("External inputs require distinct selected runs from 1, 2, and 3.")

    # 1. Detect an absent external experiment, but never silently accept a partial one.
    external_rows = {}
    for run in sorted(runs):
        for source in ("eval_functional_correctness.csv", "eval_e2e_executability.csv"):
            rows = read_csv_rows(results_dir / f"run_{run}" / source)
            if any(row["Approach"] not in (*APPROACHES, "MetaGPT") for row in rows):
                raise ValueError(f"Run {run}: unknown method in {source}.")
            external_rows[(run, source)] = [row for row in rows if row["Approach"] == "MetaGPT"]
    if not any(external_rows.values()):
        return []

    # 2. Validate one module and one E2E record per matched task before joining sources.
    results = []
    for run in sorted(runs):
        incremental = [result for result in internal_results
                       if result.run == run and result.approach == "Incremental" and result.category == "Simple"]
        ids = {result.project_id for result in incremental}
        if len(incremental) != 10 or len(ids) != 10 or any(len(result.scores) != 1 for result in incremental):
            raise ValueError(f"Run {run}: external reference requires ten one-module Incremental Simple tasks.")
        sources = []
        for source in ("eval_functional_correctness.csv", "eval_e2e_executability.csv"):
            indexed = {}
            for row in external_rows[(run, source)]:
                project_id = row["ProjectID"]
                if row["Category"] != "Simple" or project_id in indexed:
                    raise ValueError(f"Run {run}: duplicate or non-Simple MetaGPT task in {source}: {project_id}.")
                indexed[project_id] = row
            if set(indexed) != ids:
                raise ValueError(f"Run {run}: MetaGPT {source} must match all ten Incremental Simple tasks.")
            sources.append(indexed)
        score_rows, e2e_rows = sources
        for project_id in sorted(ids):
            score_row, e2e_row = score_rows[project_id], e2e_rows[project_id]
            if not score_row["Module"] or score_row["ProjectName"] != e2e_row["ProjectName"]:
                raise ValueError(f"Run {run}: inconsistent MetaGPT task metadata: {project_id}.")
            if any(e2e_row[component] not in {"Pass", "Failure"} for component in ("Backend", "Frontend")):
                raise ValueError(f"Run {run}: invalid MetaGPT E2E status: {project_id}.")
            results.append(ExternalProjectResult(
                run, project_id, "MetaGPT", score_row["ProjectName"], float(score_row["Score(0-5)"]),
                e2e_row["Backend"] == "Pass" and e2e_row["Frontend"] == "Pass",
            ))
        results.extend(ExternalProjectResult(
            result.run, result.project_id, result.approach, result.project_name, result.scores[0], result.e2e_pass,
        ) for result in incremental)

    # 3. Retain every observed outcome and require complete pairing across selected runs.
    _validate_external_results(results)
    return sorted(results, key=lambda result: (result.run, result.approach, result.project_id))


def _summarize_external_results(results: Sequence[ExternalProjectResult]) -> dict[str, ExternalSummary]:
    """Average task-level repeat means and pool original module success counts."""

    summary = {}
    for approach in EXTERNAL_APPROACHES:
        selected = [result for result in results if result.approach == approach]
        projects: dict[str, list[ExternalProjectResult]] = defaultdict(list)
        for result in selected:
            projects[result.project_id].append(result)
        passed = sum(result.e2e_pass for result in selected)
        successful = sum(result.score >= 4 for result in selected)
        summary[approach] = ExternalSummary(
            e2e_rate=fmean(fmean(result.e2e_pass for result in repeated) for repeated in projects.values()),
            project_functional_score=fmean(fmean(result.score for result in repeated) for repeated in projects.values()),
            mfs_at_4=successful / len(selected), projects=len(projects), project_runs=len(selected),
            passed_runs=passed, modules_at_4=successful,
        )
    return summary


def analyze_external_results(
    results: Sequence[ExternalProjectResult], *, bootstrap_samples: int = BOOTSTRAP_SAMPLES,
    seed: int = ANALYSIS_SEED,
) -> ExternalAnalysis:
    """Compute Simple-only summaries, paired task bootstrap CIs, and exact paired tests.

    The three quality tests form a separate supplementary Holm family. Bootstrap
    intervals condition on the observed repeats; exact swaps assume exchangeable
    method labels within independent task pairs. No individual run is resampled.
    """

    # 1. Validate the paired panel and provide descriptive results even for a single run.
    if isinstance(bootstrap_samples, bool) or not isinstance(bootstrap_samples, int) or bootstrap_samples <= 0:
        raise ValueError("bootstrap_samples must be a positive integer.")
    panel, ids, runs = _validate_external_results(results)
    ordered = sorted(results, key=lambda result: (result.run, result.approach, result.project_id))
    summary = _summarize_external_results(ordered)
    run_summaries = [(f"Run {run}", _summarize_external_results(
        [result for result in ordered if result.run == run])) for run in runs]
    estimates, comparisons = {}, []
    if len(runs) == 1:
        return ExternalAnalysis(ordered, run_summaries, summary, estimates, comparisons, bootstrap_samples, seed)

    import numpy as np

    # 2. Use a separate RNG and resample matched tasks, retaining all selected repeats.
    arrays = {approach: np.array([
        [fmean(result.e2e_pass for result in panel[approach][project_id]),
         fmean(result.score for result in panel[approach][project_id]),
         fmean(result.score >= 4 for result in panel[approach][project_id])]
        for project_id in ids
    ], dtype=float) for approach in EXTERNAL_APPROACHES}
    rng = np.random.default_rng(seed)
    indices = rng.choice(len(ids), size=(bootstrap_samples, len(ids)), replace=True)
    # Each Simple task has one module per run, so these MFS means equal pooled ratios.
    bootstrap = {approach: values[indices].mean(axis=1) for approach, values in arrays.items()}
    for approach in EXTERNAL_APPROACHES:
        low, high = np.quantile(bootstrap[approach], [.025, .975], axis=0)
        for index, metric in enumerate(QUALITY_METRICS):
            attribute = METRIC_ATTRIBUTES[metric]
            run_values = [getattr(values[approach], attribute) for _, values in run_summaries]
            estimates[(approach, metric)] = MetricEstimate(
                estimate=getattr(summary[approach], attribute), run_mean=fmean(run_values), run_sd=stdev(run_values),
                ci_low=float(low[index]), ci_high=float(high[index]),
                ci_degenerate=math.isclose(float(low[index]), float(high[index]), rel_tol=0, abs_tol=1e-12),
            )

    # 3. Enumerate all 2^10 whole-task swaps; exact tails need no Monte Carlo correction.
    differences = arrays["Incremental"] - arrays["MetaGPT"]
    observed = differences.mean(axis=0)
    signs = np.array(list(product((-1, 1), repeat=len(ids))), dtype=float)
    null = signs @ differences / len(ids)
    tolerance = np.maximum(1e-12, np.abs(observed) * np.finfo(float).eps * 100)
    extreme = np.count_nonzero(np.abs(null) >= np.abs(observed) - tolerance, axis=0)
    p_values = (extreme / len(signs)).tolist()
    adjusted = _holm_adjust(p_values)

    # 4. Pair each resampled contrast and correct only the declared external family.
    low, high = np.quantile(bootstrap["Incremental"] - bootstrap["MetaGPT"], [.025, .975], axis=0)
    for index, metric in enumerate(QUALITY_METRICS):
        values = differences[:, index]
        comparisons.append(PairedComparison(
            comparator="MetaGPT", metric=metric, difference=float(observed[index]),
            ci_low=float(low[index]), ci_high=float(high[index]),
            ci_degenerate=math.isclose(float(low[index]), float(high[index]), rel_tol=0, abs_tol=1e-12),
            p_value=p_values[index], p_holm=adjusted[index], projects=len(ids), runs_per_project=len(runs),
            project_runs=len(ids) * len(runs), higher=int(np.count_nonzero(values > 1e-12)),
            equal=int(np.count_nonzero(np.abs(values) <= 1e-12)), lower=int(np.count_nonzero(values < -1e-12)),
        ))
    return ExternalAnalysis(ordered, run_summaries, summary, estimates, comparisons, bootstrap_samples, seed)
