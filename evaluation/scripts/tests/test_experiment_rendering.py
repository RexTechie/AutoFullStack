"""Verify publication, data, and preview routing without rendering real figures."""

from __future__ import annotations

import csv
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from evaluation.scripts import experiment_rendering as rendering
from evaluation.scripts import generate_experiment_artifacts as generator
from evaluation.scripts.experiment_external import analyze_external_results
from evaluation.scripts.experiment_statistics import aggregate_projects, compute_summary
from evaluation.scripts.tests.test_experiment_external import make_internal_results, make_results


class ArtifactRoutingTests(unittest.TestCase):
    """Keep paper-ready files separate from formatted previews and raw records."""

    def test_tables_only_routes_tex_and_formatted_previews_without_raw_csv(self):
        """Place formatted display CSV/Markdown in preview and only the LaTeX table in tables."""

        with TemporaryDirectory(prefix="artifact-routing-test-") as directory:
            scope = Path(directory) / "combined"
            rendering.export_table(scope, "display_table", "Display table", ["Method", "E2E"],
                                   [["Incremental", "92.2%"]], tables_only=True)
            self.assertTrue((scope / "tables" / "display_table.tex").is_file())
            self.assertTrue((scope / "preview" / "display_table.md").is_file())
            with (scope / "preview" / "display_table.csv").open(encoding="utf-8-sig", newline="") as handle:
                self.assertEqual(list(csv.reader(handle)), [["Method", "E2E"], ["Incremental", "92.2%"]])
            self.assertFalse((scope / "data").exists())
            self.assertFalse((scope / "figures").exists())
            self.assertFalse(list(scope.rglob("*.png")))
            self.assertFalse(list(scope.rglob("*.pdf")))
            self.assertFalse((scope / "display_table.tex").exists())

    def test_plot_save_routes_pdf_to_figures_and_png_to_preview(self):
        """Send scientific plot PDFs to figures and quick-view PNGs to preview."""

        figure, pyplot = Mock(), Mock()
        with TemporaryDirectory(prefix="artifact-routing-test-") as directory:
            scope = Path(directory) / "combined"
            with patch.object(rendering, "plt", pyplot):
                rendering.save_figure(figure, scope / "effectiveness_pfs")
            saved = {Path(call.args[0]) for call in figure.savefig.call_args_list}
            self.assertEqual(saved, {scope / "figures" / "effectiveness_pfs.pdf",
                                     scope / "preview" / "effectiveness_pfs.png"})
            figure.savefig.assert_any_call(scope / "preview" / "effectiveness_pfs.png", dpi=300, bbox_inches="tight")
            pyplot.close.assert_called_once_with(figure)

    def test_formatted_table_images_remain_previews_in_both_formats(self):
        """Do not put a rendered table image among the actual plot PDFs."""

        figure, axis, pyplot = Mock(), Mock(), Mock()
        pyplot.subplots.return_value = (figure, axis)
        axis.table.return_value.get_celld.return_value = {}
        with TemporaryDirectory(prefix="artifact-routing-test-") as directory:
            scope = Path(directory) / "combined"
            with patch.object(rendering, "plt", pyplot):
                rendering.export_table(scope, "display_table", "Display table", ["Method", "E2E"],
                                       [["Incremental", "92.2%"]], tables_only=False)
            saved = {Path(call.args[0]) for call in figure.savefig.call_args_list}
            self.assertEqual(saved, {scope / "preview" / "display_table.pdf",
                                     scope / "preview" / "display_table.png"})
            self.assertTrue((scope / "tables" / "display_table.tex").is_file())
            self.assertFalse((scope / "figures").exists())

    def test_internal_and_external_exports_do_not_overwrite_each_other(self):
        """Share a logical scope while keeping internal records and external-prefixed files distinct."""

        external = make_results()
        projects = aggregate_projects(make_internal_results(external))
        summary = compute_summary(projects)
        analysis = analyze_external_results(external, bootstrap_samples=100, seed=31)
        with TemporaryDirectory(prefix="artifact-routing-test-") as directory:
            root = Path(directory)
            combined = root / "combined"
            rendering.export_dataset(combined, "Combined", projects, summary,
                                     include_ablation_cost=False, tables_only=True, combined=True)
            internal_table = combined / "tables" / "main_result_table.tex"
            internal_records = combined / "data" / "project_metrics.csv"
            before = {path: path.read_bytes() for path in (internal_table, internal_records)}
            rendering.export_external_results(root, analysis, tables_only=True)
            for path, contents in before.items():
                self.assertEqual(path.read_bytes(), contents)
            self.assertTrue((combined / "tables" / "external_simple_table.tex").is_file())
            self.assertTrue((combined / "data" / "external_simple_metric_estimates.csv").is_file())
            self.assertTrue((combined / "data" / "external_simple_paired_comparisons.csv").is_file())
            self.assertTrue((root / "run_comparison" / "data" / "external_simple_project_runs.csv").is_file())
            self.assertFalse((root / "external_simple").exists())

    def test_entry_point_passes_shared_scope_paths_to_exporters(self):
        """Catch stale top-level directory arguments even when individual exporters pass."""

        external = make_results()
        internal = make_internal_results(external)
        analysis = analyze_external_results(external, bootstrap_samples=100, seed=31)
        with (
            TemporaryDirectory(prefix="artifact-routing-test-") as directory,
            patch("sys.argv", ["generate_experiment_artifacts.py", "--tables-only", "--output-dir", directory]),
            patch("builtins.print"),
            patch.object(generator, "load_project_results", side_effect=[
                [result for result in internal if result.run == run] for run in (1, 2, 3)
            ]),
            patch.object(generator, "load_external_results", return_value=external),
            patch.object(generator, "compute_repeated_statistics", return_value=({}, [])),
            patch.object(generator, "analyze_external_results", return_value=analysis),
            patch.object(generator, "export_dataset") as dataset_export,
            patch.object(generator, "export_statistical_results") as statistics_export,
            patch.object(generator, "export_run_comparison") as comparison_export,
            patch.object(generator, "export_external_results") as external_export,
        ):
            root = Path(directory)
            self.assertEqual(generator.main(), 0)
            self.assertEqual([call.args[0] for call in dataset_export.call_args_list], [
                root / "runs/run_1", root / "runs/run_2", root / "runs/run_3", root / "combined",
            ])
            self.assertEqual(statistics_export.call_args.args[0], root / "combined")
            self.assertEqual(comparison_export.call_args.args[0], root)
            self.assertEqual(external_export.call_args.args[0], root)


if __name__ == "__main__":
    unittest.main()
