# -*- coding: utf-8 -*-

import afwf
import attr
from pathlib_mate import Path

from awscli_mate import AWSCliConfig
from awscli_mate.paths import path_config, path_credentials

from ..settings import Settings


@attr.define
class Handler(afwf.Handler):
    path_config: Path = attr.field(default=path_config)
    path_credentials: Path = attr.field(default=path_credentials)

    def parse_query(self, query: str):
        q = afwf.QueryParser(delimiter=" ").parse(query)
        return dict(
            profile=q.trimmed_parts[0],
        )

    def encode_query(self, profile: str) -> str:
        return profile

    def main(self, profile: str) -> afwf.ScriptFilter:
        awscli_config = AWSCliConfig(
            path_config=self.path_config,
            path_credentials=self.path_credentials,
        )
        awscli_config.set_profile_as_default(profile)

        settings = Settings.read()
        settings.aws_profile = profile
        settings.write()

        return afwf.ScriptFilter()


handler = Handler(id="run_set_default_profile")
