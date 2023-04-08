# -*- coding: utf-8 -*-

import afwf
import attr
from pathlib_mate import Path
from awscli_mate import AWSCliConfig
from awscli_mate.paths import path_config, path_credentials

from ..cache import cache
from ..icons import IAM_ICON
from .item import Item, FuzzyItem

@attr.define
class Handler(afwf.Handler):
    path_config: Path = attr.field(default=path_config)
    path_credentials: Path = attr.field(default=path_credentials)

    def parse_query(self, query: str):
        q = afwf.QueryParser(delimiter=list(" -_")).parse(query)
        return dict(q=q)

    @cache.typed_memoize(expire=30)
    def get_items_from_aws_cli_config(self):
        awscli_config = AWSCliConfig(
            path_config=self.path_config,
            path_credentials=self.path_credentials,
        )
        config, credentials = awscli_config.read_config()

        items = list()
        for section_name, section in config.items():
            # the python configparser always has a DEFAULT section
            # we don't want it
            if section_name == "DEFAULT":
                continue

            # extract the profile name
            if section_name.startswith("profile "):
                profile = section_name[8:]
            else:
                profile = section_name

            # extract the region name
            region = section.get("region", "unknown-region")

            # create alfred items
            item = Item(
                title=f"{profile} | {region}",
                subtitle=f"set {profile!r} as the default profile",
                autocomplete=profile,
                arg=profile,
                icon=IAM_ICON,
            ).set_name(profile)
            item.send_notification(
                title=f"Set AWS CLI default profile",
                subtitle=f"profile = {profile!r}\nregion = {region!r}",
            )
            items.append(item)
        return items

    def main(self, q: afwf.Query) -> afwf.ScriptFilter:
        sf = afwf.ScriptFilter()
        items = self.get_items_from_aws_cli_config()
        # example:
        # - ""
        # - "    "
        if len(q.trimmed_parts) == 0:
            sf.items.extend(items)
        # example:
        # - "  any query would be fine  "
        else:
            sf.items.extend(
                FuzzyItem.from_items(items).sort(" ".join(q.trimmed_parts))
            )
        return sf

handler = Handler(id="set_default_profile")
