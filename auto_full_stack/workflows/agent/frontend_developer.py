#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/1 9:38
@Author  : Rex
@File    : frontend_developer.py
"""

import json

from langchain_core.output_parsers import StrOutputParser

from auto_full_stack.common.llm import model
from auto_full_stack.common.const import ROOT
from auto_full_stack.utils import PromptUtil, MarkdownUtil, FileUtil, NameRuleConverter
from auto_full_stack.common.log import logger


class FrontendDeveloper:
    llm=None
    name = "👩‍💻 Frontend Developer"

    def __init__(self):
        self.llm = model | StrOutputParser()

    def write_api_code(self, module_name: str):
        """
        Write API Code
        """
        prompt = PromptUtil.prompt_handle("coding_workflow/frontend_developer/api.templ", {
            "module": module_name,
            "moduleName": NameRuleConverter.to_snake_case(module_name),
            "example": FileUtil.read_file(ROOT / "workflows" / "prompt" / "coding_workflow/frontend_developer/examples/api.js.example")
        })
        api_code = self.llm.invoke(prompt)
        api_code = MarkdownUtil.parse_code_block(api_code, language="javascript")[0]
        logger.info(f"[{self.name}] API Code: \n{api_code}\n")
        return api_code

    def write_page_code(self, module_name: str, incremental: dict, class_diagram: str, api_code: str):
        """
        Write Page Code
        """
        prompt = PromptUtil.prompt_handle("coding_workflow/frontend_developer/view.templ", {
            "moduleName": NameRuleConverter.to_snake_case(module_name),
            "incremental": json.dumps(incremental),
            "classDiagram": class_diagram,
            "apiCode": api_code,
            "apiPath": NameRuleConverter.to_snake_case(incremental["module_name"]),
            "example": FileUtil.read_file(ROOT / "workflows" / "prompt" / "coding_workflow/frontend_developer/examples/view.vue.example")
        })
        page_code = self.llm.invoke(prompt)
        page_code = MarkdownUtil.parse_code_block(page_code, language="vue")[0]
        logger.info(f"[{self.name}] Page Code: \n{page_code}\n")
        return page_code