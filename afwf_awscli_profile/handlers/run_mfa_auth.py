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
            token=q.trimmed_parts[1],
        )

    def encode_query(self, profile: str, token: str) -> str:
        return f"{profile} {token}"

    def main(self, profile: str, token: str) -> afwf.ScriptFilter:
        awscli_config = AWSCliConfig(
            path_config=self.path_config,
            path_credentials=self.path_credentials,
        )
        settings = Settings.read()
        awscli_config.mfa_auth(
            profile=profile,
            mfa_code=token,
            hours=settings.session_hours,
            overwrite_default=settings.overwrite_default,
        )

        if settings.overwrite_default:
            new_profile = f"{profile}_mfa"
            settings.aws_profile = new_profile
            settings.write()

        return afwf.ScriptFilter()


handler = Handler(id="run_mfa_auth")
