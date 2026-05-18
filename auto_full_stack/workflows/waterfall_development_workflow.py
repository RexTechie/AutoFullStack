#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/3/7
@Author  : Rex
@File    : waterfall_development_workflow.py
"""
import json
import platform
import subprocess
from random import Random
from string import Template
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from typing_extensions import NotRequired

from auto_full_stack.common.log import logger
from auto_full_stack.workflows.agent.backend_developer import BackendDeveloper
from auto_full_stack.workflows.agent.frontend_developer import FrontendDeveloper
from auto_full_stack.common.const import ROOT, MAX_ITERATIONS
from auto_full_stack.common.workspace import get_workspace_root
from auto_full_stack.utils import FileUtil, NameRuleConverter, MavenTestResultUtil
from auto_full_stack.utils.mysql_util import MySQLUtil

# Template path
TEMPLATE_PATH = ROOT / "templates"

# Frontend settings
FRONTEND_SETTING_THEME = ['#409EFF', '#1890FF', '#212121', '#11A983', '#13C2C2', '#6959CD']
FRONTEND_SETTING_THEME_SIDE = ['theme-dark', 'theme-light']
FRONTEND_SETTING_TOP_NAV = ['True', False]

frontend_developer = FrontendDeveloper()
backend_developer = BackendDeveloper()


def __config_backend_project(project_name: str, namespace: str, workspace_root):
    """
    Configure backend project files: application.yml.templ, application-druid.yml.templ
    """
    application_yml = FileUtil.read_file(TEMPLATE_PATH / "config_template" / "application.yml.templ")
    application_druid_yml = FileUtil.read_file(TEMPLATE_PATH / "config_template" / "application-druid.yml.templ")
    logback_xml = FileUtil.read_file(TEMPLATE_PATH / "config_template" / "logback.xml.templ")

    application_yml = Template(application_yml).substitute({
        "name": namespace + "_backend",
        "profile": f"D:/app/{namespace}/uploadPath" if platform.system().lower() == "windows" else f"~/app/{namespace}/uploadPath",
    })
    application_druid_yml = Template(application_druid_yml).substitute({
        "database": namespace
    })
    logback_xml = logback_xml.replace("@log_path@", f"D:/app/{namespace}/logs" if platform.system().lower() == "windows" else f"~/app/{namespace}/logs")

    FileUtil.write_file(workspace_root / namespace / "backend" / "admin" / "src" / "main" / "resources" / "application.yml", application_yml)
    FileUtil.write_file(workspace_root / namespace / "backend" / "admin" / "src" / "main" / "resources" / "application-druid.yml", application_druid_yml)
    FileUtil.write_file(workspace_root / namespace / "backend" / "admin" / "src" / "main" / "resources" / "logback.xml", logback_xml)


def __config_frontend_project(project_name: str, namespace: str, workspace_root):
    development_env = FileUtil.read_file(TEMPLATE_PATH / "config_template" / ".env.development.templ")
    production_env = FileUtil.read_file(TEMPLATE_PATH / "config_template" / ".env.production.templ")
    staging_env = FileUtil.read_file(TEMPLATE_PATH / "config_template" / ".env.staging.templ")
    package_json = FileUtil.read_file(TEMPLATE_PATH / "config_template" / "package.json.templ")
    setting_js = FileUtil.read_file(TEMPLATE_PATH / "config_template" / "settings.js.templ")

    development_env = Template(development_env).substitute({"VUE_APP_TITLE": project_name})
    production_env = Template(production_env).substitute({"VUE_APP_TITLE": project_name})
    staging_env = Template(staging_env).substitute({"VUE_APP_TITLE": project_name})
    package_json = Template(package_json).substitute({
        "name": namespace + "_frontend",
        "description": project_name
    })
    setting_js = Template(setting_js).substitute({
        "theme": Random().choice(FRONTEND_SETTING_THEME),
        "sideTheme": Random().choice(FRONTEND_SETTING_THEME_SIDE),
        "topNav": str(Random().choice(FRONTEND_SETTING_TOP_NAV)).lower()
    })

    FileUtil.write_file(workspace_root / namespace / "frontend" / ".env.development", development_env)
    FileUtil.write_file(workspace_root / namespace / "frontend" / ".env.production", production_env)
    FileUtil.write_file(workspace_root / namespace / "frontend" / ".env.staging", staging_env)
    FileUtil.write_file(workspace_root / namespace / "frontend" / "package.json", package_json)
    FileUtil.write_file(workspace_root / namespace / "frontend" / "src" / "settings.js", setting_js)


class WaterfallDevelopmentState(TypedDict):
    project_id: str
    project_name: str
    project_description: str
    project_namespace: str
    workspace_root: NotRequired[str]
    product_requirement: str
    architecture_diagram: str
    incremental_list: list
    class_diagram: str
    inc_class_dict: dict
    frontend_code_lines: int
    backend_code_lines: int
    attempt: int
    is_pass: bool
    

def __remove_generated_waterfall_code(namespace: str, incremental_list: list, workspace_root):
    """
    Remove all generated backend and frontend code files for all modules in the waterfall pass.
    """
    for incremental in incremental_list:
        module_name = incremental.get("module_name")
        if not module_name:
            continue

        # 0. Clear database data
        snake_name = NameRuleConverter.to_snake_case(module_name)
        drop_table_sql = f"DROP TABLE IF EXISTS tb_{snake_name}"
        delete_menu_sql = f"DELETE FROM sys_menu WHERE component LIKE 'business/{snake_name}/%%' OR perms LIKE 'business:{snake_name}:%%'"
        try:
            MySQLUtil.execute_sql_script(sql_script=drop_table_sql, database=namespace)
            MySQLUtil.execute_sql_script(sql_script=delete_menu_sql, database=namespace)
            logger.info(f"[{module_name} Module]: Removed database table and sys_menu data for rollback.")
        except Exception as e:
            logger.error(f"[{module_name} Module]: Failed to remove database data during rollback: {e}")
            
        # 1. Remove Backend Code
        FileUtil.remove_file(
            file_path=workspace_root / namespace / "backend" / "business" / "src" / "main" / "java" / "com" / "demo" / "business" / "domain" / f"{module_name}.java")
        FileUtil.remove_file(
            file_path=workspace_root / namespace / "backend" / "business" / "src" / "main" / "resources" / "mapper" / "business" / f"{module_name}Mapper.xml")
        FileUtil.remove_file(
            file_path=workspace_root / namespace / "backend" / "business" / "src" / "main" / "java" / "com" / "demo" / "business" / "mapper" / f"{module_name}Mapper.java")
        FileUtil.remove_file(
            file_path=workspace_root / namespace / "backend" / "business" / "src" / "main" / "java" / "com" / "demo" / "business" / "service" / "impl" / f"{module_name}ServiceImpl.java")
        FileUtil.remove_file(
            file_path=workspace_root / namespace / "backend" / "business" / "src" / "main" / "java" / "com" / "demo" / "business" / "service" / f"I{module_name}Service.java")
        FileUtil.remove_file(
            file_path=workspace_root / namespace / "backend" / "business" / "src" / "main" / "java" / "com" / "demo" / "business" / "controller" / f"{module_name}Controller.java")
        FileUtil.remove_file(
            file_path=workspace_root / namespace / "backend" / "admin" / "src" / "test" / "java" / "com" / "demo" / "business" / "service" / f"{module_name}ServiceTest.java")

        # 2. Remove Frontend Code
        snake_case_name = NameRuleConverter.to_snake_case(module_name)
        FileUtil.remove_file(
            file_path=workspace_root / namespace / "frontend" / "src" / "api" / "business" / f"{snake_case_name}.js")
        page_dir = workspace_root / namespace / "frontend" / "src" / "views" / "business" / snake_case_name
        FileUtil.remove_dir(page_dir)
        
    logger.info("[Waterfall] All generated code files have been removed for retry.")


def init_proj(state: WaterfallDevelopmentState):
    """
    Initialize the project by creating the necessary directory structure and files.
    Same as incremental version - project scaffold is identical.
    """
    namespace = state['project_namespace']
    project_name = state['project_name']
    workspace_root = get_workspace_root(state)

    # 1. Create project directory
    project_path = workspace_root / namespace
    FileUtil.create_dir(project_path)
    # 2. Copy template files to project directory
    FileUtil.copy_all_files(TEMPLATE_PATH / "full_stack_template", project_path)
    sql_path = project_path / "sql"
    # 3. Execute SQL scripts to create database and tables
    MySQLUtil.drop_database(database=namespace)
    MySQLUtil.create_database(database=namespace)
    MySQLUtil.execute_sql_by_file(
        script_path=sql_path / "quartz.sql",
        database=namespace
    )
    MySQLUtil.execute_sql_by_file(
        script_path=sql_path / "init.sql",
        database=namespace
    )
    # 4. Modify project config files
    __config_backend_project(project_name=project_name, namespace=namespace, workspace_root=workspace_root)
    __config_frontend_project(project_name=project_name, namespace=namespace, workspace_root=workspace_root)

    attempt = state.get("attempt", 0)

    return {
        "frontend_code_lines": 0,
        "backend_code_lines": 0,
        "attempt": attempt,
        "is_pass": False
    }


def waterfall_backend_dev(state: WaterfallDevelopmentState):
    """
    Waterfall backend development: generate ALL modules' backend code in one pass.
    No intermediate unit tests, no self-refinement/rollback.
    """
    incremental_list = state["incremental_list"]
    inc_class_dict = state["inc_class_dict"]
    namespace = state["project_namespace"]
    workspace_root = get_workspace_root(state)
    backend_code_lines = 0

    for incremental in incremental_list:
        module_name = incremental.get("module_name")
        if module_name is None or module_name == "":
            continue

        incremental_id = incremental["id"]
        current_class_diagram = inc_class_dict.get(incremental_id) or inc_class_dict.get(str(incremental_id))
        if current_class_diagram is None:
            logger.warning(f"[Waterfall] No class diagram found for incremental {incremental_id}, skipping.")
            continue

        current_incremental_code_lines = 0
        logger.info(f"[Waterfall Backend] Generating module: {module_name}")

        # 1. Create tables
        create_tables_sql = backend_developer.write_create_tables_sql(
            incremental=incremental,
            class_diagram=current_class_diagram
        )
        FileUtil.write_file(
            file_path=workspace_root / namespace / "sql" / f"create_tables_inc_{module_name}.sql",
            content=create_tables_sql)
        MySQLUtil.execute_sql_script(
            sql_script=create_tables_sql,
            database=namespace
        )

        # 2. Insert menu
        menu_info = {
            "name": module_name,
            "path": NameRuleConverter.to_snake_case(module_name),
        }
        insert_menu_info = backend_developer.write_insert_menu_sql(menu_info=menu_info)
        FileUtil.write_file(
            file_path=workspace_root / namespace / "sql" / f"insert_menu_inc_{module_name}.sql",
            content=insert_menu_info)
        MySQLUtil.execute_sql_script(
            sql_script=insert_menu_info,
            database=namespace
        )

        # 3. Generate domain code
        domain_code = backend_developer.write_domain_code(
            module_name=module_name,
            create_table_sql=create_tables_sql
        )
        current_incremental_code_lines += len(domain_code.splitlines())
        FileUtil.write_file(
            file_path=workspace_root / namespace / "backend" / "business" / "src" / "main" / "java" / "com" / "demo" / "business" / "domain" / f"{module_name}.java",
            content=domain_code
        )

        # 4. Generate mybatis code
        mybatis_code = backend_developer.write_mybatis_code(
            module_name=module_name,
            create_table_sql=create_tables_sql,
            domain_code=domain_code
        )
        current_incremental_code_lines += len(mybatis_code.splitlines())
        FileUtil.write_file(
            file_path=workspace_root / namespace / "backend" / "business" / "src" / "main" / "resources" / "mapper" / "business" / f"{module_name}Mapper.xml",
            content=mybatis_code
        )

        # 5. Generate DAO code
        dao_code = backend_developer.write_dao_code(
            module_name=module_name,
            mybatis_code=mybatis_code,
        )
        current_incremental_code_lines += len(dao_code.splitlines())
        FileUtil.write_file(
            file_path=workspace_root / namespace / "backend" / "business" / "src" / "main" / "java" / "com" / "demo" / "business" / "mapper" / f"{module_name}Mapper.java",
            content=dao_code
        )

        # 6. Generate ServiceImpl code
        service_impl_code = backend_developer.write_service_impl_code(
            module_name=module_name,
            incremental=incremental,
            dao_code=dao_code,
            mybatis_code=mybatis_code,
            domain_code=domain_code
        )
        current_incremental_code_lines += len(service_impl_code.splitlines())
        FileUtil.write_file(
            file_path=workspace_root / namespace / "backend" / "business" / "src" / "main" / "java" / "com" / "demo" / "business" / "service" / "impl" / f"{module_name}ServiceImpl.java",
            content=service_impl_code
        )

        # 7. Generate Service code
        service_code = backend_developer.write_service_code(
            module_name=module_name,
            service_impl_code=service_impl_code
        )
        current_incremental_code_lines += len(service_code.splitlines())
        FileUtil.write_file(
            file_path=workspace_root / namespace / "backend" / "business" / "src" / "main" / "java" / "com" / "demo" / "business" / "service" / f"I{module_name}Service.java",
            content=service_code
        )

        # 8. Generate Controller code
        controller_code = backend_developer.write_controller_code(
            module_name=module_name,
            incremental=incremental,
            service_code=service_code,
            domain_code=domain_code
        )
        current_incremental_code_lines += len(controller_code.splitlines())
        FileUtil.write_file(
            file_path=workspace_root / namespace / "backend" / "business" / "src" / "main" / "java" / "com" / "demo" / "business" / "controller" / f"{module_name}Controller.java",
            content=controller_code
        )

        # 9. Write unit test code (generated but NOT executed per-module)
        unit_test_code = backend_developer.write_unit_test_code(
            module_name=module_name,
            service_impl_code=service_impl_code,
            domain_code=domain_code,
            create_tables_sql=create_tables_sql
        )
        current_incremental_code_lines += len(unit_test_code.splitlines())
        FileUtil.write_file(
            file_path=workspace_root / namespace / "backend" / "admin" / "src" / "test" / "java" / "com" / "demo" / "business" / "service" / f"{module_name}ServiceTest.java",
            content=unit_test_code
        )

        logger.info(f"[Waterfall Backend] [{module_name} Module]: Generated backend code lines: {current_incremental_code_lines}")
        backend_code_lines += current_incremental_code_lines

    logger.info(f"[Waterfall Backend] Total backend code lines: {backend_code_lines}")
    return {
        "backend_code_lines": backend_code_lines
    }


def waterfall_frontend_dev(state: WaterfallDevelopmentState):
    """
    Waterfall frontend development: generate ALL modules' frontend code in one pass.
    """
    incremental_list = state["incremental_list"]
    inc_class_dict = state["inc_class_dict"]
    namespace = state["project_namespace"]
    workspace_root = get_workspace_root(state)
    frontend_code_lines = 0

    for incremental in incremental_list:
        module_name = incremental.get("module_name")
        if module_name is None or module_name == "":
            continue

        incremental_id = incremental["id"]
        current_class_diagram = inc_class_dict.get(incremental_id) or inc_class_dict.get(str(incremental_id))
        if current_class_diagram is None:
            logger.warning(f"[Waterfall] No class diagram found for incremental {incremental_id}, skipping frontend.")
            continue

        current_incremental_code_lines = 0
        logger.info(f"[Waterfall Frontend] Generating module: {module_name}")

        # 1. Generate API code
        api_code = frontend_developer.write_api_code(module_name=module_name)
        current_incremental_code_lines += len(api_code.splitlines())
        FileUtil.write_file(
            file_path=workspace_root / namespace / "frontend" / "src" / "api" / "business" / f"{NameRuleConverter.to_snake_case(module_name)}.js",
            content=api_code)

        # 2. Generate Page code
        page_code = frontend_developer.write_page_code(
            module_name=module_name,
            incremental=incremental,
            class_diagram=current_class_diagram,
            api_code=api_code
        )
        current_incremental_code_lines += len(page_code.splitlines())
        page_dir = workspace_root / namespace / "frontend" / "src" / "views" / "business" / NameRuleConverter.to_snake_case(module_name)
        FileUtil.create_dir(page_dir)
        FileUtil.write_file(
            file_path=page_dir / "index.vue",
            content=page_code
        )

        logger.info(f"[Waterfall Frontend] [{module_name} Module]: Generated frontend code lines: {current_incremental_code_lines}")
        frontend_code_lines += current_incremental_code_lines

    logger.info(f"[Waterfall Frontend] Total frontend code lines: {frontend_code_lines}")
    return {
        "frontend_code_lines": frontend_code_lines
    }


def waterfall_full_test(state: WaterfallDevelopmentState):
    """
    One-time full test after all code has been generated.
    Runs `mvn clean test` on the entire backend project.
    """
    namespace = state["project_namespace"]
    workspace_root = get_workspace_root(state)
    attempt = state["attempt"] + 1
    
    is_pass = False
    try:
        is_pass = backend_developer.run_full_test_code(namespace=namespace, workspace_root=workspace_root)
    except Exception as e:
        logger.error(f"[Waterfall Test] {e}")
        is_pass = False

    if is_pass:
        logger.info(f"[Waterfall Test] Full test PASSED on attempt {attempt}.")
        return {"attempt": attempt, "is_pass": is_pass}
    else:
        if attempt >= MAX_ITERATIONS:
            logger.error(f"[Waterfall Test] Full test FAILED after {MAX_ITERATIONS} attempts. Stopping retry.")
        else:
            logger.info(f"[Waterfall Test] Full test FAILED. Attempt {attempt} of {MAX_ITERATIONS}. Cleaning up code for retry...")
            __remove_generated_waterfall_code(
                namespace=namespace,
                incremental_list=state["incremental_list"],
                workspace_root=workspace_root,
            )
        return {"attempt": attempt, "is_pass": is_pass}


def route_waterfall_retry(state: WaterfallDevelopmentState):
    """
    Route to either retry backend dev or end based on test passage and attempt count.
    """
    attempt = state["attempt"]
    is_pass = state["is_pass"]
    logger.info(f"[Waterfall Route] Attempt: {attempt}, Is Pass: {is_pass}")
    if is_pass or attempt >= MAX_ITERATIONS:
        return "end"
    else:
        return "retry"


# ====================== Waterfall LangGraph Definition ======================
# Linear graph: init_proj → waterfall_backend_dev → waterfall_frontend_dev → waterfall_full_test → END

waterfall_development_graph = StateGraph(WaterfallDevelopmentState)
waterfall_development_graph.add_node("init_proj", init_proj)
waterfall_development_graph.add_node("waterfall_backend_dev", waterfall_backend_dev)
waterfall_development_graph.add_node("waterfall_frontend_dev", waterfall_frontend_dev)
waterfall_development_graph.add_node("waterfall_full_test", waterfall_full_test)

waterfall_development_graph.add_edge(START, "init_proj")
waterfall_development_graph.add_edge("init_proj", "waterfall_backend_dev")
waterfall_development_graph.add_edge("waterfall_backend_dev", "waterfall_frontend_dev")
waterfall_development_graph.add_edge("waterfall_frontend_dev", "waterfall_full_test")
waterfall_development_graph.add_conditional_edges("waterfall_full_test", route_waterfall_retry, {
    "retry": "waterfall_backend_dev",
    "end": END
})

waterfall_development_workflow = waterfall_development_graph.compile()

logger.debug(f"Waterfall Development Workflow: \n{waterfall_development_workflow.get_graph().draw_ascii()}")
