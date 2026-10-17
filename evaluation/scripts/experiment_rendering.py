"""Export experiment tables and figures using the original paper styling."""

from __future__ import annotations

import csv
import random
import textwrap
from pathlib import Path
from statistics import fmean
from typing import Sequence

if __package__:
    from .experiment_data import (
        APPROACHES, CATEGORIES, METRIC_ATTRIBUTES, SCOPES, STATISTICAL_METRICS,
        MetricEstimate, MetricSummary, PairedComparison, ProjectMetrics,
    )
    from .experiment_statistics import ANALYSIS_SEED, BOOTSTRAP_SAMPLES, PERMUTATION_SAMPLES
    from .experiment_external import EXTERNAL_APPROACHES, QUALITY_METRICS, ExternalAnalysis, ExternalSummary
else:
    from experiment_data import (
        APPROACHES, CATEGORIES, METRIC_ATTRIBUTES, SCOPES, STATISTICAL_METRICS,
        MetricEstimate, MetricSummary, PairedComparison, ProjectMetrics,
    )
    from experiment_statistics import ANALYSIS_SEED, BOOTSTRAP_SAMPLES, PERMUTATION_SAMPLES
    from experiment_external import EXTERNAL_APPROACHES, QUALITY_METRICS, ExternalAnalysis, ExternalSummary

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import PercentFormatter
except ModuleNotFoundError:
    plt = None


MAIN_APPROACHES = ("Incremental", "Waterfall")
ABLATION_APPROACHES = ("Incremental", "Incremental-NoSelfRefinement")
DISPLAY_NAMES = {
    "Incremental": "Incremental",
    "Waterfall": "Waterfall",
    "Incremental-NoSelfRefinement": "Incremental w/o Self-Refinement",
    "MetaGPT": "MetaGPT",
}
METHOD_COLORS = {
    "Incremental": "#2A9D8F",
    "Waterfall": "#E76F51",
    "Incremental-NoSelfRefinement": "#E9C46A",
    "MetaGPT": "#457B9D",
}


PLOT_METRICS = {
    "e2e": ("e2e_rate", "E2E Executability", "E2E (%)", 1.0),
    "pfs": ("project_functional_score", "Project Functional Score", "PFS (0-5)", 5.0),
    "mfs_at_4": ("mfs_at_4", "Module Functional Success", "MFS@4 (%)", 1.0),
}


