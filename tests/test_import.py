# -*- coding: utf-8 -*-

import os
import pytest
import afwf_awscli_profile


def test_import():
    _ = afwf_awscli_profile.wf


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
