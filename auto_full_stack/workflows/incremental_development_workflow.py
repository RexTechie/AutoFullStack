#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/6/15 23:12
@Author  : Rex
@File    : incremental_development_workflow.py
"""
import platform
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
from auto_full_stack.utils import FileUtil, NameRuleConverter
from auto_full_stack.utils.mysql_util import MySQLUtil

# Template path
TEMPLATE_PATH = ROOT / "templates"

# Frontend settings
FRONTEND_SETTING_THEME = ['#409EFF', '#1890FF', '#212121', '#11A983', '#13C2C2', '#6959CD']
FRONTEND_SETTING_THEME_SIDE = ['theme-dark', 'theme-light']
FRONTEND_SETTING_TOP_NAV = ['True', False]

frontend_developer = FrontendDeveloper()
backend_developer = BackendDeveloper()

# Define Node
class IncrementNode:
    def __init__(self, data):
        self.id = data["id"]
        self.data = data
        self.dependencies = data.get("dependencies", [])
        self.children = []

    def __repr__(self):
        return f"Node({self.id}, name='{self.data.get('name')}')"

def __build_dependency_graph(increments):
    """
    Build incremental dependency graph
    """
    nodes = {item["id"]: IncrementNode(item) for item in increments}
    for node in nodes.values():
        for dep_id in node.dependencies:
            if dep_id in nodes:
                nodes[dep_id].children.append(node)
    return nodes

def __topological_sort(nodes):
    """
    Topological sort using Kahn's algorithm
    """
    indegree = {node_id: 0 for node_id in nodes}
    for node in nodes.values():
        for child in node.children:
            indegree[child.id] += 1

    queue = [nodes[nid] for nid, deg in indegree.items() if deg == 0]
    sorted_nodes = []

    while queue:
        current = queue.pop(0)
        sorted_nodes.append(current.data)
        for child in current.children:
            indegree[child.id] -= 1
            if indegree[child.id] == 0:
                queue.append(child)
    return sorted_nodes

def __print_dependency_graph(nodes):
    """
    Print the incremental dependency graph
    """
    logger.info("=== Topological Dependency Graph ===")
    for node in nodes.values():
        if node.children:
            children_names = ", ".join(
                [f"{child.id}:{child.data['name']}" for child in node.children]
            )
            logger.info(f"{node.id}:{node.data['name']}  →  {children_names}")
        else:
            logger.info(f"{node.id}:{node.data['name']}  →  (NULL)")

def __config_backend_project(project_name: str, namespace: str, workspace_root):
    """
    Configure backend project files: application.yml.templ, application-druid.yml.templ
    """
    # Read backend config template files
    application_yml = FileUtil.read_file(TEMPLATE_PATH / "config_template" / "application.yml.templ")
    application_druid_yml = FileUtil.read_file(TEMPLATE_PATH / "config_template" / "application-druid.yml.templ")
    logback_xml = FileUtil.read_file(TEMPLATE_PATH / "config_template" / "logback.xml.templ")

    # Substitute variables in the templates
    application_yml= Template(application_yml).substitute({
        "name": namespace + "_backend",
        "profile": f"D:/app/{namespace}/uploadPath" if platform.system().lower() == "windows" else f"~/app/{namespace}/uploadPath",
    })
    application_druid_yml = Template(application_druid_yml).substitute({
        "database": namespace
    })
    logback_xml = logback_xml.replace("@log_path@", f"D:/app/{namespace}/logs" if platform.system().lower() == "windows" else f"~/app/{namespace}/logs")
    # Write the modified config files to the backend project directory
    FileUtil.write_file(workspace_root / namespace / "backend" / "admin" / "src" / "main" / "resources" / "application.yml", application_yml)
    FileUtil.write_file(workspace_root / namespace / "backend" / "admin" / "src" / "main" / "resources" / "application-druid.yml", application_druid_yml)
    FileUtil.write_file(workspace_root / namespace / "backend" / "admin" / "src" / "main" / "resources" / "logback.xml", logback_xml)

def __config_frontend_project(project_name: str, namespace: str, workspace_root):
    # Read frontend config template files
    development_env = FileUtil.read_file(TEMPLATE_PATH / "config_template" / ".env.development.templ")
    production_env = FileUtil.read_file(TEMPLATE_PATH / "config_template" / ".env.production.templ")
    staging_env = FileUtil.read_file(TEMPLATE_PATH / "config_template" / ".env.staging.templ")
    package_json = FileUtil.read_file(TEMPLATE_PATH /"config_template" / "package.json.templ")
    setting_js = FileUtil.read_file(TEMPLATE_PATH / "config_template" / "settings.js.templ")

    # Substitute variables in the templates
    development_env = Template(development_env).substitute({
        "VUE_APP_TITLE": project_name
    })
    production_env = Template(production_env).substitute({
        "VUE_APP_TITLE": project_name
    })
    staging_env = Template(staging_env).substitute({
        "VUE_APP_TITLE": project_name
    })
    package_json = Template(package_json).substitute({
        "name": namespace + "_frontend",
        "description": project_name
    })
    # Random Frontend theme settings
    setting_js = Template(setting_js).substitute({
        "theme": Random().choice(FRONTEND_SETTING_THEME),
        "sideTheme": Random().choice(FRONTEND_SETTING_THEME_SIDE),
        "topNav": str(Random().choice(FRONTEND_SETTING_TOP_NAV)).lower()
    })


    # Write the modified config files to the frontend project directory
    FileUtil.write_file(workspace_root / namespace / "frontend" / ".env.development", development_env)
    FileUtil.write_file(workspace_root / namespace / "frontend" / ".env.production", production_env)
    FileUtil.write_file(workspace_root / namespace / "frontend" / ".env.staging", staging_env)
    FileUtil.write_file(workspace_root / namespace / "frontend" / "package.json", package_json)
    FileUtil.write_file(workspace_root / namespace / "frontend" / "src" / "settings.js", setting_js)


class DevelopmentState(TypedDict):
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
    current_incremental_index: int
    current_incremental: dict | None
    current_class_diagram: str | None
    frontend_code_lines: int
    backend_code_lines: int
    module_attempts: dict[str, dict]


def init_proj(state: DevelopmentState) :
    """
    Initialize the project by creating the necessary directory structure and files.
    """
    namespace = state['project_namespace']
    project_name = state['project_name']
    incremental_list = state["incremental_list"]
    workspace_root = get_workspace_root(state)

    # 0. Topological sort of incremental nodes
    incremental_graph = __build_dependency_graph(incremental_list)
    __print_dependency_graph(incremental_graph)
    new_incremental_list = __topological_sort(incremental_graph)
    logger.info(f"Incremental list: {new_incremental_list}")

    # 1. Create project directory
    project_path = workspace_root / state["project_namespace"]
    FileUtil.create_dir(project_path)
    # 2. Copy template files to project directory
    FileUtil.copy_all_files(TEMPLATE_PATH / "full_stack_template", project_path)
    sql_path = project_path / "sql"
    # 3. Execute SQL scripts to create database and tables
    # 3.1. Create database
    MySQLUtil.drop_database(database=namespace)
    MySQLUtil.create_database(database=namespace)
    # 3.2 Execute create table scripts
    MySQLUtil.execute_sql_by_file(
        script_path=sql_path  / "quartz.sql",
        database=namespace
    )
    MySQLUtil.execute_sql_by_file(
        script_path = sql_path / "init.sql",
        database=namespace
    )
    # 4.Modify project config files if needed
    __config_backend_project(project_name=project_name, namespace=namespace, workspace_root=workspace_root)
    __config_frontend_project(project_name=project_name, namespace=namespace, workspace_root=workspace_root)

    return {
        "incremental_list": new_incremental_list,
        "frontend_code_lines": 0,
        "backend_code_lines": 0,
        "module_attempts": {}
    }

def route_incremental(state: DevelopmentState):
    """
    Route to the next incremental task.
    """
    return "end" if state["current_incremental_index"] >= len(state["incremental_list"]) else "next_incremental"

def next_incremental(state: DevelopmentState):
    idx = state["current_incremental_index"]
    current_incremental = state["incremental_list"][idx]
    inc_id = current_incremental["id"]
    return {
        "current_incremental_index": idx + 1,
        "current_incremental": current_incremental,
        "current_class_diagram": state["inc_class_dict"][inc_id],
    }
def __rollback_module_generation(namespace: str, module_name: str, workspace_root):
    """
    Remove generated backend code files and rollback database records for the module.
    """
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

    # Clean up database data
    snake_name = NameRuleConverter.to_snake_case(module_name)
    drop_table_sql = f"DROP TABLE IF EXISTS tb_{snake_name}"
    delete_menu_sql = f"DELETE FROM sys_menu WHERE component LIKE 'business/{snake_name}/%%' OR perms LIKE 'business:{snake_name}:%%'"
    try:
        MySQLUtil.execute_sql_script(sql_script=drop_table_sql, database=namespace)
        MySQLUtil.execute_sql_script(sql_script=delete_menu_sql, database=namespace)
        logger.info(f"[{module_name} Module]: Removed database table and sys_menu data for rollback.")
    except Exception as e:
        logger.error(f"[{module_name} Module]: Failed to remove database data during rollback: {e}")

def backend_dev(state: DevelopmentState):
    """
    Backend development function
    """
    current_incremental = state["current_incremental"]
    current_class_diagram = state["current_class_diagram"]
    namespace = state["project_namespace"]
    workspace_root = get_workspace_root(state)
    backend_code_lines = state["backend_code_lines"]
    module_attempts = state.get("module_attempts", {})
    module_name = current_incremental.get("module_name")

    if module_name is None or module_name == "":
        return {}

    max_attempt = MAX_ITERATIONS
    attempt = 0
    is_pass = False
    
    while True:
        current_incremental_code_lines = 0

        # 1. Create tables
        create_tables_sql = backend_developer.write_create_tables_sql(
            incremental=current_incremental,
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
            incremental=current_incremental,
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
            incremental=current_incremental,
            service_code=service_code,
            domain_code=domain_code
        )
        current_incremental_code_lines += len(controller_code.splitlines())
        FileUtil.write_file(
            file_path=workspace_root / namespace / "backend" / "business" / "src" / "main" / "java" / "com" / "demo" / "business" / "controller" / f"{module_name}Controller.java",
            content=controller_code
        )

        # 9. Write unit test code
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
        unit_test_class = f"{module_name}ServiceTest"

        logger.info(f"[{module_name} Module]: Generated backend code lines: {current_incremental_code_lines}")
        try:
            is_pass = backend_developer.run_unit_test_code(
                namespace=namespace,
                unit_test_class=unit_test_class,
                workspace_root=workspace_root,
            )
            logger.info(f"[Incremental Test] [{module_name} Module] Unit Test Passed: {is_pass}")
            attempt += 1
            if is_pass:
                logger.info(f"[Incremental Test] [{module_name} Module] Unit test PASSED on attempt {attempt}.")
                backend_code_lines += current_incremental_code_lines
                break
            else:
                if attempt >= max_attempt:
                    logger.error(f"[Incremental Test] [{module_name} Module] Unit test FAILED after {max_attempt} attempts. Stopping retry.")
                    backend_code_lines += current_incremental_code_lines
                    break
                else:
                    logger.info(f"[Incremental Test] [{module_name} Module] Unit test FAILED. Attempt {attempt} of {max_attempt}. Cleaning up code and database for retry...")
                    __rollback_module_generation(
                        namespace=namespace,
                        module_name=module_name,
                        workspace_root=workspace_root,
                    )
        except RuntimeError as e:
            logger.error(e)
            attempt += 1
            is_pass = False
            # backend_code_lines += current_incremental_code_lines
            logger.info(f"[Incremental Test] [{module_name} Module] Unit test FAILED. Attempt {attempt} of {max_attempt}. Cleaning up code and database for retry...")
            __rollback_module_generation(
                namespace=namespace,
                module_name=module_name,
                workspace_root=workspace_root,
            )
            if attempt >= max_attempt:
                logger.error(f"[Incremental Test] [{module_name} Module] Unit test FAILED after {max_attempt} attempts. Stopping retry.")
                break

    module_attempts[module_name] = {
        "attempts": attempt,
        "is_pass": is_pass
    }
    return {
        "backend_code_lines": backend_code_lines,
        "module_attempts": module_attempts
    }

def frontend_dev(state: DevelopmentState):
    current_incremental = state["current_incremental"]
    current_class_diagram = state["current_class_diagram"]
    namespace = state["project_namespace"]
    workspace_root = get_workspace_root(state)
    frontend_code_lines = state["frontend_code_lines"]
    module_name = current_incremental.get("module_name")

    if module_name is None or module_name == "":
        return {}

    current_incremental_code_lines = 0

    # 1. Generate API code
    api_code = frontend_developer.write_api_code(module_name=module_name)
    current_incremental_code_lines += len(api_code.splitlines())
    FileUtil.write_file(
        file_path=workspace_root / namespace / "frontend" / "src" / "api" / "business" / f"{NameRuleConverter.to_snake_case(module_name)}.js",
        content=api_code)
    # 2. Generate Page code
    page_code = frontend_developer.write_page_code(
        module_name=module_name,
        incremental=current_incremental,
        class_diagram=current_class_diagram,
        api_code=api_code
    )
    current_incremental_code_lines += len(page_code.splitlines())
    page_dir = workspace_root / namespace / "frontend" / "src" / "views" / "business" / NameRuleConverter.to_snake_case(module_name)
    # Create page directory
    FileUtil.create_dir(page_dir)
    FileUtil.write_file(
        file_path=page_dir / "index.vue",
        content=page_code
    )
    logger.info(f"[{module_name} Module]: Generated frontend code lines: {current_incremental_code_lines}")
    frontend_code_lines += current_incremental_code_lines
    return {
        "frontend_code_lines": frontend_code_lines
    }

development_graph = StateGraph(DevelopmentState)
development_graph.add_node("init_proj", init_proj)
development_graph.add_node("next_incremental", next_incremental)
development_graph.add_node("backend_dev", backend_dev)
development_graph.add_node("frontend_dev", frontend_dev)

development_graph.add_edge(START, "init_proj")
development_graph.add_conditional_edges("init_proj", route_incremental, {
    "next_incremental": "next_incremental",
    "end": END
})
development_graph.add_edge("next_incremental", "backend_dev")
development_graph.add_edge("next_incremental", "frontend_dev")
development_graph.add_conditional_edges("backend_dev", route_incremental, {
    "next_incremental": "next_incremental",
    "end": END
})
development_graph.add_conditional_edges("frontend_dev", route_incremental, {
    "next_incremental": "next_incremental",
    "end": END
})

incremental_development_workflow = development_graph.compile()
development_workflow = incremental_development_workflow
