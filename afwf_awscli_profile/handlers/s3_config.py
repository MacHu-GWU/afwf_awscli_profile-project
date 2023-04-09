# -*- coding: utf-8 -*-

"""
"""

import typing as T
import enum

import afwf
import attr
from pathlib_mate import Path
from awscli_mate import AWSCliConfig
from awscli_mate.paths import path_config, path_credentials

from ..settings import settings
from ..fuzzy import Fuzzy


class ActionEnum(str, enum.Enum):
    list_subcommands = "list_subcommands"
    get_config = "get_config"
    list_set_config_options = "list_set_config_options"
    set_config = "set_config"
    handle_error = "handle_error"


class FuzzyItem(Fuzzy[afwf.Item]):
    def get_name(self, item: afwf.Item):
        return item.match


@attr.define
class Handler(afwf.Handler):
    path_config: Path = attr.field(default=path_config)
    path_credentials: Path = attr.field(default=path_credentials)

    def parse_query(self, query: str):
        q = afwf.QueryParser().parse(query)
        # example:
        # - ""
        # - "    "
        if len(q.trimmed_parts) == 0:
            return dict(q=q, action=ActionEnum.list_subcommands)
        # example:
        # - "SubCommandSubString"
        # - "SubCommandSubString    "
        elif q.trimmed_parts[0] not in ["get", "set"]:
            return dict(q=q, action=ActionEnum.list_subcommands)
        # example:
        # - "get"
        # - "get    "
        # - "get    something"
        # - "get    something    "
        elif q.trimmed_parts[0] == "get":
            return dict(q=q, action=ActionEnum.get_config)
        elif q.trimmed_parts[0] == "set":
            # example:
            # - "set"
            # - "set    "
            if len(q.trimmed_parts) == 1:
                return dict(q=q, action=ActionEnum.list_set_config_options)
            # example:
            # - "set    something_weird"
            # - "set    something    werid"
            # - "set    something    werid    "
            elif q.trimmed_parts[1] not in [
                "aws_profile",
                "aws_region",
                "cache_expire",
                "max_results",
            ]:
                return dict(q=q, action=ActionEnum.list_set_config_options)
            # example:
            # - "set    aws_profile"
            # - "set    aws_profile    "
            # - "set    aws_profile    some thing"
            # - "set    aws_profile    some thing    "
            else:  # pragma: no cover
                return dict(q=q, action=ActionEnum.set_config)
        else:  # pragma: no cover
            return dict(q=q, action=ActionEnum.handle_error)

    def list_subcommands(self, sf: afwf.ScriptFilter, q: afwf.Query):
        items = [
            afwf.Item(
                title="get (s3-config get)",
                subtitle="get current config",
                autocomplete="get",
                arg="get",
                match="get",
                icon=afwf.Icon.from_image_file(afwf.IconFileEnum.gear),
            ),
            afwf.Item(
                title="set (s3-config set <key> <value>)",
                subtitle="set config values",
                autocomplete="set ",
                arg="set",
                match="set",
                icon=afwf.Icon.from_image_file(afwf.IconFileEnum.gear),
            ),
        ]
        if len(q.trimmed_parts):
            if "set".startswith(q.trimmed_parts[0]):
                sf.items.extend(items[::-1])
            else:
                sf.items.extend(items)
        else:
            sf.items.extend(items)

    def _get_config_items(self) -> T.List[afwf.Item]:
        return [
            afwf.Item(
                title=f"{name} = {value}",
                subtitle=f"use 's3-config set {key} <{key}>' (hit 'Tab') to change it",
                autocomplete=f"set {key} ",
                arg=str(value),
                match=key,
                icon=afwf.Icon.from_image_file(afwf.IconFileEnum.gear),
            )
            for value, name, key in [
                (settings.aws_profile, "AWS profile", "aws_profile"),
                (settings.aws_region, "AWS region", "aws_region"),
                (settings.cache_expire, "Cache expire", "cache_expire"),
                (settings.max_results, "Max results", "max_results"),
            ]
        ]

    def get_config(self, sf: afwf.ScriptFilter, q: afwf.Query):
        items = self._get_config_items()
        if len(q.trimmed_parts) == 1:
            sf.items.extend(items)
        else:
            fuzzy = FuzzyItem.from_items(items)
            items = fuzzy.sort(" ".join(q.trimmed_parts[1:]), threshold=0)
            sf.items.extend(items)

    def _list_set_config_items(self) -> T.List[afwf.Item]:
        return [
            afwf.Item(
                title=f"{name} = {value}",
                subtitle=f"use 's3-config set {key} <{key}>' (hit 'Tab') to change it",
                autocomplete=f"set {key} ",
                arg=str(value),
                match=key,
                icon=afwf.Icon.from_image_file(afwf.IconFileEnum.gear),
            )
            for value, name, key in [
                (settings.aws_profile, "AWS profile", "aws_profile"),
                (settings.aws_region, "AWS region", "aws_region"),
                (settings.cache_expire, "Cache expire", "cache_expire"),
                (settings.max_results, "Max results", "max_results"),
            ]
        ]

    def list_set_config_options(self, sf: afwf.ScriptFilter, q: afwf.Query):
        items = self._list_set_config_items()
        if len(q.trimmed_parts) == 1:
            sf.items.extend(items)
        else:
            fuzzy = FuzzyItem.from_items(items)
            items = fuzzy.sort(" ".join(q.trimmed_parts[1:]), threshold=0)
            sf.items.extend(items)

    def _get_aws_profile_items(self) -> T.List[afwf.Item]:
        awscli_config = AWSCliConfig(
            path_config=self.path_config,
            path_credentials=self.path_credentials,
        )
        config, credentials = awscli_config.read_config()
        items = list()
        for section_name, section in config.items():
            if section_name == "DEFAULT":
                continue
            if section_name.startswith("profile "):
                profile = section_name[8:]
            else:
                profile = section_name
            region = section.get("region", "unknown-region")
            item = afwf.Item(
                title=f"{profile} | {region}",
                subtitle=f"set {profile!r} as the default profile for afwf_s3",
                autocomplete=f"set aws_profile {profile}",
                arg=profile,
                match=profile,
                icon=afwf.Icon.from_image_file(afwf.IconFileEnum.fire),
            )
            items.append(item)
        return items

    def set_config(self, sf: afwf.ScriptFilter, q: afwf.Query):
        if q.trimmed_parts[1] == "aws_profile":
            items = self._get_aws_profile_items()
            if len(q.trimmed_parts) == 2:
                sf.items.extend(items)
            else:
                fuzzy = FuzzyItem.from_items(items)
                items = fuzzy.sort(" ".join(q.trimmed_parts[2:]), threshold=0)
                sf.items.extend(items)
        # todo: add aws_region, cache_expire, max_results logic
        else:
            pass

    def main(self, q: afwf.Query, action: ActionEnum) -> afwf.ScriptFilter:
        sf = afwf.ScriptFilter()
        if action is ActionEnum.list_subcommands:
            self.list_subcommands(sf, q)
        elif action is ActionEnum.get_config:
            self.get_config(sf, q)
        elif action is ActionEnum.list_set_config_options:
            self.list_set_config_options(sf, q)
        elif action is ActionEnum.set_config:
            self.set_config(sf, q)
        elif action is ActionEnum.handle_error:
            pass
        else:  # pragma: no cover
            pass

        return sf


handler = Handler(id="s3_config")
