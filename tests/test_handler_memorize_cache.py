# -*- coding: utf-8 -*-

import os
import pytest
from afwf_awscli_profile.handlers.memorize_cache import handler


def test():
    sf1 = handler.main("key")
    sf2 = handler.main("key")
    assert sf1.items[0].title == sf2.items[0].title


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
