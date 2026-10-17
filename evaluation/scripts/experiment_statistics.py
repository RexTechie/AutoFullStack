"""Aggregate paper metrics and estimate task-paired repeated-run uncertainty."""

from __future__ import annotations

import math
from collections import defaultdict
from statistics import fmean, stdev
from typing import Sequence

if __package__:
    from .experiment_data import (
        APPROACHES, CATEGORIES, METRIC_ATTRIBUTES, SCOPES, STATISTICAL_METRICS,
        MetricEstimate, MetricSummary, PairedComparison, ProjectMetrics, ProjectResult,
    )
else:
    from experiment_data import (
        APPROACHES, CATEGORIES, METRIC_ATTRIBUTES, SCOPES, STATISTICAL_METRICS,
        MetricEstimate, MetricSummary, PairedComparison, ProjectMetrics, ProjectResult,
    )


BOOTSTRAP_SAMPLES = 30000
PERMUTATION_SAMPLES = 199999
ANALYSIS_SEED = 12138  # Statistical resampling only; not an LLM generation seed.


def aggregate_projects(results: Sequence[ProjectResult]) -> list[ProjectMetrics]:
    """Average repeated results inside each project without pooling its modules."""

    # 1. Keep each method-project pair intact across the selected repeated runs.
    grouped: dict[tuple[str, str], list[ProjectResult]] = defaultdict(list)
    for result in results:
        grouped[(result.approach, result.project_id)].append(result)

    # 2. Average project-run metrics, while retaining pooled module numerators.
    projects = []
    for key, repeated in sorted(grouped.items()):
        first = repeated[0]
        if len({result.run for result in repeated}) != len(repeated):
            raise ValueError(f"Duplicate project run: {key}.")
        if any((result.category, result.project_name) != (first.category, first.project_name) for result in repeated):
            raise ValueError(f"Project metadata differs across runs: {key}.")
        passed_runs = sum(result.e2e_pass for result in repeated)
        projects.append(ProjectMetrics(
            project_id=first.project_id,
            category=first.category,
            approach=first.approach,
            project_name=first.project_name,
            runs=len(repeated),
            passed_runs=passed_runs,
            module_records=sum(len(result.scores) for result in repeated),
            modules_at_4=sum(score >= 4 for result in repeated for score in result.scores),
            e2e_rate=passed_runs / len(repeated),
            project_functional_score=fmean(fmean(result.scores) for result in repeated),
            project_mfs_at_4=fmean(
                sum(score >= 4 for score in result.scores) / len(result.scores) for result in repeated
            ),
            avg_tokens=fmean(result.total_tokens for result in repeated),
        ))
    return projects


def compute_summary(projects: Sequence[ProjectMetrics]) -> dict[tuple[str, str], MetricSummary]:
    """Summarize each method and complexity with equal project weights.

    PFS, E2E, and token cost average project-level repeated-run means.
    MFS@4 pools observed module counts, while project MFS@4 is exported separately.
    """

    summary = {}
    for approach in APPROACHES:
        for scope in SCOPES:
            selected = [project for project in projects if project.approach == approach
                        and (scope == "Overall" or project.category == scope)]
            if not selected:
                raise ValueError(f"Missing projects for {approach}, {scope}.")
            module_records = sum(project.module_records for project in selected)
            modules_at_4 = sum(project.modules_at_4 for project in selected)
            summary[(approach, scope)] = MetricSummary(
                e2e_rate=fmean(project.e2e_rate for project in selected),
                project_functional_score=fmean(project.project_functional_score for project in selected),
                mfs_at_4=modules_at_4 / module_records,
                project_mfs_at_4=fmean(project.project_mfs_at_4 for project in selected),
                avg_tokens=fmean(project.avg_tokens for project in selected),
                projects=len(selected),
                project_runs=sum(project.runs for project in selected),
                passed_runs=sum(project.passed_runs for project in selected),
                module_records=module_records,
                modules_at_4=modules_at_4,
            )
    return summary


