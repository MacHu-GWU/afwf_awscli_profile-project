# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from sqlitedict import SqliteDict
from dataclasses_sqlitedict import SingleTableDataModel

from .paths import path_settings_sqlite


@dataclasses.dataclass
class Settings(SingleTableDataModel):
    aws_profile: T.Optional[str] = dataclasses.field(default=None)
    aws_region: T.Optional[str] = dataclasses.field(default=None)
    cache_expire: T.Optional[int] = dataclasses.field(default=60)
    max_results: T.Optional[int] = dataclasses.field(default=20)


# read from existing settings
if path_settings_sqlite.exists():  # pragma: no cover
    db = SqliteDict(path_settings_sqlite.abspath, autocommit=False)
    settings = Settings.read(db)
# set default settings
else:  # pragma: no cover
    db = SqliteDict(path_settings_sqlite.abspath, autocommit=False)
    settings = Settings(db=db)
    settings.write()
