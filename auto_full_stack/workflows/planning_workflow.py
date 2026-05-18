#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/6/4 19:41
@Author  : Rex
@File    : planning_workflow.py.py
"""
import json
from typing import TypedDict

from typing_extensions import NotRequired

from langgraph.graph import StateGraph, START, END

from auto_full_stack.workflows.agent.product_manager import ProductManager
from auto_full_stack.workflows.agent.software_architect import SoftwareArchitect
from auto_full_stack.common.workspace import get_workspace_root
from auto_full_stack.common.log import logger
from auto_full_stack.utils import PromptUtil, FileUtil

product_manager = ProductManager()
software_architect = SoftwareArchitect()

class PlanningState(TypedDict):
    """
    Planning State
    """
    project_id: str
    project_name: str
    project_description: str
    project_namespace: str  | None
    workspace_root: NotRequired[str]
    product_requirement: str | None
    architecture_diagram: str | None
    incremental_list: list | None
    class_diagram: str | None
    inc_class_dict: dict | None


def analyze_requirement(state: PlanningState):
    """
    Project manager analyzes requirements and writes PRD
    """
    project_name = state["project_name"]
    project_description = state["project_description"]
    project_namespace = state["project_namespace"]

    docs = get_workspace_root(state) / project_namespace / "docs"

    # analyze requirement and write PRD
    prd = product_manager.write_prd(project_name, project_description)

    FileUtil.write_file(
        file_path=docs / "product_requirement.md",
        content=prd)

    # modify state
    return {
        "product_requirement": prd,
    }

def analyze_architecture(state: PlanningState):
    """
    Architect analyzes architecture and writes diagrams
    """
    product_requirement = state["product_requirement"]
    project_namespace = state["project_namespace"]
    resources_path = get_workspace_root(state) / project_namespace / "resources"

    # draw architecture diagram
    architecture_diagram = software_architect.draw_architecture_diagram(
        product_requirement=product_requirement,
    )
    FileUtil.write_file(resources_path / "architecture_diagram.mmd", architecture_diagram)

    # write incremental list
    incremental_list = software_architect.write_incremental_list(
        product_requirement=product_requirement,
        architect_diagram=architecture_diagram
    )
    FileUtil.write_file(resources_path / "incremental_list.json", json.dumps(incremental_list, indent=4, ensure_ascii=False))

    # draw class diagram
    class_diagram = software_architect.draw_class_diagram(
        product_requirement=product_requirement,
        architect_diagram=architecture_diagram
    )
    FileUtil.write_file(resources_path / "class_diagram.mmd", class_diagram)

    # write incremental class diagram match
    inc_class_dict = software_architect.incremental_class_diagram_match(
        incremental_list=incremental_list,
        class_diagram=class_diagram
    )
    FileUtil.write_file(resources_path / "incremental_class_diagram_match.json", json.dumps(inc_class_dict, indent=4))

    return {
        "architecture_diagram": architecture_diagram,
        "incremental_list": incremental_list,
        "class_diagram": class_diagram,
        "inc_class_dict": inc_class_dict,
    }

# Planning workflow
planning_graph = StateGraph(PlanningState)

planning_graph.add_node("analyze_requirement", analyze_requirement)
planning_graph.add_node("analyze_architecture", analyze_architecture)

planning_graph.add_edge(START, "analyze_requirement")
planning_graph.add_edge("analyze_requirement", "analyze_architecture")
planning_graph.add_edge("analyze_architecture", END)
planning_workflow = planning_graph.compile()

# Print the state graph of the workflow
logger.debug(f"Planning Workflow: \n{planning_workflow.get_graph().draw_ascii()}")
