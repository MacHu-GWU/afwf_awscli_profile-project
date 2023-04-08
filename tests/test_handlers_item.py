# -*- coding: utf-8 -*-

from afwf_awscli_profile.handlers.item import Item, FuzzyItem


def test():
    names = [
        "alice bob",
        "cathy david",
    ]
    items = [Item(title=name).set_name(name) for name in names]
    fuzzy = FuzzyItem.from_items(items)

    items = fuzzy.match("alice")
    assert len(items) == 1
    assert items[0].title == "alice bob"

    items = fuzzy.match("cathy")
    assert len(items) == 1
    assert items[0].title == "cathy david"

    items = fuzzy.sort("alice")
    assert len(items) == 2
    assert items[0].title == "alice bob"

    items = fuzzy.sort("cathy")
    assert len(items) == 2
    assert items[0].title == "cathy david"


if __name__ == "__main__":
    from afwf_awscli_profile.tests import run_cov_test

    run_cov_test(__file__, "afwf_awscli_profile.handlers.item", preview=False)
