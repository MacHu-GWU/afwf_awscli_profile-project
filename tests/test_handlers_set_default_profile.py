# -*- coding: utf-8 -*-

from pathlib_mate import Path
from afwf_awscli_profile.handlers.set_default_profile import Handler

dir_here = Path.dir_here(__file__)

handler = Handler(
    id="",
    path_config=dir_here.joinpath(".aws", "config"),
    path_credentials=dir_here.joinpath(".aws", "credentials"),
)


class TestHandler:
    def test(self):
        sf = handler.handler("")
        assert len(sf.items) == 3
        assert sf.items[0].autocomplete == "default"

        sf = handler.handler("company")
        assert len(sf.items) == 3
        assert sf.items[0].autocomplete == "company_abc_us_east_1"

        sf = handler.handler("xyz")
        assert len(sf.items) == 3
        assert sf.items[0].autocomplete == "group_xyz_us_east_2"


if __name__ == "__main__":
    from afwf_awscli_profile.tests import run_cov_test

    run_cov_test(
        __file__, "afwf_awscli_profile.handlers.set_default_profile", preview=False
    )
