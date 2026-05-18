#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/6/16 10:04
@Author  : Rex
@File    : incremental_main_workflow.py
"""
import json
import time
from typing import TypedDict

from langchain_core.output_parsers import StrOutputParser
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from typing_extensions import NotRequired

from auto_full_stack.common.llm import model, get_token_stats
from auto_full_stack.common.log import logger
from auto_full_stack.common.workspace import get_workspace_root
from auto_full_stack.utils import FileUtil, PromptUtil
from auto_full_stack.utils.redis_util import RedisUtil
from auto_full_stack.workflows.incremental_development_workflow import (
    incremental_development_workflow,
    DevelopmentState,
)
from auto_full_stack.workflows.planning_workflow import planning_workflow, PlanningState
from auto_full_stack.workflows.operations_workflow import operations_workflow, OperationsState


class MainState(TypedDict):
    project_id: str
    project_name: str
    project_description: str
    project_namespace: str
    workspace_root: NotRequired[str]

def init_workspace(state: MainState):
    """
    Generate project namespace
    """
    project_id = state["project_id"]
    project_name = state["project_name"]

    # Generate project namespace
    chain = model | StrOutputParser()
    prompt = PromptUtil.prompt_handle("project_namespace.templ", {
        "project_name": project_name
    })
    project_namespace = chain.invoke(prompt)

    logger.info(f"Project namespace: {project_namespace}")

    # Create project directory
    project_path = get_workspace_root(state) / project_namespace
    FileUtil.create_dir(project_path)
    FileUtil.create_dir(project_path / "docs")
    FileUtil.create_dir(project_path / "resources")

    # Store id and project_namespace mapping
    RedisUtil.hset("fullstackagentflow_namespace", project_id, project_namespace)

    # Update state
    return {
        "project_namespace": project_namespace,
    }

def planning_workflow_node(state: MainState) -> PlanningState:
    """
    Planning Stage Node
    """

    project_id = state["project_id"]
    project_namespace = state["project_namespace"]
    planning_state = PlanningState(
        project_id=project_id,
        project_name=state["project_name"],
        project_description=state["project_description"],
        project_namespace=project_namespace,
        workspace_root=state.get("workspace_root"),
        product_requirement=None,
        architecture_diagram=None,
        class_diagram=None,
        inc_class_dict=None,
        incremental_list=None,
    )
    # Store project status in Redis
    RedisUtil.hset("fullstackagentflow_status", project_id, "Planning")

    start_time = time.time()
    token_stats = get_token_stats()
    start_input_tokens = token_stats["total_input_tokens"]
    start_output_tokens = token_stats["total_output_tokens"]
    start_tokens = token_stats["total_tokens"]

    planning_state = planning_workflow.invoke(planning_state)

    end_time = time.time()
    token_stats = get_token_stats()
    end_input_tokens = token_stats["total_input_tokens"]
    end_output_tokens = token_stats["total_output_tokens"]
    end_tokens = token_stats["total_tokens"]

    # Record the time spent and the tokens spent
    planning_state["time_elapsed"] = end_time - start_time
    planning_state["input_token"] = end_input_tokens - start_input_tokens
    planning_state["output_token"] = end_output_tokens - start_output_tokens
    planning_state["total_tokens"] = end_tokens - start_tokens

    project_namespace = planning_state["project_namespace"]
    file_path = get_workspace_root(planning_state) / project_namespace / "resources" / "planning_state.json"
    FileUtil.write_file(file_path, json.dumps(planning_state, indent=4, ensure_ascii=False))

    return planning_state


def development_workflow_node(state: PlanningState) -> DevelopmentState:
    """
    Coding Stage Node
    """
    project_id = state["project_id"]
    development_state = DevelopmentState(
        project_id=project_id,
        project_name=state["project_name"],
        project_description=state["project_description"],
        project_namespace=state["project_namespace"],
        workspace_root=state.get("workspace_root"),
        product_requirement=state["product_requirement"],
        architecture_diagram=state["architecture_diagram"],
        incremental_list=state["incremental_list"],
        class_diagram=state["class_diagram"],
        inc_class_dict=state["inc_class_dict"],
        current_incremental_index=1,
        current_incremental=None,
        current_class_diagram=None
    )

    # Store project status in Redis
    RedisUtil.hset("fullstackagentflow_status", project_id, "Coding")

    start_time = time.time()
    token_stats = get_token_stats()
    start_input_tokens = token_stats["total_input_tokens"]
    start_output_tokens = token_stats["total_output_tokens"]
    start_tokens = token_stats["total_tokens"]

    development_state = incremental_development_workflow.invoke(development_state)

    # Summarize code lines and attempts
    frontend_code_lines = development_state.get("frontend_code_lines", 0)
    backend_code_lines = development_state.get("backend_code_lines", 0)
    module_attempts = development_state.get("module_attempts", {})
    logger.info("💡 Total code lines - Frontend: {}, Backend: {}, Total: {}".format(frontend_code_lines, backend_code_lines, frontend_code_lines + backend_code_lines))
    logger.info(f"💡 Module Attempts (Refinement): {json.dumps(module_attempts)}")

    # Record the time spent and the tokens spent
    end_time = time.time()
    token_stats = get_token_stats()
    end_input_tokens = token_stats["total_input_tokens"]
    end_output_tokens = token_stats["total_output_tokens"]
    end_tokens = token_stats["total_tokens"]

    development_state["time_elapsed"] = end_time - start_time
    development_state["input_token"] = end_input_tokens - start_input_tokens
    development_state["output_token"] = end_output_tokens - start_output_tokens
    development_state["total_tokens"] = end_tokens - start_tokens

    project_namespace = development_state["project_namespace"]
    file_path = get_workspace_root(development_state) / project_namespace / "resources" / "development_state.json"
    logger.info("💡 Total token usage - Input: {}, Output: {}, Total: {}".format(end_input_tokens, end_output_tokens, end_tokens))
    FileUtil.write_file(file_path, json.dumps(development_state, indent=4, ensure_ascii=False))

    # Store id and project_namespace mapping
    project_namespace = development_state["project_namespace"]
    RedisUtil.hset("fullstackagentflow_namespace", project_id, project_namespace)
    return development_state


def operations_workflow_node(state: DevelopmentState) -> OperationsState:
    """
    Running Stage Node
    """
    project_id = state["project_id"]
    operations_state = OperationsState(
        project_id=project_id,
        project_namespace=state["project_namespace"],
        workspace_root=state.get("workspace_root"),
        reset_database=False
    )
    # Store project status in Redis
    RedisUtil.hset("fullstackagentflow_status", project_id, "Running")

    operations_state  = operations_workflow.invoke(operations_state)

    # Store id and project_namespace mapping
    project_namespace = operations_state["project_namespace"]
    RedisUtil.hset("fullstackagentflow_namespace", project_id, project_namespace)

    return operations_state


main_graph = StateGraph(MainState)
main_graph.add_node("init", init_workspace)
main_graph.add_node("planning", planning_workflow_node)
main_graph.add_node("development", development_workflow_node)
main_graph.add_node("operations", operations_workflow_node)

main_graph.add_edge(START, "init")
main_graph.add_edge("init", "planning")
main_graph.add_edge("planning", "development")
main_graph.add_edge("development", "operations")
main_graph.add_edge("operations", END)
incremental_main_workflow = main_graph.compile(checkpointer=MemorySaver())
main_workflow = incremental_main_workflow

# 打印工作流的状态图
logger.debug(f"Main Workflow: \n{incremental_main_workflow.get_graph().draw_ascii()}")
