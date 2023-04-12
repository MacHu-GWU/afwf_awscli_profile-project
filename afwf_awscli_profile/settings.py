# -*- coding: utf-8 -*-

import typing as T
import json
import dataclasses
from pathlib_mate import Path

from .paths import path_settings_json


@dataclasses.dataclass
class Settings:
    aws_profile: T.Optional[str] = dataclasses.field(default=None)
    aws_region: T.Optional[str] = dataclasses.field(default=None)
    session_hours: T.Optional[int] = dataclasses.field(default=12)
    overwrite_default: T.Optional[bool] = dataclasses.field(default=True)

    @classmethod
    def read(cls, path: Path = path_settings_json) -> "Settings":
        if path.exists():
            return Settings(**json.loads(path.read_text()))
        else:
            settings = cls()
            settings.write(path)
            return settings

    def write(self, path: Path = path_settings_json):
        path.write_text(json.dumps(dataclasses.asdict(self), indent=4))
