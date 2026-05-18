#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/1 9:38
@Author  : Rex
@File    : backend_developer.py
"""
import json
import platform
import subprocess
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser

from auto_full_stack.common.llm import model
from auto_full_stack.common.const import ROOT, DEFAULT_WORKSPACE_ROOT
from auto_full_stack.common.log import logger
from auto_full_stack.utils import PromptUtil, MarkdownUtil, FileUtil, MavenTestResultUtil


class BackendDeveloper:
    llm = None
    name = "👨‍💻 Backend Developer"

    def __init__(self):
        self.llm = model | StrOutputParser()

    def _workspace_root(self, workspace_root=None):
        return Path(workspace_root) if workspace_root else DEFAULT_WORKSPACE_ROOT

    # ====================== SQL Action ======================
    def write_create_tables_sql(self, incremental: dict, class_diagram: str):
        """
        Write Create Table SQL
        """
        prompt = PromptUtil.prompt_handle("coding_workflow/backend_developer/sql_create_table.templ", {
            "incremental": json.dumps(incremental, ensure_ascii=False),
            "classDiagram": class_diagram,
            "example": FileUtil.read_file(ROOT / "workflows" / "prompt" / "coding_workflow/backend_developer/examples/sql_create_table.sql.example")
        })
        create_table_sql = self.llm.invoke(prompt)
        create_table_sql = MarkdownUtil.parse_code_block(create_table_sql, language="sql")[0]
        logger.info(f"[{self.name}] Create Table SQL: \n{create_table_sql}\n")
        return create_table_sql

    def write_insert_menu_sql(self, menu_info: dict):
        """
        Write Insert Menu Info SQL
        """
        prompt = PromptUtil.prompt_handle("coding_workflow/backend_developer/sql_insert_menu_info.templ", {
            "menuInfo": json.dumps(menu_info, ensure_ascii=False),
            "example": FileUtil.read_file(ROOT / "workflows" / "prompt" / "coding_workflow/backend_developer/examples/sql_insert_menu_info.sql.example")
        })
        insert_menu_info_sql = self.llm.invoke(prompt)
        insert_menu_info_sql = MarkdownUtil.parse_code_block(insert_menu_info_sql, language="sql")[0]
        logger.info(f"[{self.name}] Insert Menu Info SQL: \n{insert_menu_info_sql}\n")
        return insert_menu_info_sql

    # ====================== Code Action ======================
    def write_domain_code(self, module_name: str, create_table_sql: str):
        """
        Write Domain Code
        """
        prompt = PromptUtil.prompt_handle("coding_workflow/backend_developer/domain.templ", {
            "moduleName": module_name,
            "createTableSql": create_table_sql,
            "example": FileUtil.read_file(ROOT / "workflows" / "prompt" / "coding_workflow/backend_developer/examples/domain.java.example")
        })
        domain_code = self.llm.invoke(prompt)
        domain_code = MarkdownUtil.parse_code_block(domain_code, language="java")[0]
        logger.info(f"[{self.name}] Domain Code: \n{domain_code}\n")
        return domain_code

    def write_mybatis_code(self, module_name: str, create_table_sql: str, domain_code: str):
        """
        Write MyBatis Code
        """
        prompt = PromptUtil.prompt_handle("coding_workflow/backend_developer/mybatis.templ", {
            "moduleName": module_name,
            "createTableSql": create_table_sql,
            "domainCode": domain_code,
            "example": FileUtil.read_file(ROOT / "workflows" / "prompt" / "coding_workflow/backend_developer/examples/mybatis.xml.example")
        })
        mybatis_code = self.llm.invoke(prompt)
        mybatis_code = MarkdownUtil.parse_code_block(mybatis_code, language="xml")[0]
        logger.info(f"[{self.name}] MyBatis Code: \n{mybatis_code}\n")
        return mybatis_code

    def write_dao_code(self, module_name: str, mybatis_code: str):
        """
        Write DAO Code
        """
        prompt = PromptUtil.prompt_handle("coding_workflow/backend_developer/dao.templ", {
            "moduleName": module_name,
            "mybatisCode": mybatis_code,
            "example": FileUtil.read_file(ROOT / "workflows" / "prompt" / "coding_workflow/backend_developer/examples/dao.java.example")
        })
        dao_code = self.llm.invoke(prompt)
        dao_code = MarkdownUtil.parse_code_block(dao_code, language="java")[0]
        logger.info(f"[{self.name}] DAO Code: \n{dao_code}\n")
        return dao_code

    def write_service_impl_code(self, module_name: str, incremental: dict, dao_code: str, mybatis_code: str, domain_code: str):
        """
        Write service impl Code
        """
        prompt = PromptUtil.prompt_handle("coding_workflow/backend_developer/service_impl.templ", {
            "moduleName": module_name,
            "incremental": json.dumps(incremental, ensure_ascii=False),
            "daoCode": dao_code,
            "mybatisCode": mybatis_code,
            "domainCode": domain_code,
            "example": FileUtil.read_file(ROOT / "workflows" / "prompt" / "coding_workflow/backend_developer/examples/service_impl.java.example")
        })
        service_impl_code = self.llm.invoke(prompt)
        service_impl_code = MarkdownUtil.parse_code_block(service_impl_code, language="java")[0]
        logger.info(f"[{self.name}] Service Impl Code: \n{service_impl_code}\n")
        return service_impl_code

    def write_service_code(self, module_name: str, service_impl_code: str):
        """
        Write service Code
        """
        prompt = PromptUtil.prompt_handle("coding_workflow/backend_developer/service.templ", {
            "moduleName": module_name,
            "serviceImplCode": service_impl_code,
            "example": FileUtil.read_file(ROOT / "workflows" / "prompt" / "coding_workflow/backend_developer/examples/service.java.example")
        })
        service_code = self.llm.invoke(prompt)
        service_code = MarkdownUtil.parse_code_block(service_code, language="java")[0]
        logger.info(f"[{self.name}] Service Code: \n{service_code}\n")
        return service_code

    def write_controller_code(self, module_name: str, incremental:dict, service_code: str, domain_code: str):
        """
        Write controller Code
        """
        prompt = PromptUtil.prompt_handle("coding_workflow/backend_developer/controller.templ", {
            "moduleName": module_name,
            "incremental": json.dumps(incremental, ensure_ascii=False),
            "serviceCode": service_code,
            "domainCode": domain_code,
            "example": FileUtil.read_file(ROOT / "workflows" / "prompt" / "coding_workflow/backend_developer/examples/controller.java.example")
        })
        controller_code = self.llm.invoke(prompt)
        controller_code = MarkdownUtil.parse_code_block(controller_code, language="java")[0]
        logger.info(f"[{self.name}] Controller Code: \n{controller_code}\n")
        return controller_code

    def write_unit_test_code(self, module_name: str, service_impl_code: str, domain_code: str, create_tables_sql: str):
        """
        Write unit test code
        """
        prompt = PromptUtil.prompt_handle("coding_workflow/backend_developer/unit_test_code.templ", {
            "moduleName": module_name,
            "serviceImplCode": service_impl_code,
            "domainCode": domain_code,
            "sqlCreateTable": create_tables_sql,
            "example": FileUtil.read_file(ROOT / "workflows" / "prompt" / "coding_workflow/backend_developer/examples/unit_test.java.example")
        })
        unit_test_code = self.llm.invoke(prompt)
        unit_test_code = MarkdownUtil.parse_code_block(unit_test_code, language="java")[0]
        logger.info(f"[{self.name}] Unit Test Code: \n{unit_test_code}\n")
        return unit_test_code

    def run_unit_test_code(self, namespace: str, unit_test_class: str, workspace_root=None):
        """
        Run unit test code
        1. mvn install -DskipTests
        2. mvn test -Dtest=UnitTestClass
        """
        workspace_root = self._workspace_root(workspace_root)
        mvn_cmd = "mvn.cmd" if platform.system().lower() == "windows" else "mvn"
        install_cmd = [mvn_cmd, "clean", "install", "-DskipTests"]
        cwd = workspace_root / namespace / "backend"
        subprocess.run(
            args=install_cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        test_cmd = [mvn_cmd, "test", f"-Dtest={unit_test_class}"]
        cwd = workspace_root / namespace / "backend" / "admin"
        test_result = subprocess.run(
            args=test_cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        surefire_report_path = workspace_root / namespace / "backend" / "admin" / "target" / "surefire-reports" / f"TEST-com.demo.business.service.{unit_test_class}.xml"

        if FileUtil.exists(file_path=surefire_report_path):
            summary = MavenTestResultUtil.parse_test_result(xml_file_path=surefire_report_path)
            logger.info(f"[{self.name}] Unit Test Summary: \n{json.dumps(summary, indent=4)}\n")
            if summary["errors"] > 0:
                raise RuntimeError(f"[{self.name}] Unit Test Failed with Errors.")
            return not (summary["failures"] > 0)
        else:
            # Log Maven output to help diagnose why no report was generated
            logger.error(f"[{self.name}] Maven test command failed, no report generated.\n"
                         f"--- STDOUT (last 2000 chars) ---\n{test_result.stdout[-2000:]}\n"
                         f"--- STDERR (last 2000 chars) ---\n{test_result.stderr[-2000:]}")
            raise RuntimeError(f"[{self.name}] Unit Test Summary: \nNo test report found at {surefire_report_path}")

    def run_full_test_code(self, namespace: str, workspace_root=None):
        """
        Run full unit test code
        1. mvn install -DskipTests
        2. mvn test
        """
        workspace_root = self._workspace_root(workspace_root)
        mvn_cmd = "mvn.cmd" if platform.system().lower() == "windows" else "mvn"
        install_cmd = [mvn_cmd, "clean", "install", "-DskipTests"]
        cwd = workspace_root / namespace / "backend"
        subprocess.run(
            args=install_cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        test_cmd = [mvn_cmd, "test"]
        test_cwd = workspace_root / namespace / "backend" / "admin"
        test_result = subprocess.run(
            args=test_cmd,
            cwd=test_cwd,
            capture_output=True,
            text=True,
        )
        surefire_report_path = workspace_root / namespace / "backend" / "admin" / "target" / "surefire-reports"

        if FileUtil.exists(file_path=surefire_report_path):
            summary = MavenTestResultUtil.parse_all_results(report_dir=surefire_report_path)
            logger.info(f"[{self.name}] Full Test Summary: \n{json.dumps(summary, indent=4)}\n")
            if summary["total_errors"] > 0:
                raise RuntimeError(f"[{self.name}] Full Test Failed with Errors.")
            return not (summary["total_failures"] > 0)
        else:
            # Log Maven output to help diagnose why no report was generated
            logger.error(f"[{self.name}] Maven test command failed, no report generated.\n"
                         f"--- STDOUT (last 2000 chars) ---\n{test_result.stdout[-2000:]}\n"
                         f"--- STDERR (last 2000 chars) ---\n{test_result.stderr[-2000:]}")
            raise RuntimeError(f"[{self.name}] Full Test Summary: \nNo test report found at {surefire_report_path}")
