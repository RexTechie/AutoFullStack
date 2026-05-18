#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/11/14 17:59
@Author  : Rex
@File    : name_rule_convert.py
"""

import re
class NameRuleConverter:
    """
    Name Rule Convert Tips: Upper Camel Case, Lower Camel Case and Snake Case
    @descript Upper Camel Case: First Letter of Each Word is Capitalized, also known as Pascal Case
    @descript Lower Camel Case: First letter of the first word is lowercase, and the first letter of each subsequent word is capitalized
    @descript Snake Case:  Each word is separated by an underscore
    """

    @staticmethod
    def to_snake_case(x):
        """
        To Snake Case
        """
        return re.sub(r'(?<=[a-z])[A-Z]|(?<!^)[A-Z](?=[a-z])', r'_\g<0>', x).lower()

    @staticmethod
    def snake_case_to_upper_camel_case(x):
        """
        Snake Case to Upper Camel Case
        """
        s = re.sub(r'_([a-zA-Z])', lambda m: m.group(1).upper(), x.lower())
        return s[0].upper() + s[1:]

    @staticmethod
    def upper_camel_case_to_lower_camel_case(x):
        """
        Upper Camel Case to Lower Camel Case
        """
        if not x:
            return x
        return x[0].lower() + x[1:]

    @staticmethod
    def snake_case_to_lower_camel_case(x):
        """
        Snake Case to Lower Camel Case
        """
        s = re.sub(r'_([a-zA-Z])', lambda m: m.group(1).upper(), x.lower())
        return s[0].lower() + s[1:]


# 示例用法
if __name__ == "__main__":
    example_str = "ExampleString"
    print(NameRuleConverter.to_snake_case(example_str))  # Output: example_string
    print(NameRuleConverter.snake_case_to_upper_camel_case(example_str))  # Output: ExampleString
    print(NameRuleConverter.upper_camel_case_to_lower_camel_case(example_str))  # Output: exampleString
