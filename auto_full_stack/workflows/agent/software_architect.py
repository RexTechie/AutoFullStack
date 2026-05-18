#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/1 9:38
@Author  : Rex
@File    : software_architect.py
"""
from langchain_core.output_parsers import StrOutputParser

import json
from auto_full_stack.common.llm import model
from auto_full_stack.utils import PromptUtil, MarkdownUtil
from auto_full_stack.common.log import logger

class SoftwareArchitect:
    llm: None
    name = "🏗️ Software Architect"

    def __init__(self):
        self.llm = model | StrOutputParser()

    def draw_architecture_diagram(self, product_requirement: str):
        """
        Draw Architecture Diagram
        """
        prompt = PromptUtil.prompt_handle("planning_workflow/software_architect/architecture_diagram.templ", {
            "product_requirement": product_requirement
        })
        diagram_str = self.llm.invoke(prompt)
        diagram = MarkdownUtil.parse_code_block(diagram_str, "mermaid")[0]
        logger.info(f"[{self.name}] Architecture Diagram: \n{diagram}\n")
        return diagram

    def draw_class_diagram(self, product_requirement: str, architect_diagram: str):
        """
        Draw Class Diagram
        """
        prompt = PromptUtil.prompt_handle("planning_workflow/software_architect/class_diagram.templ", {
            "product_requirement": product_requirement,
            "architecture_diagram": architect_diagram
        })
        diagram_str = self.llm.invoke(prompt)
        diagram = MarkdownUtil.parse_code_block(diagram_str, "mermaid")[0]
        logger.info(f"[{self.name}] Class Diagram: \n{diagram}\n")
        return diagram

    def write_incremental_list(self, product_requirement: str, architect_diagram: str):
        """
        Analyze product requirements and architecture diagrams to write an incremental list in JSON format.
        Each incremental should include id, name, description, dependencies and priority.
        The first incremental should be "Basic Framework Setup" with id 1, no dependencies, and highest priority.
        """
        prompt = PromptUtil.prompt_handle("planning_workflow/software_architect/incremental_list.templ", {
            "product_requirement": product_requirement,
            "architecture_diagram": architect_diagram,
        })
        incremental_markdown = self.llm.invoke(prompt)
        incremental_str = MarkdownUtil.parse_code_block(incremental_markdown, "json")[0]
        logger.info(f"[{self.name}] Incremental List: \n{incremental_str}\n")
        return json.loads(incremental_str)

    def incremental_class_diagram_match(self, incremental_list: list, class_diagram: str):
        """
        Match Class Diagram for each Incremental.
        """
        inc_class_dict = {}
        for incremental in incremental_list:
            logger.info(f"[{self.name}] Incremental Class: \n{incremental}\n")
            if incremental["name"] == "Basic Framework Setup": # Basic Framework Setup does not need class diagram
                continue
            prompt = PromptUtil.prompt_handle("planning_workflow/software_architect/incremental_class_diagram_match.templ", {
                "incremental": json.dumps(incremental, indent=2, ensure_ascii=False),
                "class_diagram": class_diagram
            })
            match_markdown = self.llm.invoke(prompt)
            match_class_diagram = MarkdownUtil.parse_code_block(match_markdown, "mermaid")[0]
            inc_class_dict[incremental["id"]] =  match_class_diagram
        logger.info(f"[{self.name}] Incremental Class Diagram Match: \n{inc_class_dict}\n")
        return inc_class_dict
