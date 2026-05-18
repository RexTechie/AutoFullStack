#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/8 11:39
@Author  : Rex
@File    : app_only_run_proj.py
"""
import uuid

from auto_full_stack.common.log import logger
from auto_full_stack.workflows.operations_workflow import operations_workflow, OperationsState

if __name__ == '__main__':
    logger.info("Welcome to the Full Stack Agent Flow Application!")
    config = {
        "configurable": {"thread_id": "1"},
        "recursion_limit": 10
    }
    result = operations_workflow.invoke({
        "project_id": uuid.uuid4().hex,
        "project_namespace": "personal_contact_manager",
        "reset_database": True
    }, config)
    while True:
        pass