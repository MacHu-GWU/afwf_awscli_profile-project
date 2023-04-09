Welcome to ``afwf_awscli_profile`` document
==============================================================================
This project is a `Alfred Workflow <https://www.alfredapp.com/workflows/>`_ that manipulate your AWS CLI profiles.

Features:

- Full text search your aws named profiles, set given one as the default (by editing the ~/.aws files). This allows you to switch between different AWS profiles easily.
- Do MFA authentication for a given AWS CLI. For example, suppose that you have a base profile ``my_work``, it will automatically create a ``my_work_mfa`` profile and set it as the default.
