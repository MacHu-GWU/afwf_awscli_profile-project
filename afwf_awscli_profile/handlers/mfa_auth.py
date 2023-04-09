# -*- coding: utf-8 -*-

import typing as T
import sys

import afwf
import attr
from pathlib_mate import Path
from awscli_mate import AWSCliConfig
from awscli_mate.paths import path_config, path_credentials

from ..cache import cache
from ..icons import IAM_ICON
from .item import Item, FuzzyItem
from .run_mfa_auth import handler as run_mfa_auth_handler


@attr.define
class Handler(afwf.Handler):
    path_config: Path = attr.field(default=path_config)
    path_credentials: Path = attr.field(default=path_credentials)

    def parse_query(self, query: str):
        q = afwf.QueryParser(delimiter=list(" ")).parse(query)
        return dict(q=q)

    @cache.typed_memoize(expire=30)
    def read_profile_and_region_pairs(self) -> T.List[T.Tuple[str, str]]:
        awscli_config = AWSCliConfig(
            path_config=self.path_config,
            path_credentials=self.path_credentials,
        )
        config, _ = awscli_config.read_config()
        profile_and_region_pairs = list()
        for section_name, section in config.items():
            # extract the profile name
            # we don't want the configparser's DEFAULT section
            # and also we don't want to use the default profile as the base profile
            if not section_name.startswith("profile "):
                continue

            profile = section_name[8:]

            # extract the region name
            region = section.get("region", "unknown-region")

            profile_and_region_pairs.append((profile, region))
        return profile_and_region_pairs

    def list_profiles(
        self,
        profile_and_region_pairs: T.List[T.Tuple[str, str]],
    ) -> T.List[Item]:
        items = list()
        for profile, region in profile_and_region_pairs:
            # create alfred items
            item = Item(
                title=f"{profile} | {region}",
                subtitle=f"use this base profile for MFA auth",
                autocomplete=f"{profile} ",
                arg=profile,
                icon=IAM_ICON,
            ).set_name(profile)
            items.append(item)
        return items

    def select_profiles(
        self,
        items: T.List[Item],
        text: str,
    ) -> T.List[Item]:
        """ """
        return FuzzyItem.from_items(items).sort(text)

    ask_for_mfa_token_subtitle = "Hit 'Enter' to read the official doc"

    def ask_for_mfa_token(
        self,
        profile: str,
    ) -> T.List[Item]:
        """
        :param profile: the selected profile name.
        """
        item = Item(
            title=f"MFA with {profile!r}, enter your six digit MFA token ...",
            subtitle=self.ask_for_mfa_token_subtitle,
        )

        item.open_url(url="https://repost.aws/knowledge-center/authenticate-mfa-cli")
        return [item]

    entering_mfa_token_subtitle = "continue to enter your six digit MFA token ..."

    def entering_mfa_token(
        self,
        profile: str,
        token: str,
    ) -> T.List[Item]:
        item = Item(
            title=f"MFA with {profile!r} + {token!r} ...",
            subtitle=self.entering_mfa_token_subtitle,
        )
        return [item]

    run_mfa_auth_subtitle = "Hit 'Enter' to run it ..."

    def run_mfa_auth(
        self,
        profile: str,
        token: str,
    ) -> T.List[Item]:
        cmd = run_mfa_auth_handler.encode_run_script_command(
            bin_python=sys.executable,
            profile=profile,
            token=token,
        )
        afwf.log_debug_info(f"will run command: {cmd}")
        item = Item(
            title=f"MFA with {profile!r} + {token!r} ...",
            subtitle=self.run_mfa_auth_subtitle,
            arg=cmd,
            icon=afwf.Icon.from_image_file(afwf.IconFileEnum.bash),
        )
        item.run_script(cmd=cmd)
        item.send_notification(
            title=f"aws cli MFA with:",
            subtitle=f"base profile = {profile!r}\nnew profile = '{profile}__mfa'",
        )
        return [item]

    entered_invalid_token_subtitle = "Hit 'Tab' to re-enter your six digit MFA token"

    def entered_invalid_token(
        self,
        profile: str,
        token: str,
    ):
        item = Item(
            title=f"{token!r} is NOT a valid six digit MFA token!",
            subtitle=self.entered_invalid_token_subtitle,
            autocomplete=f"{profile} ",
            icon=afwf.Icon.from_image_file(afwf.IconFileEnum.error),
        )
        return [item]

    def main(self, q: afwf.Query) -> afwf.ScriptFilter:
        sf = afwf.ScriptFilter()
        profile_and_region_pairs = self.read_profile_and_region_pairs()
        profiles = {profile for profile, _ in profile_and_region_pairs}
        items = self.list_profiles(profile_and_region_pairs)
        # example:
        # - ""
        # - "    "
        if len(q.trimmed_parts) == 0:
            sf.items.extend(items)
        # example:
        # - "profile_name"
        # - "profile_substr"
        elif len(q.trimmed_parts) == 1:
            if q.trimmed_parts[0] in profiles:
                sf.items.extend(self.ask_for_mfa_token(profile=q.trimmed_parts[0]))
            else:
                sf.items.extend(self.select_profiles(items, text=q.trimmed_parts[0]))
        elif len(q.trimmed_parts) == 2:
            profile, token = q.trimmed_parts
            # see below
            if profile in profiles:
                # see below
                if token.isdigit():
                    # - "profile 123"
                    if len(token) < 6:
                        sf.items.extend(self.entering_mfa_token(profile, token))
                    # - "profile 123456"
                    elif len(token) == 6:
                        sf.items.extend(self.run_mfa_auth(profile, token))
                    # - "profile 123456789"
                    elif len(token) >= 6:
                        sf.items.extend(self.entered_invalid_token(profile, token))
                    else:  # pragma: no cover
                        raise NotImplementedError
                # - "profile abc"
                else:
                    sf.items.extend(self.entered_invalid_token(profile, token))
            # - "alice bob"
            else:
                sf.items.extend(
                    self.select_profiles(items, text=" ".join(q.trimmed_parts))
                )
        # example:
        # - "profile sub str"
        # - "profile sub str 123456"
        elif len(q.trimmed_parts) >= 3:
            profile = q.trimmed_parts[0]
            if profile in profiles:
                sf.items.extend(
                    self.entered_invalid_token(
                        profile, token=" ".join(q.trimmed_parts[1:])
                    )
                )
            else:
                sf.items.extend(
                    self.select_profiles(items, text=" ".join(q.trimmed_parts))
                )
        else:  # pragma: no cover
            raise NotImplementedError

        if len(sf.items) == 0:  # pragma: no cover
            sf.items.append(
                Item(
                    title="Error!",
                    subtitle="query = " + " ".join(q.trimmed_parts),
                    icon=afwf.Icon.from_image_file(afwf.IconFileEnum.error),
                )
            )
        return sf


handler = Handler(id="mfa_auth")
