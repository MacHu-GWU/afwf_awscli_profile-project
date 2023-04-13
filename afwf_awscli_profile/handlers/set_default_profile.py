# -*- coding: utf-8 -*-

import sys

import afwf
from afwf.opt.fuzzy_item import Item, FuzzyItem
import attr
from pathlib_mate import Path
from awscli_mate import AWSCliConfig
from awscli_mate.paths import path_config, path_credentials

from ..cache import cache
from ..icons import IAM_ICON
from .run_set_default_profile import handler as run_set_default_profile_handler
from .help import get_help_item


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
            # extract the profile name
            # we don't want the configparser's DEFAULT section
            # and also we don't want to use the default profile as the base profile
            if not section_name.startswith("profile "):
                continue

            profile = section_name[8:]

            # extract the region name
            region = section.get("region", "unknown-region")

            # create alfred items
            cmd = run_set_default_profile_handler.encode_run_script_command(
                bin_python=sys.executable,
                profile=profile,
            )
            # afwf.log_debug_info(f"will run command: {cmd}")
            item = Item(
                title=f"{profile} | {region}",
                subtitle=f"set {profile!r} as the default profile",
                autocomplete=profile,
                icon=IAM_ICON,
            ).set_fuzzy_match_name(profile)
            item.run_script(cmd=cmd)
            item.arg = profile
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
            if q.trimmed_parts[0].startswith("?"):
                sf.items.append(get_help_item())
            else:
                sf.items.extend(
                    FuzzyItem.from_items(items).sort(" ".join(q.trimmed_parts))
                )
        return sf


handler = Handler(id="set_default_profile")
