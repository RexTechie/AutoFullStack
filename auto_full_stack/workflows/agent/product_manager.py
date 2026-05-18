#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/1 9:38
@Author  : Rex
@File    : product_manager.py
"""
from langchain_core.output_parsers import StrOutputParser

from auto_full_stack.common.llm import model
from auto_full_stack.utils import PromptUtil, MarkdownUtil
from auto_full_stack.common.log import logger

class ProductManager:
    llm = None
    name = "👩‍💼 Product Manager"

    def __init__(self):
        self.llm = model | StrOutputParser()

    def write_prd(self, project_name: str, project_description):
        """
        Write Product Requirement Document
        """
        prompt = PromptUtil.prompt_handle("planning_workflow/product_manager/product_requirement.templ", {
            "project_name": project_name,
            "project_description": project_description
        })
        prd = self.llm.invoke(prompt)
        prd = MarkdownUtil.parse_code_block(prd, language="markdown")[0]
        logger.info(f"[{self.name}] Product Requirement Document: \n{prd}\n")
        return prd
