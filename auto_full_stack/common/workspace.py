#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path

from auto_full_stack.common.const import DEFAULT_WORKSPACE_ROOT


def get_workspace_root(state: dict | None = None) -> Path:
    workspace_root = state.get("workspace_root") if state else None
    return Path(workspace_root) if workspace_root else DEFAULT_WORKSPACE_ROOT