def write_csv_table(path: Path, headers: Sequence[str], rows: Sequence[Sequence[object]]) -> None:
    """Write traceable CSV values, preserving numeric precision supplied by callers."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def save_figure(figure, path: Path, *, table: bool = False) -> None:
    """Route a scope/stem to PNG previews and either paper or table-preview PDFs."""

    preview_dir = path.parent / "preview"
    pdf_dir = preview_dir if table else path.parent / "figures"
    preview_dir.mkdir(parents=True, exist_ok=True)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    figure.savefig(preview_dir / f"{path.name}.png", dpi=300, bbox_inches="tight")
    figure.savefig(pdf_dir / f"{path.name}.pdf", bbox_inches="tight")
    plt.close(figure)


def save_table_image(path: Path, title: str, headers: Sequence[str], rows: Sequence[Sequence[str]],
                     notes: Sequence[str] | None = None) -> None:
    """Keep the original draft-table style and give long method labels enough room."""

    note_text = "\n".join(textwrap.fill(note, width=130) for note in notes or ())
    note_height = (note_text.count("\n") + 1) * 0.22 + 0.2 if note_text else 0
    figure_height = max(3.5, len(rows) * 0.8 + 1.8) + note_height
    fig, ax = plt.subplots(figsize=(max(12, len(headers) * 2.2), figure_height))
    ax.axis("off")
    column_widths = None
    method_column = headers.index("Method") if "Method" in headers else None
    if method_column is not None and any(len(row[method_column]) > 22 for row in rows):
        column_widths = [0.62 / (len(headers) - 1)] * len(headers)
        column_widths[method_column] = 0.38
    if "95% CI" in headers:
        if len(headers) == 6:
            column_widths = [0.29, 0.13, 0.13, 0.27, 0.09, 0.09]
        else:
            column_widths = [0.30, 0.14, 0.16, 0.13, 0.27]
    table = ax.table(cellText=rows, colLabels=headers, loc="center", cellLoc="center",
                     colLoc="center", colWidths=column_widths)
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.0, 1.6)
    for (row_index, column_index), cell in table.get_celld().items():
        cell.set_edgecolor("#D9E0E8")
        cell.set_linewidth(0.8)
        if row_index == 0:
            cell.set_facecolor("#284B63")
            cell.set_text_props(color="white", weight="bold")
        else:
            cell.set_facecolor("#F7F9FB" if row_index % 2 else "#EDF2F7")
            if column_index == method_column:
                cell.set_text_props(weight="bold")
    ax.set_title(title, fontsize=14, fontweight="bold", pad=18)
    if note_text:
        fig.text(0.015, 0.015, note_text, fontsize=9, va="bottom", ha="left", color="#374151")
        fig.tight_layout(rect=(0, note_height / figure_height, 1, 1))
    else:
        fig.tight_layout()
    save_figure(fig, path, table=True)


def escape_latex_text(value: str) -> str:
    """Escape fixed table text and preserve statistical symbols in LaTeX fragments."""

    return (value.replace("%", r"\%").replace("&", r"\&").replace("_", r"\_")
            .replace("±", r"$\pm$").replace("<0.001", r"$<0.001$"))


def export_table(output_dir: Path, stem: str, title: str, headers: Sequence[str],
                 rows: Sequence[Sequence[str]], tables_only: bool,
                 notes: Sequence[str] | None = None,
                 image_notes: Sequence[str] | None = None) -> None:
    """Separate paper-ready LaTeX from formatted CSV/Markdown and image previews."""

    preview_dir = output_dir / "preview"
    tables_dir = output_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    write_csv_table(preview_dir / f"{stem}.csv", headers, rows)
    markdown_rows = [headers, ["---"] * len(headers), *rows]
    markdown = "\n".join("| " + " | ".join(row) + " |" for row in markdown_rows) + "\n"
    if notes:
        markdown += "\nNotes: " + "\n\n".join(notes) + "\n"
    (preview_dir / f"{stem}.md").write_text(markdown, encoding="utf-8")
    alignment = "".join("l" if header in {"Method", "Complexity", "Run"} else "r" for header in headers)
    latex = [f"\\begin{{tabular}}{{{alignment}}}", "\\toprule"]
    if notes:
        latex.insert(0, r"\resizebox{\ifdim\width>\linewidth\linewidth\else\width\fi}{!}{%")
    for index, row in enumerate([headers, *rows]):
        cells = [escape_latex_text(value) for value in row]
        latex.append(" & ".join(cells) + r" \\")
        if index == 0:
            latex.append(r"\midrule")
    latex.extend([r"\bottomrule", r"\end{tabular}"])
    if notes:
        latex.extend(["}", r"\par\smallskip", r"\begin{minipage}{\linewidth}",
                      r"\footnotesize Notes: " + " ".join(escape_latex_text(note) for note in notes),
                      r"\end{minipage}"])
    (tables_dir / f"{stem}.tex").write_text("\n".join(latex) + "\n", encoding="utf-8")
    if not tables_only:
        save_table_image(output_dir / stem, title, headers, rows,
                         notes if image_notes is None else image_notes)


def save_effectiveness_plot(path: Path, title: str, metric: str,
                            datasets: Sequence[tuple[str, dict[tuple[str, str], MetricSummary]]]) -> None:
    """Compare methods in three shared-scale complexity panels using paper styling."""

    # 1. Match the paper's three-panel layout with a shared metric scale.
    attribute, _, axis_label, ceiling = PLOT_METRICS[metric]
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 5.6), sharey=True)
    width = 0.24
    hatches = ("", "//", "..")
    handles = []
    # 2. Keep method encodings fixed and label the observed means.
    for axis, category in zip(axes, CATEGORIES):
        for method_index, approach in enumerate(APPROACHES):
            values = [getattr(summary[(approach, category)], attribute) for _, summary in datasets]
            positions = [index + (method_index - 1) * width for index in range(len(datasets))]
            bars = axis.bar(positions, values, width=width, color=METHOD_COLORS[approach],
                            edgecolor="#374151", linewidth=0.6, hatch=hatches[method_index], zorder=3)
            if category == "Simple":
                handles.append(bars[0])
            for bar, value in zip(bars, values):
                label = f"{value:.1%}" if ceiling == 1 else f"{value:.2f}"
                label_offset = 4 + method_index * 10 if len(datasets) > 1 and value > 0 else 4
                axis.annotate(label, (bar.get_x() + bar.get_width() / 2, value),
                              xytext=(0, label_offset), textcoords="offset points", ha="center", fontsize=9)
        axis.set_title(category, fontsize=12, fontweight="bold")
        axis.set_xticks(range(len(datasets)), [label for label, _ in datasets])
        axis.set_ylim(0, ceiling * 1.12)
        axis.set_yticks([ceiling * index / 5 for index in range(6)])
        if ceiling == 1:
            axis.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
        axis.grid(True, axis="y", linestyle="--", linewidth=0.6, alpha=0.35)
        axis.set_axisbelow(True)
    # 3. Use one paper-style legend and export the same figure in both formats.
    axes[0].set_ylabel(axis_label)
    fig.legend(handles, [DISPLAY_NAMES[approach] for approach in APPROACHES],
               loc="upper center", bbox_to_anchor=(0.5, 0.95), ncol=3, frameon=True)
    fig.suptitle(title, fontsize=16, fontweight="bold", y=1.02)
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    save_figure(fig, path)


def save_cost_plot(path: Path, title: str, projects: Sequence[ProjectMetrics],
                   approaches: Sequence[str], combined: bool) -> None:
    """Preserve the original token boxplot; combined points are per-project run means."""

    fig, axes = plt.subplots(1, 3, figsize=(15.5, 5.6), sharey=False)
    for axis, category in zip(axes, CATEGORIES):
        category_projects = [project for project in projects if project.category == category]
        token_groups = [[project.avg_tokens for project in category_projects if project.approach == approach]
                        for approach in approaches]
        boxplot = axis.boxplot(
            token_groups, patch_artist=True, widths=0.55, showfliers=False,
            medianprops={"color": "#1F2933", "linewidth": 1.2},
            whiskerprops={"color": "#4B5563", "linewidth": 1.0},
            capprops={"color": "#4B5563", "linewidth": 1.0},
            boxprops={"edgecolor": "#374151", "linewidth": 1.0},
        )
        for patch, approach in zip(boxplot["boxes"], approaches):
            patch.set_facecolor(METHOD_COLORS[approach])
            patch.set_alpha(0.35)
        for position, approach in enumerate(approaches, start=1):
            method_projects = [project for project in category_projects if project.approach == approach]
            for project in method_projects:
                jitter = random.Random(f"{approach}:{project.project_id}").uniform(-0.12, 0.12)
                axis.scatter(position + jitter, project.avg_tokens, s=38, marker="o",
                             color=METHOD_COLORS[approach], edgecolors="none", alpha=0.48, zorder=3)
            axis.scatter(position, fmean(project.avg_tokens for project in method_projects), s=135,
                         marker="D", color=METHOD_COLORS[approach], edgecolors="#1F2933",
                         linewidths=1.0, zorder=4)
        axis.set_title(category, fontsize=12, fontweight="bold")
        axis.set_xticks(range(1, len(approaches) + 1))
        axis.set_xticklabels([DISPLAY_NAMES[method].replace(" w/o ", " w/o\n") for method in approaches],
                            rotation=15, ha="right")
        axis.grid(True, linestyle="--", linewidth=0.6, alpha=0.35)
        axis.ticklabel_format(style="plain", axis="y")
    axes[0].set_ylabel("Mean Total Tokens Across Runs" if combined else "Total Tokens")
    project_label = f"Project mean ({projects[0].runs} runs)" if combined else "Project"
    marker_handles = [
        Line2D([0], [0], marker="o", color="w", label=project_label, markerfacecolor="#94A3B8",
               markeredgecolor="none", markersize=9, alpha=0.6),
        Line2D([0], [0], marker="D", color="w", label="Method Mean", markerfacecolor="#FFFFFF",
               markeredgecolor="#1F2933", markersize=9),
    ]
    fig.legend(handles=marker_handles, title="Marker", loc="upper right", frameon=True)
    fig.suptitle(title, fontsize=16, fontweight="bold", y=1.02)
    if combined:
        fig.text(0.01, 0.015, "Each point is one task's mean across selected runs; boxes show between-task spread, not run-to-run variability.",
                 fontsize=9, color="#374151")
        fig.tight_layout(rect=(0, 0.06, 1, 0.9))
    else:
        fig.tight_layout(rect=(0, 0, 1, 0.9))
    save_figure(fig, path)


def format_metric_value(metric: str, value: float, signed: bool = False,
                         difference: bool = False) -> str:
    """Format rates as percentages or percentage-point differences and other units directly."""

    sign = "+" if signed else ""
    if metric in {"E2E", "MFS4"}:
        return f"{value * 100:{sign}.1f}" + (" pp" if difference else "%")
    if metric == "PFS":
        return f"{value:{sign}.2f}"
    return f"{value:{sign},.1f}"


def format_estimate_with_sd(metric: str, value: MetricEstimate) -> str:
    """Display a combined point estimate with sample SD of its selected run aggregates."""

    return f"{format_metric_value(metric, value.estimate)} ± {format_metric_value(metric, value.run_sd)}"


def export_dataset(output_dir: Path, label: str, projects: Sequence[ProjectMetrics],
                    summary: dict[tuple[str, str], MetricSummary],
                    include_ablation_cost: bool, tables_only: bool, combined: bool,
                    estimates: dict[tuple[str, str, str], MetricEstimate] | None = None) -> None:
    """Export one run or the combined results with the original paper table grouping."""

    # 1. Keep main-result and ablation tables separate, in their original row order.
    repeated_statistics = combined and estimates is not None
    quality_notes = None
    if repeated_statistics:
        quality_notes = [
            f"Entries are the combined estimate ± sample SD of {projects[0].runs} run-level aggregates (ddof=1), not SE or CI; rate SDs correspond to percentage points.",
            "There are 10 paired tasks per complexity and 30 overall; repeat outcomes are not independent tasks. MFS@4 pools successful modules and module totals.",
            "E2E requires both the front end and back end to pass build/compilation and startup checks; it does not imply complete business functionality.",
        ]
    for stem, title, methods in (
        ("main_result", "Main Result", MAIN_APPROACHES),
        ("ablation_study", "Ablation Study", ABLATION_APPROACHES),
    ):
        rows = []
        for approach in methods:
            for scope in SCOPES:
                value = summary[(approach, scope)]
                metrics = ([format_estimate_with_sd(metric, estimates[(approach, scope, metric)])
                            for metric in ("E2E", "PFS", "MFS4")] if repeated_statistics else
                           [f"{value.e2e_rate:.1%}", f"{value.project_functional_score:.2f}",
                            f"{value.mfs_at_4:.1%}"])
                rows.append([DISPLAY_NAMES[approach], scope, *metrics])
        export_table(output_dir, f"{stem}_table", f"{title} ({label})",
                     ["Method", "Complexity", "E2E", "PFS", "MFS@4"], rows, tables_only, quality_notes)

    # 2. Keep the original cost comparison unless the ablation cost is requested.
    cost_approaches = ("Incremental", "Incremental-NoSelfRefinement", "Waterfall") if include_ablation_cost else MAIN_APPROACHES
    cost_rows = [[DISPLAY_NAMES[method], scope,
                 format_estimate_with_sd("Tokens", estimates[(method, scope, "Tokens")]) if repeated_statistics
                 else f"{summary[(method, scope)].avg_tokens:.1f}"]
                 for method in cost_approaches for scope in SCOPES]
    cost_notes = ([
        f"Entries are equal-task-weight combined mean Tokens ± sample SD of {projects[0].runs} run-level mean Token values (ddof=1), not SE or CI.",
        "There are 10 tasks per complexity and 30 overall. Combined boxplot points are task means across runs; boxplot spread is between tasks, not between runs.",
    ] if repeated_statistics else None)
    export_table(output_dir, "cost_analysis_table", f"Cost Analysis ({label})",
                 ["Method", "Complexity", "Avg Tokens"], cost_rows, tables_only, cost_notes)
    write_csv_table(output_dir / "data" / "cost_analysis_plot_data.csv",
                    ["Method", "Complexity", "ProjectID", "ProjectName", "Avg Tokens", "PFS", "Runs"],
                    [[DISPLAY_NAMES[p.approach], p.category, p.project_id, p.project_name,
                      p.avg_tokens, p.project_functional_score, p.runs]
                     for p in projects if p.approach in cost_approaches])
    write_csv_table(output_dir / "data" / "project_metrics.csv",
                    ["Approach", "Category", "ProjectID", "ProjectName", "Runs", "E2E", "PFS",
                     "ProjectMFS4", "AvgTokens", "ModuleRecords", "ModulesAtLeast4", "PassedRuns"],
                    [[p.approach, p.category, p.project_id, p.project_name, p.runs, p.e2e_rate,
                      p.project_functional_score, p.project_mfs_at_4, p.avg_tokens,
                      p.module_records, p.modules_at_4, p.passed_runs] for p in projects])

    # 3. Use identical scales and method colors for all effectiveness figures.
    if not tables_only:
        for metric, (_, title, _, _) in PLOT_METRICS.items():
            save_effectiveness_plot(output_dir / metric, f"{title} ({label})",
                                    metric, [(label, summary)])
        save_cost_plot(output_dir / "cost_analysis_boxplot",
                       f"Cost Analysis ({label})", projects, cost_approaches, combined)


def export_run_comparison(output_dir: Path,
                           run_summaries: Sequence[tuple[str, dict[tuple[str, str], MetricSummary]]],
                           combined_summary: dict[tuple[str, str], MetricSummary], tables_only: bool) -> None:
    """Export exact per-run/combined values and directly comparable repeated-run figures."""

    comparison_dir = output_dir / "run_comparison"
    # 1. Retain exact values and denominators for every observed group.
    all_summaries = list(run_summaries)
    if len(run_summaries) > 1:
        all_summaries.append(("Combined", combined_summary))
    rows = []
    for label, summary in all_summaries:
        for approach in APPROACHES:
            for scope in SCOPES:
                value = summary[(approach, scope)]
                rows.append([label, approach, scope, value.projects, value.project_runs,
                             value.e2e_rate, value.project_functional_score, value.mfs_at_4,
                             value.project_mfs_at_4, value.avg_tokens, value.passed_runs,
                             value.module_records, value.modules_at_4])
    write_csv_table(comparison_dir / "data" / "summary_values.csv",
                    ["Run", "Approach", "Category", "Projects", "ProjectRuns", "E2E", "PFS", "MFS4",
                     "ProjectMFS4", "AvgTokens", "PassedRuns", "ModuleRecords", "ModulesAtLeast4"], rows)
    # 2. Keep rounded overall comparisons separate from the precise CSV.
    overall_rows = []
    for label, summary in all_summaries:
        for approach in APPROACHES:
            value = summary[(approach, "Overall")]
            overall_rows.append([label, DISPLAY_NAMES[approach], f"{value.e2e_rate:.1%}",
                                 f"{value.project_functional_score:.2f}", f"{value.mfs_at_4:.1%}",
                                 f"{value.avg_tokens:.1f}"])
    export_table(comparison_dir, "overall_results_table", "Overall Results Across Runs",
                 ["Run", "Method", "E2E", "PFS", "MFS@4", "Avg Tokens"], overall_rows, tables_only)
    # 3. Compare repeated runs only when more than one run was selected.
    if not tables_only and len(run_summaries) > 1:
        for metric, (_, title, _, _) in PLOT_METRICS.items():
            save_effectiveness_plot(comparison_dir / metric,
                                    f"{title} Across Runs", metric, all_summaries)


def format_p_value(value: float) -> str:
    """Round displayed p-values without showing a small nonzero probability as zero."""

    return "<0.001" if value < 0.001 else f"{value:.3f}"


def export_statistical_results(output_dir: Path,
                               run_summaries: Sequence[tuple[str, dict[tuple[str, str], MetricSummary]]],
                               estimates: dict[tuple[str, str, str], MetricEstimate],
                               comparisons: Sequence[PairedComparison], tables_only: bool) -> None:
    """Export exact statistical evidence and compact overall tables for the paper supplement."""

    # 1. Retain raw metric estimates, run variance, intervals, and actual denominators.
    metric_rows = []
    run_count = len(run_summaries)
    units = {"E2E": "proportion", "PFS": "score points", "MFS4": "proportion", "Tokens": "tokens"}
    for approach in APPROACHES:
        for scope in SCOPES:
            groups = [summary[(approach, scope)] for _, summary in run_summaries]
            for metric in STATISTICAL_METRICS:
                value = estimates[(approach, scope, metric)]
                metric_rows.append([
                    approach, scope, metric, value.estimate, value.run_mean, value.run_sd,
                    value.run_sd ** 2, value.ci_low, value.ci_high, value.ci_degenerate,
                    groups[0].projects, run_count, sum(group.project_runs for group in groups),
                    sum(group.module_records for group in groups), sum(group.modules_at_4 for group in groups),
                    units[metric],
                ])
    write_csv_table(output_dir / "data" / "metric_estimates.csv",
                    ["Approach", "Category", "Metric", "Estimate", "RunMean", "RunSD", "RunVariance",
                     "CILow", "CIHigh", "CIDegenerate", "Projects", "RunsPerProject", "ProjectRuns",
                     "ModuleRecords", "ModulesAtLeast4", "Unit"], metric_rows)

    # 2. Keep paired effect signs and both raw and family-adjusted p-values inspectable.
    comparison_rows = [[
        "Incremental", value.comparator, value.metric, value.difference, value.ci_low, value.ci_high,
        value.ci_degenerate, value.p_value, value.p_holm, value.projects, value.runs_per_project,
        value.project_runs, value.higher, value.equal, value.lower, units[value.metric],
    ] for value in comparisons]
    write_csv_table(output_dir / "data" / "paired_comparisons.csv",
                    ["Approach", "Comparator", "Metric", "Difference", "CILow", "CIHigh", "CIDegenerate",
                     "PValue", "PHolm", "Projects", "RunsPerProject", "ProjectRuns",
                     "ProjectsHigher", "ProjectsEqual", "ProjectsLower", "Unit"], comparison_rows)

    # 3. Keep uncertainty separate from the existing main-result table structure.
    uncertainty_rows = []
    metric_labels = {"E2E": "E2E", "PFS": "PFS (points)", "MFS4": "MFS@4", "Tokens": "Tokens"}
    for approach in APPROACHES:
        for metric in STATISTICAL_METRICS:
            value = estimates[(approach, "Overall", metric)]
            interval = (f"[{format_metric_value(metric, value.ci_low)}, "
                        f"{format_metric_value(metric, value.ci_high)}]")
            if value.ci_degenerate:
                interval += " *"
            uncertainty_rows.append([
                DISPLAY_NAMES[approach], metric_labels[metric], format_metric_value(metric, value.estimate),
                format_metric_value(metric, value.run_sd, difference=metric in {"E2E", "MFS4"}), interval,
            ])
    overall_projects = run_summaries[0][1][("Incremental", "Overall")].projects
    uncertainty_notes = [
        f"n={overall_projects} paired benchmark tasks with {run_count} selected runs per task and method; repeat outcomes are not independent tasks. Run SD is the sample SD of the selected run aggregates (ddof=1), not bootstrap SE or a precise estimate of LLM stochastic variance.",
        f"Pointwise 95% percentile CIs use {BOOTSTRAP_SAMPLES:,} paired, complexity-stratified task-cluster bootstrap samples; all selected repeats and modules remain inside each sampled task. These intervals condition on the observed repeats.",
        "E2E/PFS/Tokens use equal task weights. MFS@4 pools module successes and totals; its pooled estimate can differ from the mean of run-level rates. Rate SDs use percentage points (pp).",
        f"Analysis RNG seed {ANALYSIS_SEED} makes resampling reproducible; it is not an LLM generation seed. * A zero-width empirical CI does not establish certainty beyond these tasks/runs.",
        "E2E requires both the front end and back end to pass build/compilation and startup checks; it does not imply complete business functionality. Intervals are not simultaneous and do not establish generalization to arbitrary applications.",
    ]
    uncertainty_image_notes = [
        f"n={overall_projects} paired tasks x {run_count} selected runs per method. Run SD is descriptive sample SD across run aggregates (ddof=1), not SE; rate SDs use pp.",
        f"Pointwise 95% CIs: {BOOTSTRAP_SAMPLES:,} paired, complexity-stratified task-cluster bootstrap samples, conditional on observed repeats. MFS@4 pools modules.",
        "* Zero-width empirical CIs do not imply certainty. E2E covers build/compilation and startup, not complete business functionality. Full statistical notes accompany the MD/TeX exports.",
    ]
    export_table(output_dir, "overall_uncertainty_table", "Overall Estimates, Run Variability, and Confidence Intervals",
                 ["Method", "Metric", "Estimate", "Run SD", "95% CI"], uncertainty_rows,
                 tables_only, uncertainty_notes, uncertainty_image_notes)

    # 4. Report only the preselected overall comparisons, not subgroup significance tests.
    paired_rows = []
    paired_labels = {"E2E": "E2E (pp)", "PFS": "PFS (points)", "MFS4": "MFS@4 (pp)", "Tokens": "Tokens"}
    for value in comparisons:
        scale = 100 if value.metric in {"E2E", "MFS4"} else 1
        numeric_metric = "PFS" if value.metric == "PFS" else "Tokens"
        interval = (f"[{format_metric_value(numeric_metric, value.ci_low * scale, signed=True)}, "
                    f"{format_metric_value(numeric_metric, value.ci_high * scale, signed=True)}]")
        if value.ci_degenerate:
            interval += " *"
        paired_rows.append([
            f"vs. {DISPLAY_NAMES[value.comparator]}", paired_labels[value.metric],
            format_metric_value(numeric_metric, value.difference * scale, signed=True), interval,
            format_p_value(value.p_value), format_p_value(value.p_holm),
        ])
    paired_notes = [
        f"All effects are Incremental minus comparator, using {overall_projects} paired tasks averaged across {run_count} selected runs. Positive quality differences favor Incremental; negative Token differences favor Incremental. pp denotes percentage points.",
        f"95% CIs use {BOOTSTRAP_SAMPLES:,} paired, complexity-stratified task-cluster bootstrap samples, retaining repeats/modules and conditioning on observed repeats. These are pointwise, not family-wise intervals.",
        f"Two-sided paired label-swap permutation tests use {PERMUTATION_SAMPLES:,} Monte Carlo permutations and the plus-one correction. Method labels are swapped once per task for all repeats/modules together, assuming exchangeability under the null.",
        "Holm p adjusts one family of 8 overall comparisons: two comparators x E2E, PFS, MFS@4, and Tokens. No per-complexity significance tests are performed; an unadjusted CI excluding zero need not imply Holm-adjusted significance.",
        f"Task clusters are treated as independent. Analysis RNG seed {ANALYSIS_SEED} is not an LLM generation seed. * A zero-width empirical CI is not proof of certainty. Recorded E2E covers build/compilation and startup, not complete business functionality.",
    ]
    paired_image_notes = [
        f"Incremental minus comparator; n={overall_projects} paired tasks x {run_count} selected runs. Positive quality / negative Token effects favor Incremental; pp denotes percentage points.",
        f"95% task-cluster bootstrap CIs ({BOOTSTRAP_SAMPLES:,} samples) condition on observed repeats. Two-sided task-level permutation tests: {PERMUTATION_SAMPLES:,} permutations, plus-one correction.",
        "Holm p adjusts all 8 overall comparisons; CIs are pointwise, not Holm-adjusted. * Zero-width CIs do not imply certainty. Full methodological notes accompany the MD/TeX exports.",
    ]
    export_table(output_dir, "overall_paired_comparisons_table", "Overall Paired Differences (Incremental - Comparator)",
                 ["Method", "Metric", "Difference", "95% CI", "p", "Holm p"], paired_rows,
                 tables_only, paired_notes, paired_image_notes)


def save_external_effectiveness_plot(
    path: Path, title: str, summary: dict[str, ExternalSummary], run_count: int,
    estimates: dict[tuple[str, str], MetricEstimate] | None = None,
) -> None:
    """Compare the two methods on Simple tasks, showing bootstrap CIs only for repeated runs."""

    # 1. Keep the paper palette and three-panel layout, with one quality metric per panel.
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 5.6))
    for axis, metric, (attribute, panel_title, axis_label, ceiling) in zip(axes, QUALITY_METRICS, PLOT_METRICS.values()):
        for position, approach in enumerate(EXTERNAL_APPROACHES):
            value = getattr(summary[approach], attribute)
            axis.bar(position, value, width=0.55, color=METHOD_COLORS[approach],
                     edgecolor="#374151", linewidth=0.6, hatch="" if position == 0 else "//", zorder=3)
            annotation_height = value
            if estimates is not None:
                interval = estimates[(approach, metric)]
                axis.vlines(position, interval.ci_low, interval.ci_high, color="#1F2933", linewidth=1.2, zorder=4)
                axis.hlines((interval.ci_low, interval.ci_high), position - 0.09, position + 0.09,
                            color="#1F2933", linewidth=1.2, zorder=4)
                annotation_height = max(value, interval.ci_high)
            axis.annotate(format_metric_value(metric, value), (position, annotation_height),
                          xytext=(0, 5), textcoords="offset points", ha="center", fontsize=10)
        axis.set_title(panel_title, fontsize=12, fontweight="bold")
        axis.set_xticks(range(len(EXTERNAL_APPROACHES)), [DISPLAY_NAMES[a] for a in EXTERNAL_APPROACHES])
        axis.set_ylabel(axis_label)
        axis.set_ylim(0, ceiling * 1.12)
        axis.set_yticks([ceiling * index / 5 for index in range(6)])
        if ceiling == 1:
            axis.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
        axis.grid(True, axis="y", linestyle="--", linewidth=0.6, alpha=0.35)
        axis.set_axisbelow(True)

    # 2. Distinguish task-cluster confidence intervals from descriptive run-level SD.
    task_count = summary[EXTERNAL_APPROACHES[0]].projects
    note = f"Simple tasks only: n={task_count} paired task clusters, {run_count} observed run(s) per task and method."
    if estimates is not None:
        note += " Whiskers: pointwise 95% task-cluster bootstrap CIs, not run SD."
    else:
        note += " Bars show single-run point estimates; no CI or run SD is reported."
    fig.text(0.01, 0.015, note, fontsize=9, color="#374151")
    fig.suptitle(title, fontsize=16, fontweight="bold", y=1.02)
    fig.tight_layout(rect=(0, 0.07, 1, 0.94))
    save_figure(fig, path)


def export_external_results(output_dir: Path, analysis: ExternalAnalysis, tables_only: bool) -> None:
    """Add prefixed Simple-only external artifacts to the shared output scopes."""

    comparison_dir = output_dir / "run_comparison"
    combined_dir = output_dir / "combined"
    # 1. Preserve run-level quality observations and exact summary denominators.
    run_count = len(analysis.run_summaries)
    bootstrap_samples, analysis_seed = analysis.bootstrap_samples, analysis.analysis_seed
    task_count = analysis.summary[EXTERNAL_APPROACHES[0]].projects
    units = {"E2E": "proportion", "PFS": "score points", "MFS4": "proportion"}
    write_csv_table(comparison_dir / "data" / "external_simple_project_runs.csv",
                    ["Run", "Approach", "Category", "ProjectID", "ProjectName", "Score(0-5)", "E2E", "MFS4"],
                    [[r.run, r.approach, "Simple", r.project_id, r.project_name, r.score,
                      int(r.e2e_pass), int(r.score >= 4)] for r in analysis.results])
    all_summaries = list(analysis.run_summaries)
    if run_count > 1:
        all_summaries.append(("Combined", analysis.summary))
    write_csv_table(comparison_dir / "data" / "external_simple_summary_values.csv",
                    ["Run", "Approach", "Category", "Projects", "ProjectRuns", "E2E", "PFS", "MFS4",
                     "PassedRuns", "ModuleRecords", "ModulesAtLeast4"],
                    [[label, approach, "Simple", value.projects, value.project_runs, value.e2e_rate,
                      value.project_functional_score, value.mfs_at_4, value.passed_runs,
                      value.project_runs, value.modules_at_4]
                     for label, summary in all_summaries for approach in EXTERNAL_APPROACHES
                     for value in [summary[approach]]])

    # 2. Retain separate per-run tables and plots, using only the ten Simple tasks.
    evaluation_note = ("E2E requires both the front end and back end to pass build/compilation and startup checks; "
                       "it does not imply complete business functionality.")
    run_notes = [
        f"Simple tasks only: {task_count} paired tasks, with one assessed module per task and run. Values summarize one run across the matched tasks; repeats are not additional independent tasks.",
        evaluation_note,
    ]
    for label, summary in analysis.run_summaries:
        run_directory = output_dir / "runs" / label.lower().replace(" ", "_")
        rows = [[DISPLAY_NAMES[approach], "Simple",
                 *[format_metric_value(metric, getattr(summary[approach], METRIC_ATTRIBUTES[metric]))
                   for metric in QUALITY_METRICS]] for approach in EXTERNAL_APPROACHES]
        export_table(run_directory, "external_simple_table", f"External Comparison on Simple Tasks ({label})",
                     ["Method", "Complexity", "E2E", "PFS", "MFS@4"], rows, tables_only, run_notes)
        if not tables_only:
            save_external_effectiveness_plot(run_directory / "external_simple_effectiveness",
                                              f"External Comparison on Simple Tasks ({label})", summary, 1)

    comparison_rows = [[label, DISPLAY_NAMES[approach], "Simple",
                        *[format_metric_value(metric, getattr(summary[approach], METRIC_ATTRIBUTES[metric]))
                          for metric in QUALITY_METRICS]]
                       for label, summary in all_summaries for approach in EXTERNAL_APPROACHES]
    comparison_notes = [
        f"All rows use the same {task_count} matched Simple tasks; each task has one assessed module per run. Combined values, when present, pool the selected {run_count} runs within tasks before averaging tasks.",
        evaluation_note,
    ]
    export_table(comparison_dir, "external_simple_run_comparison_table", "External Simple Results Across Runs",
                 ["Run", "Method", "Complexity", "E2E", "PFS", "MFS@4"], comparison_rows,
                 tables_only, comparison_notes)
    if run_count == 1:
        return

    # 3. Show combined mean and run SD in the table, but bootstrap CI whiskers in the plot.
    combined_notes = [
        f"Simple tasks only: n={task_count} paired task clusters with {run_count} observed runs per method and one module per task/run. Repeated outcomes are not independent tasks.",
        "Entries are the combined estimate ± sample SD of run-level aggregates (ddof=1), not SE or CI; rate SDs correspond to percentage points.",
        f"Plot whiskers are pointwise 95% percentile CIs from {bootstrap_samples:,} paired task-cluster bootstrap samples within the single Simple stratum, retaining all observed repeats. The CIs condition on these repeats, not unobserved generation randomness.",
        f"Bootstrap uses an independent analysis RNG with seed {analysis_seed}, not an LLM generation seed. Zero-width empirical CIs do not imply certainty beyond these tasks/runs.",
        evaluation_note,
    ]
    combined_image_notes = [
        f"n={task_count} paired Simple tasks x {run_count} observed runs; one module per task/run. Entries: combined estimate ± sample run SD (ddof=1), not CI.",
        f"Plot whiskers: pointwise 95% task-cluster bootstrap CIs ({bootstrap_samples:,} samples), conditional on observed repeats. E2E includes build/compilation and startup.",
    ]
    combined_rows = [[DISPLAY_NAMES[approach], "Simple",
                      *[format_estimate_with_sd(metric, analysis.estimates[(approach, metric)])
                        for metric in QUALITY_METRICS]] for approach in EXTERNAL_APPROACHES]
    export_table(combined_dir, "external_simple_table", "External Comparison on Simple Tasks (Combined)",
                 ["Method", "Complexity", "E2E", "PFS", "MFS@4"], combined_rows,
                 tables_only, combined_notes, combined_image_notes)
    if not tables_only:
        save_external_effectiveness_plot(combined_dir / "external_simple_effectiveness",
                                          "External Comparison on Simple Tasks (Combined)",
                                          analysis.summary, run_count, analysis.estimates)

    # 4. Keep raw uncertainty and exact-test metadata separate from formatted display tables.
    estimate_rows = []
    for approach in EXTERNAL_APPROACHES:
        summary = analysis.summary[approach]
        for metric in QUALITY_METRICS:
            value = analysis.estimates[(approach, metric)]
            estimate_rows.append([
                approach, "Simple", metric, value.estimate, value.run_mean, value.run_sd, value.run_sd ** 2,
                value.ci_low, value.ci_high, value.ci_degenerate, summary.projects, run_count,
                summary.project_runs, summary.project_runs, summary.modules_at_4,
                bootstrap_samples, analysis_seed, units[metric],
            ])
    write_csv_table(combined_dir / "data" / "external_simple_metric_estimates.csv",
                    ["Approach", "Category", "Metric", "Estimate", "RunMean", "RunSD", "RunVariance",
                     "CILow", "CIHigh", "CIDegenerate", "Projects", "RunsPerProject", "ProjectRuns",
                     "ModuleRecords", "ModulesAtLeast4", "BootstrapSamples", "AnalysisSeed", "Unit"], estimate_rows)
    paired_raw_rows, paired_rows = [], []
    for value in analysis.comparisons:
        paired_raw_rows.append([
            "Incremental", value.comparator, "Simple", value.metric, value.difference, value.ci_low,
            value.ci_high, value.ci_degenerate, value.p_value, value.p_holm, value.projects,
            value.runs_per_project, value.project_runs, value.higher, value.equal, value.lower,
            2 ** value.projects, "exact_two_sided_task_label_swap", "external_simple_quality", 3,
            bootstrap_samples, analysis_seed, units[value.metric],
        ])
        scale = 100 if value.metric in {"E2E", "MFS4"} else 1
        precision = 2 if value.metric == "PFS" else 1
        metric_label = {"E2E": "E2E (pp)", "PFS": "PFS (points)", "MFS4": "MFS@4 (pp)"}[value.metric]
        interval = f"[{value.ci_low * scale:+.{precision}f}, {value.ci_high * scale:+.{precision}f}]"
        if value.ci_degenerate:
            interval += " *"
        paired_rows.append([metric_label, f"{value.difference * scale:+.{precision}f}", interval,
                            format_p_value(value.p_value), format_p_value(value.p_holm)])
    write_csv_table(combined_dir / "data" / "external_simple_paired_comparisons.csv",
                    ["Approach", "Comparator", "Category", "Metric", "Difference", "CILow", "CIHigh",
                     "CIDegenerate", "PValue", "PHolm", "Projects", "RunsPerProject", "ProjectRuns",
                     "ProjectsHigher", "ProjectsEqual", "ProjectsLower", "ExactPermutations", "TestMethod",
                     "Family", "FamilySize", "BootstrapSamples", "AnalysisSeed", "Unit"], paired_raw_rows)
    paired_notes = [
        f"All effects are Incremental minus MetaGPT on {task_count} matched Simple tasks averaged across {run_count} observed runs per method. Positive quality differences favor Incremental; pp denotes percentage points.",
        f"CIs are pointwise 95% percentile intervals from {bootstrap_samples:,} paired task-cluster bootstrap samples within the single Simple stratum. All repeats remain inside each sampled task; intervals condition on the observed repeats and are not simultaneous or Holm-adjusted.",
        f"Two-sided exact paired tests enumerate all {2 ** task_count:,} whole-task method-label swaps, assuming exchangeability under the null. The p-value is K/{2 ** task_count}, where K counts absolute permuted differences at least as large as the observed absolute difference; no Monte Carlo plus-one correction is used.",
        "Holm p adjusts the three external quality comparisons as a separate supplementary family, not jointly with the original eight comparisons. An unadjusted CI excluding zero need not imply Holm-adjusted significance.",
        f"Task clusters are treated as independent. Bootstrap RNG seed {analysis_seed} is for analysis, not generation. * Zero-width empirical CIs do not imply certainty beyond these tasks/runs.",
        evaluation_note,
    ]
    paired_image_notes = [
        f"Incremental minus MetaGPT; n={task_count} paired Simple tasks x {run_count} observed runs. Positive quality differences favor Incremental; pp denotes percentage points.",
        f"95% pointwise task-cluster bootstrap CIs; exact two-sided tests enumerate {2 ** task_count:,} task-level swaps (K/{2 ** task_count}, no plus-one correction). Holm p adjusts only these 3 external comparisons.",
        "CIs condition on observed repeats and are not Holm-adjusted. * Zero-width empirical CIs do not imply certainty.",
    ]
    export_table(combined_dir, "external_simple_paired_comparisons_table",
                 "External Simple Paired Differences (Incremental - MetaGPT)",
                 ["Metric", "Difference", "95% CI", "p", "Holm p"], paired_rows,
                 tables_only, paired_notes, paired_image_notes)
