#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/4 15:16
@Author  : Rex
@File    : operations_engineer.py
"""
import platform
import subprocess
import json
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser

from auto_full_stack.utils import FileUtil, MavenTestResultUtil
from auto_full_stack.utils.mysql_util import MySQLUtil
from auto_full_stack.common.const import DEFAULT_WORKSPACE_ROOT
from auto_full_stack.common.llm import model
from auto_full_stack.common.log import logger

class OperationsEngineer:
    llm = None
    name = "🛠️ Operations Engineer"

    def __init__(self):
        self.llm = model | StrOutputParser

    def _workspace_root(self, workspace_root=None):
        return Path(workspace_root) if workspace_root else DEFAULT_WORKSPACE_ROOT

    def init_database(self, namespace:str, workspace_root=None):
        """
        Initialize Database(MySQL)
        """
        workspace_root = self._workspace_root(workspace_root)
        sql_path = workspace_root / namespace / "sql"
        resources_path = workspace_root / namespace / "resources"
        # 0. Create Database
        MySQLUtil.drop_database(database=namespace)
        MySQLUtil.create_database(namespace)
        # 1. Init Database
        quartz_sql_path = sql_path / "quartz.sql"
        init_sql_path = sql_path / "init.sql"
        MySQLUtil.execute_sql_by_file(
            script_path=quartz_sql_path,
            database=namespace
        )
        MySQLUtil.execute_sql_by_file(
            script_path=init_sql_path,
            database=namespace
        )
        # 2. Read incremental list
        incremental_list_path = resources_path / "incremental_list.json"
        incremental_list = FileUtil.read_file(file_path=incremental_list_path)
        json.loads(incremental_list)
        for incremental in json.loads(incremental_list):
            if incremental.get("id", None) is None or incremental.get("id", None) == 1:
                continue
            module_name = incremental.get("module_name", None)
            create_table_sql = sql_path / f"create_tables_inc_{module_name}.sql"
            MySQLUtil.execute_sql_by_file(
                script_path=create_table_sql,
                database=namespace
            )
            insert_menu_sql = sql_path / f"insert_menu_inc_{module_name}.sql"
            MySQLUtil.execute_sql_by_file(
                script_path=insert_menu_sql,
                database=namespace
            )
        logger.info(f"[{self.name}] Database Initialized Successfully.")

        return

    def test_backend_project(self, namespace:str, workspace_root=None):
        """
        Test Backend Project(Spring Boot + Maven)
        """
        workspace_root = self._workspace_root(workspace_root)
        mvn_cmd = "mvn.cmd" if platform.system().lower() == "windows" else "mvn"
        cwd = workspace_root / namespace / "backend"
        cmd = [mvn_cmd, "clean", "test"]
        logger.info(f"[{self.name}] Test Backend Project Command: {cmd}")
        logger.info(f"[{self.name}] 🧪 Testing Backend Project...")
        subprocess.run(
            args=cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        surefire_report_path = workspace_root / namespace / "backend" / "admin" / "target" / "surefire-reports"
        if FileUtil.exists(file_path=surefire_report_path):
            summary = MavenTestResultUtil.parse_all_results(report_dir=surefire_report_path)
            logger.info(f"[{self.name}] All Test Summary: \n{json.dumps(summary, indent=4)}\n")
        else:
            logger.info(f"[{self.name}] port Found at {surefire_report_path}")

        logger.info(f"[{self.name}] 🧪 Test Backend Project Finished.")

    def build_backend_project(self, namespace:str, workspace_root=None):
        """
        Build Backend Project(Spring Boot + Maven)
        The result path is: {namespace}/backend/admin/target/admin.jar
        """
        workspace_root = self._workspace_root(workspace_root)
        mvn_cmd = "mvn.cmd" if platform.system().lower() == "windows" else "mvn"
        cwd = workspace_root / namespace / "backend"
        cmd = [mvn_cmd, "package", "-DskipTests"]
        logger.info(f"[{self.name}] Build Backend Project Command: {cmd}")

        process = subprocess.Popen(
            args=cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        logger.info(f"[{self.name}] Build Backend Project Process PID: {process.pid}")
        logger.info(f"[{self.name}] 🏗️ Building Backend Project...")
        return cmd, process

    def run_backend_project(self, namespace:str, workspace_root=None):
        """
        Run Backend Project(Spring Boot + Maven)
        """
        workspace_root = self._workspace_root(workspace_root)
        cwd = workspace_root / namespace / "backend"
        cmd = ["java", "-Dfile.encoding=UTF-8", "-Dconsole.encoding=UTF-8", "-jar", "admin/target/admin.jar"]
        logger.info(f"[{self.name}] Run Backend Project Command: {' '.join(cmd)}")

        process = subprocess.Popen(
            args=cmd,
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=	subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        logger.info(f"[{self.name}] Run Backend Project Process PID: {process.pid}")
        logger.info(f"[{self.name}] 🚀 Starting Backend Project...")
        return cmd, process

    def frontend_install_dependencies(self, namespace:str, workspace_root=None):
        """
        Install Frontend Dependencies(Vue + Vite + Node)
        """
        workspace_root = self._workspace_root(workspace_root)
        npm_cmd = "npm.cmd" if platform.system().lower() == "windows" else "npm"
        cwd = workspace_root / namespace / "frontend"
        cmd = [npm_cmd, "install", "--registry=https://registry.npmmirror.com"]
        logger.info(f"[{self.name}] Install Frontend Dependencies Command: {cmd}")

        process = subprocess.Popen(
            args=cmd,
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        logger.info(f"[{self.name}] Install Frontend Dependencies Process PID: {process.pid}")
        logger.info(f"[{self.name}] 📦 Installing Frontend Dependencies...")
        return cmd, process

    def run_frontend(self, namespace:str, workspace_root=None):
        """
        Run Frontend Project(Vue + Vite + Node)
        """
        workspace_root = self._workspace_root(workspace_root)
        npm_cmd = "npm.cmd" if platform.system().lower() == "windows" else "npm"
        cwd = workspace_root / namespace / "frontend"
        cmd = [npm_cmd, "run", "dev"]
        logger.info(f"[{self.name}] Run Frontend Project Command: {cmd}")

        process = subprocess.Popen(
            args=cmd,
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        logger.info(f"[{self.name}] Run Frontend Project Process PID: {process.pid}")
        logger.info(f"[{self.name}] 🚀 Starting Frontend Project...")
        return cmd, process
