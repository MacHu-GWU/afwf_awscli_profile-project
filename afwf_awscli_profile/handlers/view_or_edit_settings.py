# -*- coding: utf-8 -*-

import afwf
import attr
from pathlib_mate import Path
from ..paths import path_settings_json
from ..settings import Settings


@attr.define
class Handler(afwf.Handler):
    def parse_query(self, query: str):
        return dict()

    def main(self) -> afwf.ScriptFilter:
        sf = afwf.ScriptFilter()
        settings = Settings.read()
        item = afwf.Item(
            title="View or Edit settings for awscli profile Alfred Workflow",
            subtitle=f"open {path_settings_json.abspath}",
            arg=path_settings_json.abspath,
            icon=afwf.Icon.from_image_file(afwf.IconFileEnum.gear),
        )
        item.open_file(path=path_settings_json.abspath)
        sf.items.append(item)
        return sf


handler = Handler(id="view_or_edit_settings")
