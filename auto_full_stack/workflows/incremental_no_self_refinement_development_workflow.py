#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/4/9
@Author  : Rex
@File    : incremental_no_self_refinement_development_workflow.py
"""
from __future__ import annotations

from langgraph.graph import StateGraph, START, END

from auto_full_stack.workflows import incremental_development_workflow as base


IncrementalNoSelfRefinementDevelopmentState = base.DevelopmentState


def backend_dev(state: IncrementalNoSelfRefinementDevelopmentState):
    """
    Backend development without module-level retry or rollback.

    The module is generated once, tested once, and its artifact is kept
    regardless of the unit-test outcome so the ablation isolates the
    contribution of iterative self-repair.
    """
    current_incremental = state["current_incremental"]
    current_class_diagram = state["current_class_diagram"]
    namespace = state["project_namespace"]
    workspace_root = base.get_workspace_root(state)
    backend_code_lines = state["backend_code_lines"]
    module_attempts = state.get("module_attempts", {})
    module_name = current_incremental.get("module_name")

    if module_name is None or module_name == "":
        return {}

    current_incremental_code_lines = 0
    attempt = 1
    is_pass = False

    # 1. Create tables
    create_tables_sql = base.backend_developer.write_create_tables_sql(
        incremental=current_incremental,
        class_diagram=current_class_diagram,
    )
    base.FileUtil.write_file(
        file_path=workspace_root / namespace / "sql" / f"create_tables_inc_{module_name}.sql",
        content=create_tables_sql,
    )
    base.MySQLUtil.execute_sql_script(
        sql_script=create_tables_sql,
        database=namespace,
    )

    # 2. Insert menu
    menu_info = {
        "name": module_name,
        "path": base.NameRuleConverter.to_snake_case(module_name),
    }
    insert_menu_info = base.backend_developer.write_insert_menu_sql(menu_info=menu_info)
    base.FileUtil.write_file(
        file_path=workspace_root / namespace / "sql" / f"insert_menu_inc_{module_name}.sql",
        content=insert_menu_info,
    )
    base.MySQLUtil.execute_sql_script(
        sql_script=insert_menu_info,
        database=namespace,
    )

    # 3. Generate domain code
    domain_code = base.backend_developer.write_domain_code(
        module_name=module_name,
        create_table_sql=create_tables_sql,
    )
    current_incremental_code_lines += len(domain_code.splitlines())
    base.FileUtil.write_file(
        file_path=workspace_root / namespace / "backend" / "business" / "src" / "main" / "java" / "com" / "demo" / "business" / "domain" / f"{module_name}.java",
        content=domain_code,
    )

    # 4. Generate mybatis code
    mybatis_code = base.backend_developer.write_mybatis_code(
        module_name=module_name,
        create_table_sql=create_tables_sql,
        domain_code=domain_code,
    )
    current_incremental_code_lines += len(mybatis_code.splitlines())
    base.FileUtil.write_file(
        file_path=workspace_root / namespace / "backend" / "business" / "src" / "main" / "resources" / "mapper" / "business" / f"{module_name}Mapper.xml",
        content=mybatis_code,
    )

    # 5. Generate DAO code
    dao_code = base.backend_developer.write_dao_code(
        module_name=module_name,
        mybatis_code=mybatis_code,
    )
    current_incremental_code_lines += len(dao_code.splitlines())
    base.FileUtil.write_file(
        file_path=workspace_root / namespace / "backend" / "business" / "src" / "main" / "java" / "com" / "demo" / "business" / "mapper" / f"{module_name}Mapper.java",
        content=dao_code,
    )

    # 6. Generate ServiceImpl code
    service_impl_code = base.backend_developer.write_service_impl_code(
        module_name=module_name,
        incremental=current_incremental,
        dao_code=dao_code,
        mybatis_code=mybatis_code,
        domain_code=domain_code,
    )
    current_incremental_code_lines += len(service_impl_code.splitlines())
    base.FileUtil.write_file(
        file_path=workspace_root / namespace / "backend" / "business" / "src" / "main" / "java" / "com" / "demo" / "business" / "service" / "impl" / f"{module_name}ServiceImpl.java",
        content=service_impl_code,
    )

    # 7. Generate Service code
    service_code = base.backend_developer.write_service_code(
        module_name=module_name,
        service_impl_code=service_impl_code,
    )
    current_incremental_code_lines += len(service_code.splitlines())
    base.FileUtil.write_file(
        file_path=workspace_root / namespace / "backend" / "business" / "src" / "main" / "java" / "com" / "demo" / "business" / "service" / f"I{module_name}Service.java",
        content=service_code,
    )

    # 8. Generate Controller code
    controller_code = base.backend_developer.write_controller_code(
        module_name=module_name,
        incremental=current_incremental,
        service_code=service_code,
        domain_code=domain_code,
    )
    current_incremental_code_lines += len(controller_code.splitlines())
    base.FileUtil.write_file(
        file_path=workspace_root / namespace / "backend" / "business" / "src" / "main" / "java" / "com" / "demo" / "business" / "controller" / f"{module_name}Controller.java",
        content=controller_code,
    )

    # 9. Generate one unit test and execute it once
    unit_test_code = base.backend_developer.write_unit_test_code(
        module_name=module_name,
        service_impl_code=service_impl_code,
        domain_code=domain_code,
        create_tables_sql=create_tables_sql,
    )
    current_incremental_code_lines += len(unit_test_code.splitlines())
    base.FileUtil.write_file(
        file_path=workspace_root / namespace / "backend" / "admin" / "src" / "test" / "java" / "com" / "demo" / "business" / "service" / f"{module_name}ServiceTest.java",
        content=unit_test_code,
    )
    unit_test_class = f"{module_name}ServiceTest"

    base.logger.info(
        f"[{module_name} Module][Incremental w/o Self-Refinement]: Generated backend code lines: {current_incremental_code_lines}"
    )

    try:
        is_pass = base.backend_developer.run_unit_test_code(
            namespace=namespace,
            unit_test_class=unit_test_class,
            workspace_root=workspace_root,
        )
        base.logger.info(
            f"[Incremental w/o Self-Refinement Test] [{module_name} Module] Unit Test Passed: {is_pass}"
        )
        if is_pass:
            base.logger.info(
                f"[Incremental w/o Self-Refinement Test] [{module_name} Module] Unit test PASSED on attempt 1."
            )
        else:
            base.logger.info(
                f"[Incremental w/o Self-Refinement Test] [{module_name} Module] Unit test FAILED on attempt 1. "
                "Self-refinement is disabled in this ablation setting; keeping generated code and continuing."
            )
    except RuntimeError as e:
        base.logger.error(e)
        is_pass = False
        base.logger.info(
            f"[Incremental w/o Self-Refinement Test] [{module_name} Module] Unit test FAILED on attempt 1 due to "
            "test/runtime error. Self-refinement is disabled in this ablation setting; keeping generated code and continuing."
        )

    # Keep generated artifacts regardless of the unit-test outcome.
    backend_code_lines += current_incremental_code_lines
    module_attempts[module_name] = {
        "attempts": attempt,
        "is_pass": is_pass,
    }
    return {
        "backend_code_lines": backend_code_lines,
        "module_attempts": module_attempts,
    }


incremental_no_self_refinement_development_graph = StateGraph(IncrementalNoSelfRefinementDevelopmentState)
incremental_no_self_refinement_development_graph.add_node("init_proj", base.init_proj)
incremental_no_self_refinement_development_graph.add_node("next_incremental", base.next_incremental)
incremental_no_self_refinement_development_graph.add_node("backend_dev", backend_dev)
incremental_no_self_refinement_development_graph.add_node("frontend_dev", base.frontend_dev)

incremental_no_self_refinement_development_graph.add_edge(START, "init_proj")
incremental_no_self_refinement_development_graph.add_conditional_edges("init_proj", base.route_incremental, {
    "next_incremental": "next_incremental",
    "end": END,
})
incremental_no_self_refinement_development_graph.add_edge("next_incremental", "backend_dev")
incremental_no_self_refinement_development_graph.add_edge("next_incremental", "frontend_dev")
incremental_no_self_refinement_development_graph.add_conditional_edges("backend_dev", base.route_incremental, {
    "next_incremental": "next_incremental",
    "end": END,
})
incremental_no_self_refinement_development_graph.add_conditional_edges("frontend_dev", base.route_incremental, {
    "next_incremental": "next_incremental",
    "end": END,
})

incremental_no_self_refinement_development_workflow = incremental_no_self_refinement_development_graph.compile()
