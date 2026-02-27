"""
Project-wide structured logging helper.

Provides a single `get_logger` function so every module can obtain a
consistent logger without reconfiguring logging repeatedly.
"""

from __future__ import annotations

import logging
import sys
from typing import Optional


def _configure_root_logger(level: int = logging.INFO) -> None:
    if logging.getLogger().handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Return a module-specific logger.
    """
    _configure_root_logger()
    return logging.getLogger(name or "strider")


__all__ = ["get_logger"]

