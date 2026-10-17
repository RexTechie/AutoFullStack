"""Generate per-run and combined artifacts for the three paper experiments.

Run from the repository with:
    python evaluation/scripts/generate_experiment_artifacts.py
    python evaluation/scripts/generate_experiment_artifacts.py --runs 3 --output-dir evaluation/run3_only

Figures retain the original paper palette, typography, and cost-plot layout.
Combined metrics average repeated runs within each project before averaging
projects. MFS@4 remains the pooled module-level proportion used in the paper.
Combined tables also report run-level sample standard deviations. Supplementary
statistics retain paired projects for bootstrap intervals and permutation tests.
When MetaGPT rows are present in the selected runs, a separate Simple-only
external comparison is exported without requiring external token measurements.
Artifacts default to evaluation/artifacts/, grouped into combined/, runs/run_N/,
and run_comparison/. Each scope separates tables/, figures/, data/, and preview/.
"""

from __future__ import annotations

import argparse
from pathlib import Path

if __package__:
    from .experiment_data import APPROACHES, DEFAULT_OUTPUT_DIR, RESULTS_DIR, load_project_results
    from .experiment_external import analyze_external_results, load_external_results
    from .experiment_rendering import (
        export_dataset, export_external_results, export_run_comparison, export_statistical_results, plt,
    )
    from .experiment_statistics import aggregate_projects, compute_repeated_statistics, compute_summary
else:
    from experiment_data import APPROACHES, DEFAULT_OUTPUT_DIR, RESULTS_DIR, load_project_results
    from experiment_external import analyze_external_results, load_external_results
    from experiment_rendering import (
        export_dataset, export_external_results, export_run_comparison, export_statistical_results, plt,
    )
    from experiment_statistics import aggregate_projects, compute_repeated_statistics, compute_summary


def build_parser() -> argparse.ArgumentParser:
    """Define the fixed three-run inputs and paper artifact output options."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, nargs="+", choices=(1, 2, 3), default=[1, 2, 3])
    parser.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--include-no-self-refinement", action="store_true",
        help="Also include the ablation method in the cost table and boxplot.",
    )
    parser.add_argument(
        "--tables-only", action="store_true",
        help="Export CSV, Markdown, and LaTeX without requiring Matplotlib.",
    )
    return parser


def main() -> int:
    """Validate selected runs, generate each run, and then generate their combined artifacts."""

    parser = build_parser()
    args = parser.parse_args()
    if len(set(args.runs)) != len(args.runs):
        parser.error("Each run must be selected only once.")
    if plt is None and not args.tables_only:
        parser.error("Matplotlib is required for figures. Install the repository requirements or use --tables-only.")
    runs = sorted(args.runs)
    if plt is not None:
        plt.rcParams.update({
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "pdf.fonttype": 42,
        })

    # 1. Load every selected input before writing any figures or comparison tables.
    try:
        results_by_run = {run: load_project_results(run, args.results_dir) for run in runs}
        reference_keys = {(p.approach, p.project_id) for p in results_by_run[runs[0]]}
        if any({(p.approach, p.project_id) for p in results} != reference_keys for results in results_by_run.values()):
            raise ValueError("Selected runs evaluate different project sets.")
        all_results = [result for results in results_by_run.values() for result in results]
        external_results = load_external_results(runs, args.results_dir, all_results)
        combined_projects = aggregate_projects(all_results)
        combined_summary = compute_summary(combined_projects)
        projects_by_run = {run: aggregate_projects(results) for run, results in results_by_run.items()}
        run_summaries = [(f"Run {run}", compute_summary(projects)) for run, projects in projects_by_run.items()]
        estimates, comparisons = ({}, [])
        if len(runs) > 1:
            estimates, comparisons = compute_repeated_statistics(combined_projects, run_summaries)
        external_analysis = analyze_external_results(external_results) if external_results else None
    except ModuleNotFoundError as error:
        parser.error(f"A required statistical dependency is missing: {error}. Install the repository requirements.")
    except (OSError, KeyError, ValueError) as error:
        parser.error(str(error))
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # 2. Export each run using exactly the same plotting and formatting functions.
    for (run, projects), (_, summary) in zip(projects_by_run.items(), run_summaries):
        export_dataset(args.output_dir / "runs" / f"run_{run}", f"Run {run}", projects, summary,
                       args.include_no_self_refinement, args.tables_only, combined=False)
        print(f"Run {run}: {len(projects)} project-method records exported.")

    # 3. Export the project-balanced combination and a cross-run comparison.
    if len(runs) > 1:
        export_dataset(args.output_dir / "combined", "Combined", combined_projects, combined_summary,
                       args.include_no_self_refinement, args.tables_only, combined=True, estimates=estimates)
        export_statistical_results(args.output_dir / "combined", run_summaries,
                                   estimates, comparisons, args.tables_only)
        print(f"Combined: {len(combined_projects) // len(APPROACHES)} paired projects; "
              f"{len(comparisons)} overall comparisons exported.")
    export_run_comparison(args.output_dir, run_summaries, combined_summary, args.tables_only)

    # 4. Add prefixed Simple external artifacts without changing the original comparisons.
    if external_analysis is not None:
        export_external_results(args.output_dir, external_analysis, args.tables_only)
        print(f"MetaGPT Simple: 10 paired projects across {len(runs)} selected runs; "
              f"{len(external_analysis.comparisons)} supplementary quality comparisons exported.")
    print(f"Artifacts saved to {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
