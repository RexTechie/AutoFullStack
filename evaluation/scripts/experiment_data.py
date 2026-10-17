"""Load and validate the fixed three-run paper experiment data."""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = PROJECT_ROOT / "experiment_results"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "evaluation" / "artifacts"
CATEGORIES = ("Simple", "Medium", "Complex")
SCOPES = (*CATEGORIES, "Overall")
APPROACHES = ("Incremental", "Waterfall", "Incremental-NoSelfRefinement")
STATISTICAL_METRICS = ("E2E", "PFS", "MFS4", "Tokens")
METRIC_ATTRIBUTES = {
    "E2E": "e2e_rate",
    "PFS": "project_functional_score",
    "MFS4": "mfs_at_4",
    "Tokens": "avg_tokens",
}


BENCHMARK_FILES = {
    1: {
        "Incremental": "benchmark_results_incremental_all_20260314_104325.csv",
        "Waterfall": "benchmark_results_waterfall_all_20260318_165450.csv",
        "Incremental-NoSelfRefinement": "benchmark_results_incremental_no_self_refinement_all_20260409_214202.csv",
    },
    2: {
        "Incremental": "benchmark_results_incremental_all_20260907_214251.csv",
        "Waterfall": "benchmark_results_waterfall_all_20260908_213334.csv",
        "Incremental-NoSelfRefinement": "benchmark_results_incremental_no_self_refinement_all_20260910_102117.csv",
    },
    3: {
        "Incremental": "benchmark_results_incremental_all_20260911_221318.csv",
        "Waterfall": "benchmark_results_waterfall_all_20260914_101314.csv",
        "Incremental-NoSelfRefinement": "benchmark_results_incremental_no_self_refinement_all_20260911_093954.csv",
    },
}


@dataclass(frozen=True)
class ProjectResult:
    """Store the verified evaluation and token cost for one project run."""

    run: int
    project_id: str
    category: str
    approach: str
    project_name: str
    scores: tuple[float, ...]
    e2e_pass: bool
    total_tokens: float


@dataclass(frozen=True)
class ProjectMetrics:
    """Store a project's metrics after averaging its selected repeated runs."""

    project_id: str
    category: str
    approach: str
    project_name: str
    runs: int
    passed_runs: int
    module_records: int
    modules_at_4: int
    e2e_rate: float
    project_functional_score: float
    project_mfs_at_4: float
    avg_tokens: float


@dataclass(frozen=True)
class MetricSummary:
    """Store project-weighted metrics and module-pooled MFS@4 for one group."""

    e2e_rate: float
    project_functional_score: float
    mfs_at_4: float
    project_mfs_at_4: float
    avg_tokens: float
    projects: int
    project_runs: int
    passed_runs: int
    module_records: int
    modules_at_4: int


@dataclass(frozen=True)
class MetricEstimate:
    """Separate the combined estimate, run-level variation, and bootstrap interval."""

    estimate: float
    run_mean: float
    run_sd: float
    ci_low: float
    ci_high: float
    ci_degenerate: bool


