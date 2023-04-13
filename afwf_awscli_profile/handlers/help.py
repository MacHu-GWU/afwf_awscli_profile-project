# -*- coding: utf-8 -*-

import afwf

def get_help_item() -> afwf.Item:
    return afwf.Item(
        title="Read afwf_awscli_profile Alfred Workflow Manual",
        subtitle="hit 'Enter' to read the manual",
        icon=afwf.Icon.from_image_file(afwf.IconFileEnum.idea),
    ).open_url("https://github.com/MacHu-GWU/afwf_awscli_profile-project")
