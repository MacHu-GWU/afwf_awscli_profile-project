# -*- coding: utf-8 -*-

import typing as T
from pathlib_mate import Path
from afwf_awscli_profile.handlers.mfa_auth import Handler, Item


dir_here = Path.dir_here(__file__)

handler = Handler(
    id="",
    path_config=dir_here.joinpath(".aws", "config"),
    path_credentials=dir_here.joinpath(".aws", "credentials"),
)


class TestHandler:
    def assert_list_profiles(self, items: T.List[Item]):
        assert len(items) == 2
        assert items[0].autocomplete == "company_abc_us_east_1 "

    def assert_select_profile(self, items: T.List[Item], query: str):
        assert len(items) == 2
        assert query.split(" ")[0] in items[0].autocomplete
        assert items[0].autocomplete[-1] == " "

    def assert_ask_for_token(self, items: T.List[Item]):
        assert len(items) == 1
        assert items[0].subtitle == handler.ask_for_mfa_token_subtitle

    def assert_entering_mfa_token(self, items: T.List[Item]):
        assert len(items) == 1
        assert items[0].subtitle == handler.entering_mfa_token_subtitle

    def assert_run_mfa_auth(self, items: T.List[Item]):
        assert len(items) == 1
        assert items[0].subtitle == handler.run_mfa_auth_subtitle
        print(items[0].variables)

    def assert_entered_invalid_token(self, items: T.List[Item]):
        assert len(items) == 1
        assert items[0].subtitle == handler.entered_invalid_token_subtitle

    def test(self):
        sf = handler.handler("")
        self.assert_list_profiles(sf.items)

        for query in [
            "company",
            "xyz",
            "company abc",
            "company abc us-east-1",
        ]:
            sf = handler.handler(query)
            self.assert_select_profile(sf.items, query)

        for query in [
            "company_abc_us_east_1",
            "company_abc_us_east_1 ",
        ]:
            sf = handler.handler(query)
            self.assert_ask_for_token(sf.items)

        for query in [
            "company_abc_us_east_1 123",
            "company_abc_us_east_1 123 ",
        ]:
            sf = handler.handler(query)
            self.assert_entering_mfa_token(sf.items)

        for query in [
            "company_abc_us_east_1 123456",
            "company_abc_us_east_1 123456 ",
        ]:
            sf = handler.handler(query)
            self.assert_run_mfa_auth(sf.items)

        for query in [
            "company_abc_us_east_1 123456789",
            "company_abc_us_east_1 abc",
            "company_abc_us_east_1 abc xyz ",
        ]:
            sf = handler.handler(query)
            self.assert_entered_invalid_token(sf.items)


if __name__ == "__main__":
    from afwf_awscli_profile.tests import run_cov_test

    run_cov_test(
        __file__,
        "afwf_awscli_profile.handlers.mfa_auth",
        preview=False,
    )
