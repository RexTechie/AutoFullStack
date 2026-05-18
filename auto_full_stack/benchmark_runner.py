#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/3/7
@Author  : Rex
@File    : benchmark_runner.py

Automated benchmark script to evaluate Incremental, Incremental-NoSelfRefinement,
and Waterfall variants.
This script extracts metrics (ER, MSR, LoC, Time, Token) into an output CSV.
Crucially, it skips the blocking `operations_workflow` to allow unattended
batch processing.
"""
import json
import time
import os
import csv
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to sys.path so 'auto_full_stack' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auto_full_stack.common.const import ROOT
from auto_full_stack.common.log import logger

# Import specific nodes instead of compiled graphs to construct customized, non-blocking pipelines
from auto_full_stack.workflows.incremental_main_workflow import (
    MainState,
    init_workspace,
    planning_workflow_node,
    development_workflow_node,
)
from auto_full_stack.workflows.incremental_no_self_refinement_main_workflow import (
    incremental_no_self_refinement_development_workflow_node,
)
from auto_full_stack.workflows.waterfall_main_workflow import waterfall_development_workflow_node

PROJECT_ROOT = ROOT.parent

DATASET_FILES = {
    "simple": PROJECT_ROOT / "data" / "simple_dataset.json",
    "medium": PROJECT_ROOT / "data" / "medium_dataset.json",
    "complex": PROJECT_ROOT / "data" / "complex_dataset.json",
}

APPROACH_LABELS = {
    "incremental": "Incremental",
    "incremental_no_self_refinement": "Incremental-NoSelfRefinement",
    "waterfall": "Waterfall",
}

RESULTS_DIR = PROJECT_ROOT / "experiment_results"

def load_benchmark_data(complexity):
    all_projects = []
    file_path = DATASET_FILES[complexity]
    category = file_path.stem.split('_')[0].capitalize()  # Simple, Medium, Complex
    if not os.path.exists(file_path):
        logger.warning(f"Benchmark file not found: {file_path}")
        return all_projects
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for idx, item in enumerate(data):
            proj_id = f"proj_{category.lower()}_{idx+1:02d}"
            all_projects.append({
                "id": proj_id,
                "name": item.get("project_name", f"Untitled_{proj_id}"),
                "description": item.get("project_description", ""),
                "category": category
            })
    return all_projects


def build_workspace_root(workspace_base: Path, approach_key: str, category: str) -> Path:
    return workspace_base / approach_key / category.lower()


def extract_metrics(dev_state, approach):
    """ Extract generic metrics from the Development State """
    metrics = {
        "status": "Success",
        "time_elapsed": round(dev_state.get("time_elapsed", 0), 2),
        "total_tokens": dev_state.get("total_tokens", 0),
        "frontend_lines": dev_state.get("frontend_code_lines", 0),
        "backend_lines": dev_state.get("backend_code_lines", 0),
        "total_lines": dev_state.get("frontend_code_lines", 0) + dev_state.get("backend_code_lines", 0)
    }

    if approach == "Waterfall":
        metrics["global_attempts"] = dev_state.get("attempt", 0)
        # We modified waterfall state to explicitly emit "is_pass", so refer to it directly instead of a heuristic
        metrics["compile_pass_heuristic"] = dev_state.get("is_pass", False)
        metrics["module_success_data"] = "N/A (Waterfall)"
    else:
        # Incremental / Incremental-NoSelfRefinement specific parsing
        module_attempts = dev_state.get("module_attempts", {})
        total_modules = len(module_attempts)
        passed_modules = sum(1 for m in module_attempts.values() if m.get("is_pass", False))
        
        metrics["global_attempts"] = "N/A (Incremental)"
        metrics["compile_pass_heuristic"] = total_modules > 0 and passed_modules == total_modules
        metrics["module_success_data"] = f"{passed_modules}/{total_modules}"
        
        # Calculate avg retries
        if total_modules > 0:
            avg_retry = sum(m.get("attempts", 0) for m in module_attempts.values()) / total_modules
            metrics["avg_module_retry"] = round(avg_retry, 2)
        else:
            metrics["avg_module_retry"] = 0.0

    return metrics


def run_single_experiment(proj_data, approach_key, workspace_base):
    """ Run a single PRD through one of the workflows (Truncated version) """
    approach = APPROACH_LABELS[approach_key]
    workspace_root = build_workspace_root(workspace_base, approach_key, proj_data["category"])
    logger.info(f"\n{'='*50}\nStarting Experiment: {proj_data['id']} | Category: {proj_data['category']} | Approach: {approach}\n{'='*50}")

    state = MainState(
        project_id=f"{proj_data['id']}_{approach_key}",
        project_name=proj_data["name"],
        project_description=proj_data["description"],
        project_namespace="",
        workspace_root=str(workspace_root),
    )

    try:
        start_time = time.time()
        # 1. Init (Creates namespace and dirs)
        # init_workspace only returns the updated keys (project_namespace), so we must update the dict
        init_result = init_workspace(state)
        state.update(init_result)
        
        # 2. Planning
        planning_state = planning_workflow_node(state)
        
        # 3. Development (Generates code AND tests it)
        if approach == "Waterfall":
            dev_state = waterfall_development_workflow_node(planning_state)
        elif approach == "Incremental-NoSelfRefinement":
            dev_state = incremental_no_self_refinement_development_workflow_node(planning_state)
        else:
            dev_state = development_workflow_node(planning_state)

        end_time = time.time()
        
        # 4. Extract Results (SKIP Operations workflow)
        metrics = extract_metrics(dev_state, approach)
        metrics["error_msg"] = ""
        # Override with exact total time and combined tokens
        metrics["time_elapsed"] = round(end_time - start_time, 2)
        metrics["total_tokens"] = planning_state.get("total_tokens", 0) + dev_state.get("total_tokens", 0)

    except Exception as e:
        logger.error(f"Experiment {proj_data['id']} ({approach}) FAILED: {str(e)}")
        metrics = {
            "status": "Failed",
            "error_msg": str(e).split('\n')[0][:100],  # Short error
            "time_elapsed": 0, "total_tokens": 0, "total_lines": 0,
            "compile_pass_heuristic": False, "module_success_data": "", "avg_module_retry": 0
        }

    # Flatten for CSV
    result_row = {
        "ProjectID": proj_data["id"],
        "Category": proj_data["category"],
        "Approach": approach,
        "Namespace": state.get("project_namespace", ""),
        "Status": metrics.get("status"),
        "CompilePassHeuristic": metrics.get("compile_pass_heuristic"),
        "ModuleSuccess": metrics.get("module_success_data", ""),
        "AvgModuleRetry_or_GlobalAttempts": metrics.get("avg_module_retry", metrics.get("global_attempts", "")),
        "TotalTokens": metrics.get("total_tokens"),
        "TimeElapsed(s)": metrics.get("time_elapsed"),
        "TotalLines": metrics.get("total_lines"),
        "ErrorMsg": metrics.get("error_msg")
    }
    return result_row


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run AutoFullStack Benchmarks")
    parser.add_argument(
        "--approach",
        choices=["incremental", "incremental_no_self_refinement", "waterfall", "all"],
        default="all",
        help="Which approach to run",
    )
    parser.add_argument(
        "--complexity",
        choices=["simple", "medium", "complex", "all"],
        default="all",
        help="Which benchmark complexity to run",
    )
    parser.add_argument(
        "--workspace-base",
        type=Path,
        default=PROJECT_ROOT / "experiments",
        help="Base directory for generated benchmark projects",
    )
    parser.add_argument("--limit", type=int, default=0, help="Limit the number of projects to run (0 means all)")
    parser.add_argument("--project-id", type=str, default=None, help="Run only the project with this specific ID (e.g., proj_complex_02). Overrides --limit.")
    args = parser.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = RESULTS_DIR / f"benchmark_results_{args.approach}_{args.complexity}_{timestamp}.csv"

    approach_keys = list(APPROACH_LABELS.keys()) if args.approach == "all" else [args.approach]
    complexity_keys = list(DATASET_FILES.keys()) if args.complexity == "all" else [args.complexity]

    fieldnames = [
        "ProjectID", "Category", "Approach", "WorkspaceRoot", "ProjectPath", "Namespace", "Status", "CompilePassHeuristic",
        "ModuleSuccess", "AvgModuleRetry_or_GlobalAttempts", 
        "TotalTokens", "TimeElapsed(s)", "TotalLines", "ErrorMsg"
    ]

    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        
        has_project = False
        for approach_key in approach_keys:
            for complexity in complexity_keys:
                projects = load_benchmark_data(complexity)

                if args.project_id:
                    projects = [p for p in projects if p["id"] == args.project_id]
                elif args.limit > 0:
                    projects = projects[:args.limit]

                if not projects:
                    continue

                has_project = True
                logger.info(
                    f"Loaded {len(projects)} {complexity} benchmark projects. "
                    f"Starting tests for approach: {APPROACH_LABELS[approach_key]}"
                )

                for proj in projects:
                    res = run_single_experiment(proj, approach_key=approach_key, workspace_base=args.workspace_base)
                    writer.writerow(res)
                    csv_file.flush()
                    time.sleep(2)

        if not has_project:
            if args.project_id:
                logger.error(f"Project ID '{args.project_id}' not found in benchmark data. Aborting.")
            else:
                logger.error("No PRDs found in data directory. Aborting.")
            return

    logger.info(f"Benchmarks completed. Results written to: {csv_filename}")
    logger.info("NOTE: For 'Executability Rate' verification, please run 'operations_workflow' manually on corresponding namespaces.")

if __name__ == "__main__":
    main()
