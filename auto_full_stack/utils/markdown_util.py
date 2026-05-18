#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from auto_full_stack.common.log import logger


class MarkdownUtil:
    """
    Markdown parsing utility class
    """

    @staticmethod
    def parse_code_block(content: str, language: str) -> list[str]:
        """
        Parse the specific content in ```xxx {content} ```, only parse the outermost layer, and support parsing failure.
        :param content: Input text containing possible code blocks.
        :param language: Specify the language tag of the code block (e.g., 'python', 'json').
        :return: [str]: Parse successful content, if parsing fails, output the original string.
        """
        # Regex to match the outermost code block of the specified language
        pattern = rf"```{language}(.*?)```"

        # Return all matches of the code block content
        matches = re.findall(pattern, content, re.DOTALL)

        if not matches:
            logger.error(f"Failed to parse {language}: {content}")
            return [content]

        # Return all matched code block contents
        return [match.strip() for match in matches]


