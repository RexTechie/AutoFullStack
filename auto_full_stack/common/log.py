#!/usr/bin/env python
# -*- coding: utf-8 -*-
from loguru import logger
import sys

from auto_full_stack.common.const import LOG_PATH

# Log directory
log_path = LOG_PATH
log_path.mkdir(exist_ok=True)

# Log format
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

# Remove default logger
logger.remove()

# Add console logger
logger.add(sys.stdout, level="INFO", format=LOG_FORMAT, enqueue=True)

# Add file logger with rotation and compression
logger.add(
    log_path / "app_{time:YYYYMMDD}.log",
    level="INFO",
    format=LOG_FORMAT,
    rotation="00:00",  # Update every day
    compression="gz",  # Log compression format
    encoding="utf-8",
    enqueue=True
)
