'''
Author: Rex rexhub@163.com
Date: 2025-11-11 17:12:52
LastEditors: Rex rexhub@163.com
LastEditTime: 2026-05-15 09:42:37
FilePath: \AutoFullStack\auto_full_stack\common\const.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
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

