# -*- coding: utf-8 -*-

from pathlib_mate import Path
from afwf_awscli_profile.settings import Settings

dir_here = Path.dir_here(__file__)
path_settings_json = dir_here.joinpath("test-settings.json")


def test():
    path_settings_json.remove_if_exists()

    settings = Settings.read(path_settings_json)
    settings.session_hours = 24
    settings.write(path_settings_json)

    settings = Settings.read(path_settings_json)
    assert settings.session_hours == 24


if __name__ == "__main__":
    from afwf_awscli_profile.tests import run_cov_test

    run_cov_test(__file__, "afwf_awscli_profile.settings", preview=False)