@dataclass(frozen=True)
class PairedComparison:
    """Store an overall Incremental-minus-comparator project-paired comparison."""

    comparator: str
    metric: str
    difference: float
    ci_low: float
    ci_high: float
    ci_degenerate: bool
    p_value: float
    p_holm: float
    projects: int
    runs_per_project: int
    project_runs: int
    higher: int
    equal: int
    lower: int


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a supplied CSV using its existing UTF-8/BOM-compatible schema."""

    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{key: value.strip() for key, value in row.items()} for row in csv.DictReader(handle)]


def load_project_results(run: int, results_dir: Path) -> list[ProjectResult]:
    """Join module scores, recorded E2E results, and costs for a fixed run.

    E2E status covers build/compilation and startup checks for both components.
    Recorded status comes from the E2E CSV, never from benchmark heuristics.
    Namespace and module names are not used to join different repeated runs.
    """

    run_dir = results_dir / f"run_{run}"

    # 1. Group module scores by project and reject duplicate or invalid scores.
    score_groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    metadata: dict[tuple[str, str], tuple[str, str]] = {}
    module_keys = set()
    for row in read_csv_rows(run_dir / "eval_functional_correctness.csv"):
        if row["Approach"] == "MetaGPT":
            continue  # The external Simple comparison validates these records separately.
        if row["Approach"] not in APPROACHES:
            raise ValueError(f"Run {run}: unknown method: {row['Approach']}.")
        key = (row["Approach"], row["ProjectID"])
        module_key = (*key, row["Module"])
        score = float(row["Score(0-5)"])
        if module_key in module_keys or score not in range(6):
            raise ValueError(f"Run {run}: duplicate module or invalid score: {module_key}.")
        category_and_name = (row["Category"], row["ProjectName"])
        if key in metadata and metadata[key] != category_and_name:
            raise ValueError(f"Run {run}: inconsistent project metadata: {key}.")
        module_keys.add(module_key)
        metadata[key] = category_and_name
        score_groups[key].append(score)

    # 2. Read the common E2E status columns and preserve failed evaluations.
    e2e_rows: dict[tuple[str, str], dict[str, str]] = {}
    for row in read_csv_rows(run_dir / "eval_e2e_executability.csv"):
        if row["Approach"] == "MetaGPT":
            continue  # External quality data does not require a token benchmark file.
        if row["Approach"] not in APPROACHES:
            raise ValueError(f"Run {run}: unknown method: {row['Approach']}.")
        key = (row["Approach"], row["ProjectID"])
        if key in e2e_rows:
            raise ValueError(f"Run {run}: duplicate E2E project: {key}.")
        if row["Backend"] not in {"Pass", "Failure"} or row["Frontend"] not in {"Pass", "Failure"}:
            raise ValueError(f"Run {run}: invalid build status: {key}.")
        e2e_rows[key] = row

    # 3. Attach the exact benchmark file for each method; do not discover backups.
    token_rows: dict[tuple[str, str], dict[str, str]] = {}
    for approach, filename in BENCHMARK_FILES[run].items():
        for row in read_csv_rows(run_dir / filename):
            key = (row["Approach"], row["ProjectID"])
            tokens = float(row["TotalTokens"])
            if row["Approach"] != approach or key in token_rows or not math.isfinite(tokens) or tokens < 0:
                raise ValueError(f"Run {run}: duplicate, mismatched, or invalid token record: {key}.")
            token_rows[key] = row

    # 4. Require the same clean, complete project set in all three sources.
    if set(score_groups) != set(e2e_rows) or set(score_groups) != set(token_rows):
        raise ValueError(f"Run {run}: Functional, E2E, and benchmark project sets differ.")
    if {approach for approach, _ in score_groups} != set(APPROACHES):
        raise ValueError(f"Run {run}: expected the three paper methods.")
    reference_projects = {project_id for approach, project_id in score_groups if approach == "Incremental"}
    results = []
    for approach in APPROACHES:
        method_projects = {project_id for method, project_id in score_groups if method == approach}
        if method_projects != reference_projects:
            raise ValueError(f"Run {run}: methods evaluate different project sets.")
        for category in CATEGORIES:
            category_keys = sorted(key for key in score_groups if key[0] == approach and metadata[key][0] == category)
            if len(category_keys) != 10:
                raise ValueError(f"Run {run}: expected 10 {category} projects for {approach}.")
            for key in category_keys:
                project_category, project_name = metadata[key]
                if any(row["Category"] != project_category for row in (e2e_rows[key], token_rows[key])):
                    raise ValueError(f"Run {run}: project category mismatch: {key}.")
                scores = tuple(score_groups[key])
                if len(scores) not in {"Simple": (1,), "Medium": (3, 4), "Complex": (6,)}[category]:
                    raise ValueError(f"Run {run}: unexpected module count: {key}.")
                passed = e2e_rows[key]["Backend"] == "Pass" and e2e_rows[key]["Frontend"] == "Pass"
                if not passed and any(score > 0 for score in scores):
                    raise ValueError(f"Run {run}: failed build has a positive functional score: {key}.")
                results.append(ProjectResult(
                    run=run,
                    project_id=key[1],
                    category=category,
                    approach=approach,
                    project_name=project_name,
                    scores=scores,
                    e2e_pass=passed,
                    total_tokens=float(token_rows[key]["TotalTokens"]),
                ))
    if len(results) != len(score_groups):
        raise ValueError(f"Run {run}: unexpected project category.")
    return results
