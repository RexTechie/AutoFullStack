#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/11/27 21:33
@Author  : Rex
@File    : prompt_util.py
"""
from string import Template
from auto_full_stack.common.const import ROOT

class PromptUtil:
    """
    Prompt utility class
    """

    @staticmethod
    def prompt_handle(prompt_path, *args):
        """
        Read prompt file content and replace placeholders
        :param prompt_path: prompt file path
        :param args: Prompt content to be replaced
        """
        with open(ROOT / "workflows" / "prompt" / prompt_path, 'r', encoding='utf-8') as file:
            prompt_template = Template(file.read())

        prompt = prompt_template.substitute(*args)
        return prompt
