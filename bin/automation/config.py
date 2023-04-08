# -*- coding: utf-8 -*-

"""
Automation config management.
"""

import dataclasses
from pathlib_mate import Path


@dataclasses.dataclass
class AutomationConfig:
    python_version: str = dataclasses.field()
    dir_workflow: Path = dataclasses.field()


config = AutomationConfig(
    python_version="3.8",
    dir_workflow=Path(
        "/Users/sanhehu/Documents/Alfred-Preferences/Alfred.alfredpreferences/workflows/user.workflow.3F6BACFA-4BEA-45A6-81FE-3597BB70AE39"
    ),
)
