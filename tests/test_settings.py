# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from pathlib_mate import Path
from afwf_awscli_profile.paths import path_settings_sqlite

def test():
    path_settings_sqlite.remove_if_exists()
    # print(path_settings_sqlite.exists())

    from afwf_awscli_profile.settings import settings
    # print(settings)


if __name__ == "__main__":
    from afwf_awscli_profile.tests import run_cov_test

    run_cov_test(__file__, "afwf_awscli_profile.settings", preview=False)
