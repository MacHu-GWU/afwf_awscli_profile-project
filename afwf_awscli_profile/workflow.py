# -*- coding: utf-8 -*-

import afwf

from .handlers import (
    run_set_default_profile,
    run_mfa_auth,
    set_default_profile,
    mfa_auth,
    view_or_edit_settings,
)

wf = afwf.Workflow()
wf.register(run_set_default_profile.handler)
wf.register(run_mfa_auth.handler)
wf.register(set_default_profile.handler)
wf.register(mfa_auth.handler)
wf.register(view_or_edit_settings.handler)