def _validate_paired_projects(
    projects: Sequence[ProjectMetrics],
    run_summaries: Sequence[tuple[str, dict[tuple[str, str], MetricSummary]]],
) -> tuple[dict[str, dict[str, ProjectMetrics]], list[str], int]:
    """Require complete, matched task clusters before resampling their outcomes."""

    run_count = len(run_summaries)
    if run_count < 2:
        raise ValueError("Repeated-run statistics require at least two run summaries.")
    labels = [label for label, _ in run_summaries]
    if any(not isinstance(label, str) or not label.strip() for label in labels):
        raise ValueError("Run summaries must have nonempty run labels.")
    if len(set(labels)) != run_count or any(label.strip().lower() == "combined" for label in labels):
        raise ValueError("Run summaries must contain distinct individual runs, not Combined.")

    panel = {approach: {} for approach in APPROACHES}
    for project in projects:
        if project.approach not in panel or project.category not in CATEGORIES:
            raise ValueError("Repeated-run statistics contain an unknown method or category.")
        if not isinstance(project.project_id, str) or not project.project_id:
            raise ValueError("Repeated-run statistics require nonempty ProjectID values.")
        key = (project.approach, project.project_id)
        if project.project_id in panel[project.approach]:
            raise ValueError(f"Duplicate paired project: {key}.")
        if isinstance(project.runs, bool) or not isinstance(project.runs, int) or project.runs != run_count:
            raise ValueError(f"Project run count does not match selected run summaries: {key}.")
        counts = (project.module_records, project.modules_at_4, project.passed_runs)
        if any(isinstance(value, bool) or not isinstance(value, int) for value in counts):
            raise ValueError(f"Paired project counts must be integers: {key}.")
        if (project.module_records <= 0 or not 0 <= project.modules_at_4 <= project.module_records
                or not 0 <= project.passed_runs <= run_count):
            raise ValueError(f"Invalid paired project counts: {key}.")
        values = (project.e2e_rate, project.project_functional_score,
                  project.project_mfs_at_4, project.avg_tokens)
        if (not all(math.isfinite(value) for value in values)
                or not 0 <= project.e2e_rate <= 1 or not 0 <= project.project_functional_score <= 5
                or not 0 <= project.project_mfs_at_4 <= 1 or project.avg_tokens < 0
                or not math.isclose(project.e2e_rate, project.passed_runs / run_count,
                                    rel_tol=0, abs_tol=1e-12)):
            raise ValueError(f"Invalid paired project metrics: {key}.")
        panel[project.approach][project.project_id] = project

    ids = sorted(panel[APPROACHES[0]])
    if not ids or any(set(panel[approach]) != set(ids) for approach in APPROACHES):
        raise ValueError("Repeated-run statistics require the same tasks under all three methods.")
    for project_id in ids:
        paired = [panel[approach][project_id] for approach in APPROACHES]
        if len({project.category for project in paired}) != 1:
            raise ValueError(f"Paired task categories differ across methods: {project_id}.")
        if len({project.module_records for project in paired}) != 1:
            raise ValueError(
                f"Paired module denominators differ across methods: {project_id}; "
                "whole-task sign flips require matching denominators."
            )
    category_counts = {category: sum(panel[APPROACHES[0]][pid].category == category for pid in ids)
                       for category in CATEGORIES}
    if any(count == 0 for count in category_counts.values()):
        raise ValueError("Repeated-run statistics require tasks in every complexity stratum.")
    for label, summary in run_summaries:
        for approach in APPROACHES:
            for scope in SCOPES:
                key = (approach, scope)
                if key not in summary:
                    raise ValueError(f"Missing run summary for {label}: {key}.")
                expected = len(ids) if scope == "Overall" else category_counts[scope]
                value = summary[key]
                if value.projects != expected or value.project_runs != expected:
                    raise ValueError(f"Run summary task counts differ from the paired data: {label}, {key}.")
                if not all(math.isfinite(getattr(value, attribute)) for attribute in METRIC_ATTRIBUTES.values()):
                    raise ValueError(f"Nonfinite run summary metric: {label}, {key}.")
    return panel, ids, run_count


def _bootstrap_metric_values(values, indices):
    """Evaluate task means and the pooled module ratio on sampled task clusters."""

    import numpy as np

    sampled = values[indices]
    return np.column_stack((sampled[:, :, 0].mean(axis=1), sampled[:, :, 1].mean(axis=1),
                            sampled[:, :, 2].sum(axis=1) / sampled[:, :, 3].sum(axis=1),
                            sampled[:, :, 4].mean(axis=1)))


def _holm_adjust(p_values: Sequence[float]) -> list[float]:
    """Adjust one complete comparison family with Holm's step-down procedure."""

    adjusted = [0.0] * len(p_values)
    running = 0.0
    for rank, index in enumerate(sorted(range(len(p_values)), key=lambda item: p_values[item])):
        running = max(running, min(1.0, (len(p_values) - rank) * p_values[index]))
        adjusted[index] = running
    return adjusted


