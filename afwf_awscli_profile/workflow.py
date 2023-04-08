# -*- coding: utf-8 -*-

import afwf

from .handlers import (
    set_default_profile,
)

wf = afwf.Workflow()
wf.register(set_default_profile.handler)
