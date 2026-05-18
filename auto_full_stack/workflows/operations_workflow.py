#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/6/16 19:37
@Author  : Rex
@File    : operations_workflow.py
"""
from langgraph.graph import StateGraph, START, END
from typing_extensions import NotRequired, TypedDict

from auto_full_stack.common.log import logger
from auto_full_stack.common.workspace import get_workspace_root
from auto_full_stack.utils import FileUtil
from auto_full_stack.utils.redis_util import RedisUtil
from auto_full_stack.workflows.agent.operations_engineer import OperationsEngineer

operations_engineer = OperationsEngineer()

class OperationsState(TypedDict):
    project_id: str
    project_namespace: str  # Project Namespace
    workspace_root: NotRequired[str]
    reset_database: bool

def init_database(state: OperationsState) -> OperationsState:
    project_namespace = state["project_namespace"]
    reset_database = state["reset_database"]
    workspace_root = get_workspace_root(state)

    if reset_database:
        logger.info("Initializing database...")
        operations_engineer.init_database(project_namespace, workspace_root=workspace_root)

    return state



def deploy_frontend(state: OperationsState) -> OperationsState:
    project_namespace = state["project_namespace"]
    project_id = state["project_id"]
    workspace_root = get_workspace_root(state)

    log_path = workspace_root / project_namespace / "logs" / f"{project_namespace}_frontend.log"

    # 1. Install frontend dependencies
    logger.info("Installing frontend dependencies...")
    install_dependencies_cmd, install_dependencies_process = operations_engineer.frontend_install_dependencies(
        project_namespace,
        workspace_root=workspace_root,
    )
    # Get PID, store in Redis
    RedisUtil.hset("fullstackagentflow_front_pid", project_id, install_dependencies_process.pid)
    try:
        while install_dependencies_process.poll() is None:
            line = install_dependencies_process.stdout.readline()
            if line:
                line = line.decode('utf-8', errors='replace').strip()
                FileUtil.append_file(log_path, line + "\n")
    except Exception as e:
        install_dependencies_process.terminate()

    # 2. Run frontend project
    logger.info("Running frontend project...")
    run_frontend_cmd, run_frontend_process = operations_engineer.run_frontend(
        project_namespace,
        workspace_root=workspace_root,
    )
    # Get PID, store in Redis
    RedisUtil.hset("fullstackagentflow_front_pid", project_id, run_frontend_process.pid)
    try:
        while run_frontend_process.poll() is None:
            line = run_frontend_process.stdout.readline()
            if line:
                line = line.decode('utf-8', errors='replace').strip()
                FileUtil.append_file(log_path, line + "\n")
    except Exception as e:
        run_frontend_process.terminate()

def deploy_backend(state: OperationsState) -> OperationsState:
    project_namespace = state["project_namespace"]
    project_id = state["project_id"]
    workspace_root = get_workspace_root(state)

    log_path = workspace_root / project_namespace / "logs" / f"{project_namespace}_backend.log"

    # 1. Build backend project
    logger.info("Building backend project...")
    operations_engineer.test_backend_project(project_namespace, workspace_root=workspace_root)
    build_cmd, build_process = operations_engineer.build_backend_project(project_namespace, workspace_root=workspace_root)
    # Get PID, store in Redis
    RedisUtil.hset("fullstackagentflow_backend_pid", project_id, build_process.pid)
    try:
        while build_process.poll() is None:
            line = build_process.stdout.readline()
            if line:
                line = line.decode('utf-8', errors='replace').strip()
                FileUtil.append_file(log_path, line + "\n")
    except Exception as e:
        build_process.terminate()

    # 2. Run backend project
    logger.info("Running backend project...")
    run_cmd, run_process = operations_engineer.run_backend_project(project_namespace, workspace_root=workspace_root)

    # Get PID, store in Redis
    RedisUtil.hset("fullstackagentflow_backend_pid", project_id, run_process.pid)
    try:
        while run_process.poll() is None:
            line = run_process.stdout.readline()
            if line:
                line = line.decode('utf-8', errors='replace').strip()
                FileUtil.append_file(log_path, line + "\n")

    except Exception as e:
        run_process.terminate()

operations_graph = StateGraph(OperationsState)
operations_graph.add_node("init_database", init_database)
operations_graph.add_node("deploy_frontend", deploy_frontend)
operations_graph.add_node("deploy_backend", deploy_backend)

operations_graph.add_edge(START, "init_database")
operations_graph.add_edge("init_database", "deploy_frontend")
operations_graph.add_edge("init_database", "deploy_backend")
operations_graph.add_edge("deploy_frontend", END)
operations_graph.add_edge("deploy_backend", END)

operations_workflow = operations_graph.compile()
#
# # 打印工作流的状态图
logger.debug(f"Operations Workflow: \n{operations_workflow.get_graph().draw_ascii()}")
