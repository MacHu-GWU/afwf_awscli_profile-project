# -*- coding: utf-8 -*-

import afwf
from ..paths import dir_python_lib

IAM_ICON = afwf.Icon.from_image_file(
    str(dir_python_lib.joinpath("icons", "iam-64.png"))
)
