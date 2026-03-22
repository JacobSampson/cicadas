# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

"""
Cicadas: Sustainable, Spec-Driven Development (SDD) for human-AI teams.

Cicadas is a methodology toolset that reverses the traditional relationship
between code and documentation. Forward-looking specs (PRDs, plans) are
treated as disposable inputs that drive implementation and then expire.
Authoritative documentation is reverse-engineered from the code itself.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("aprovan-cicadas")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"
