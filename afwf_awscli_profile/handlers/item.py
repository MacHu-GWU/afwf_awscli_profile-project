# -*- coding: utf-8 -*-

import attr
import afwf

from ..fuzzy import Fuzzy

NAME_VAR_KEY = "fuzzy_match_name"


@attr.define
class Item(afwf.Item):
    def set_name(self, name: str) -> "Item":
        """
        Store the string of name in the alfred item variables. it is used for
        fuzzy matching and sorting.
        """
        self.variables[NAME_VAR_KEY] = name
        return self


class FuzzyItem(Fuzzy[Item]):
    def get_name(self, item: Item):
        return item.variables[NAME_VAR_KEY]
