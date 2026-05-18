#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/18 22:26
@Author  : Rex
@File    : maven_test_report_util.py.py
"""
import json

import os
import xml.etree.ElementTree as ET
from auto_full_stack.common.log import logger


class MavenTestResultUtil:

    @staticmethod
    def parse_test_result(xml_file_path: str) -> dict:
        """
        Parse a single Maven Surefire/Failsafe XML result file.
        :param xml_file_path: Path to XML result file
        :return: A dictionary with test case summary and test case details
        """
        if not os.path.exists(xml_file_path):
            logger.error(f"Test result file {xml_file_path} not found")
            return {}

        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()

            suite_summary = {
                "case": root.attrib.get("name", ""),
                "tests": int(root.attrib.get("tests", 0)),
                "failures": int(root.attrib.get("failures", 0)),
                "errors": int(root.attrib.get("errors", 0)),
                "skipped": int(root.attrib.get("skipped", 0)),
                "time": float(root.attrib.get("time", 0)),
                "failure_details": []
            }

            # Extract failure/error messages from each testcase
            for testcase in root.findall("testcase"):
                test_name = testcase.attrib.get("name", "unknown")
                failure = testcase.find("failure")
                error = testcase.find("error")
                if failure is not None:
                    suite_summary["failure_details"].append({
                        "test": test_name,
                        "type": "failure",
                        "message": failure.attrib.get("message", "")[:200],
                    })
                if error is not None:
                    suite_summary["failure_details"].append({
                        "test": test_name,
                        "type": "error",
                        "message": error.attrib.get("message", "")[:200],
                    })

            return suite_summary
        except Exception as e:
            logger.error(f"Error parsing test result {xml_file_path}: {e}")
            return {}

    @staticmethod
    def parse_all_results(report_dir: str) -> dict:
        """
        Parse all Maven Surefire/Failsafe XML result files under a directory.
        :param report_dir: Directory containing test result XML files
        :return: A dictionary with aggregated results
        """
        if not os.path.exists(report_dir):
            logger.error(f"Report directory {report_dir} not found")
            return {}

        summary = {
            "total_tests": 0,
            "total_failures": 0,
            "total_errors": 0,
            "total_skipped": 0,
            "total_time": 0.0,
            "total_failure_details": []
        }


        for file in os.listdir(report_dir):
            if file.startswith("TEST-") and file.endswith(".xml"):
                xml_path = os.path.join(report_dir, file)
                suite_result = MavenTestResultUtil.parse_test_result(xml_path)
                if suite_result:
                    summary["total_tests"] += suite_result["tests"]
                    summary["total_failures"] += suite_result["failures"]
                    summary["total_errors"] += suite_result["errors"]
                    summary["total_skipped"] += suite_result["skipped"]
                    summary["total_time"] += suite_result["time"]
                    summary["total_failure_details"].extend(suite_result["failure_details"])

        return summary