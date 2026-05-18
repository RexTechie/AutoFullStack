import uuid
import argparse

from auto_full_stack.common.log import logger
from auto_full_stack.workflows.incremental_main_workflow import incremental_main_workflow
from auto_full_stack.workflows.incremental_no_self_refinement_main_workflow import (
    incremental_no_self_refinement_main_workflow,
)
from auto_full_stack.workflows.waterfall_main_workflow import waterfall_main_workflow


DEFAULT_PROJECT_NAME = "Personal Contact Manager"
DEFAULT_PROJECT_DESCRIPTION = (
    "Please help me create a personal contact management system. This system includes "
    "a contact management module. Contact management enables users to add, edit, "
    "delete and view contact information. Contacts contain information such as name, "
    "phone number, email address, and address."
)

WORKFLOWS = {
    "incremental": incremental_main_workflow,
    "incremental_no_self_refinement": incremental_no_self_refinement_main_workflow,
    "waterfall": waterfall_main_workflow,
}


def parse_args():
    parser = argparse.ArgumentParser(description="Run AutoFullStack on a single project requirement.")
    parser.add_argument(
        "--project-name",
        default=DEFAULT_PROJECT_NAME,
        help="Project name used by AutoFullStack.",
    )
    parser.add_argument(
        "--description",
        default=DEFAULT_PROJECT_DESCRIPTION,
        help="Natural language project requirement.",
    )
    parser.add_argument(
        "--approach",
        choices=sorted(WORKFLOWS.keys()),
        default="incremental",
        help="Workflow variant to run.",
    )
    return parser.parse_args()



if __name__ == "__main__":
    args = parse_args()
    logger.info("Welcome to the Full Stack Agent Flow Application!")
    logger.info(f"Running approach: {args.approach}")
    config = {
        "configurable": {"thread_id": "1"},
        "recursion_limit": 100
    }
    workflow = WORKFLOWS[args.approach]
    result = workflow.invoke({
        "project_id": uuid.uuid4().hex,
        "project_name": args.project_name,
        "project_description": args.description,
    }, config)