def compute_repeated_statistics(
    combined_projects: Sequence[ProjectMetrics],
    run_summaries: Sequence[tuple[str, dict[tuple[str, str], MetricSummary]]],
    *, bootstrap_samples: int = BOOTSTRAP_SAMPLES,
    permutation_samples: int = PERMUTATION_SAMPLES,
    seed: int = ANALYSIS_SEED,
) -> tuple[dict[tuple[str, str, str], MetricEstimate], list[PairedComparison]]:
    """Estimate paired task-composition uncertainty without resampling individual runs.

    Bootstrap intervals are pointwise percentile intervals with complexity-stratified
    task clusters. Permutation tests exchange complete method outcomes within each
    task under method-label exchangeability, retaining all selected repetitions.
    Eight overall comparisons form one Holm family. Higher/lower counts describe
    raw Incremental values; lower token consumption is favorable.
    """

    # 1. Validate paired tasks and import the optional resampling dependency only here.
    for name, count in (("bootstrap_samples", bootstrap_samples), ("permutation_samples", permutation_samples)):
        if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
            raise ValueError(f"{name} must be a positive integer.")
    panel, ids, run_count = _validate_paired_projects(combined_projects, run_summaries)
    try:
        import numpy as np
    except ModuleNotFoundError as error:
        raise ValueError("NumPy is required for repeated-run statistics; single-run output does not require it.") from error
    summary = compute_summary(combined_projects)
    arrays = {approach: np.array([
        [panel[approach][pid].e2e_rate, panel[approach][pid].project_functional_score,
         panel[approach][pid].modules_at_4, panel[approach][pid].module_records,
         panel[approach][pid].avg_tokens] for pid in ids
    ], dtype=float) for approach in APPROACHES}
    rng = np.random.default_rng(seed)

    # 2. Reuse sampled task IDs for every method and pool module counts in each sample.
    categories = np.array([panel[APPROACHES[0]][pid].category for pid in ids])
    indices = {}
    for category in CATEGORIES:
        members = np.flatnonzero(categories == category)
        indices[category] = rng.choice(members, size=(bootstrap_samples, len(members)), replace=True)
    indices["Overall"] = np.concatenate([indices[category] for category in CATEGORIES], axis=1)
    estimates = {}
    overall_bootstrap = {}
    for scope in SCOPES:
        for approach in APPROACHES:
            bootstrap = _bootstrap_metric_values(arrays[approach], indices[scope])
            low, high = np.quantile(bootstrap, [.025, .975], axis=0)
            if scope == "Overall":
                overall_bootstrap[approach] = bootstrap
            for metric_index, metric in enumerate(STATISTICAL_METRICS):
                attribute = METRIC_ATTRIBUTES[metric]
                run_values = [getattr(run_summary[(approach, scope)], attribute) for _, run_summary in run_summaries]
                estimates[(approach, scope, metric)] = MetricEstimate(
                    estimate=getattr(summary[(approach, scope)], attribute),
                    run_mean=fmean(run_values), run_sd=stdev(run_values),
                    ci_low=float(low[metric_index]), ci_high=float(high[metric_index]),
                    ci_degenerate=math.isclose(float(low[metric_index]), float(high[metric_index]),
                                               rel_tol=0, abs_tol=1e-12),
                )

    # 3. Swap entire task outcomes through equivalent sign flips, including module weights.
    contributions, observed = [], []
    incremental = arrays[APPROACHES[0]]
    for comparator in APPROACHES[1:]:
        other = arrays[comparator]
        contributions.append(np.column_stack((
            (incremental[:, 0] - other[:, 0]) / len(ids),
            (incremental[:, 1] - other[:, 1]) / len(ids),
            (incremental[:, 2] - other[:, 2]) / incremental[:, 3].sum(),
            (incremental[:, 4] - other[:, 4]) / len(ids),
        )))
        observed.extend(getattr(summary[(APPROACHES[0], "Overall")], METRIC_ATTRIBUTES[metric])
                        - getattr(summary[(comparator, "Overall")], METRIC_ATTRIBUTES[metric])
                        for metric in STATISTICAL_METRICS)
    contributions = np.concatenate(contributions, axis=1)
    observed = np.array(observed)
    tolerance = np.maximum(1e-12, np.abs(observed) * np.finfo(float).eps * 100)
    extreme = np.zeros(len(observed), dtype=np.int64)
    for start in range(0, permutation_samples, 10000):
        batch = min(10000, permutation_samples - start)
        signs = rng.integers(0, 2, size=(batch, len(ids)), dtype=np.int8) * 2 - 1
        null = signs @ contributions
        extreme += np.count_nonzero(np.abs(null) >= np.abs(observed) - tolerance, axis=0)
    p_values = ((extreme + 1) / (permutation_samples + 1)).tolist()
    p_holm = _holm_adjust(p_values)

    # 4. Report paired differences and one Holm family, retaining raw comparison directions.
    comparisons = []
    for comparator_index, comparator in enumerate(APPROACHES[1:]):
        other = arrays[comparator]
        differences = overall_bootstrap[APPROACHES[0]] - overall_bootstrap[comparator]
        low, high = np.quantile(differences, [.025, .975], axis=0)
        project_differences = np.column_stack((
            incremental[:, 0] - other[:, 0], incremental[:, 1] - other[:, 1],
            incremental[:, 2] / incremental[:, 3] - other[:, 2] / other[:, 3],
            incremental[:, 4] - other[:, 4],
        ))
        for metric_index, metric in enumerate(STATISTICAL_METRICS):
            index = comparator_index * len(STATISTICAL_METRICS) + metric_index
            values = project_differences[:, metric_index]
            comparisons.append(PairedComparison(
                comparator=comparator, metric=metric, difference=float(observed[index]),
                ci_low=float(low[metric_index]), ci_high=float(high[metric_index]),
                ci_degenerate=math.isclose(float(low[metric_index]), float(high[metric_index]),
                                           rel_tol=0, abs_tol=1e-12),
                p_value=p_values[index], p_holm=p_holm[index], projects=len(ids),
                runs_per_project=run_count, project_runs=len(ids) * run_count,
                higher=int(np.count_nonzero(values > 1e-12)),
                equal=int(np.count_nonzero(np.abs(values) <= 1e-12)),
                lower=int(np.count_nonzero(values < -1e-12)),
            ))
    return estimates, comparisons
