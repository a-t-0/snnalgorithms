"""Packaging logic for snnalgorithms."""
from __future__ import annotations

import os
import sys

import setuptools

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
# sys.path.insert(1, os.path.join(os.path.dirname(__file__), "tests"))

install_requires = [
    "lava @ https://github.com/a-t-0/lava/archive/refs/tags/v0.5.1.tar.gz",
]
setuptools.setup()
