#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path
import auto_full_stack


# Project root directory
ROOT = Path(auto_full_stack.__file__).parent

MAX_ITERATIONS = 3

# Log directory
LOG_PATH = ROOT.parent / 'logs'

# Results directory
DEFAULT_WORKSPACE_ROOT = ROOT.parent / "workspace"

# Container working directory
CONTAINER_WORKDIR = "/app"

