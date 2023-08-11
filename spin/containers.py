import collections


class DotDict(collections.UserDict):
    def __getitem__(self, key):
        subitem = self.data
        for subkey in key.split("."):
            try:
                subitem = subitem[subkey]
            except KeyError:
                raise KeyError(f"`{key}` not found in configuration") from None
        return subitem

    # Fix for Python 3.12
    # See https://github.com/python/cpython/issues/105524
    def __contains__(self, key):
        subitem = self.data
        for subkey in key.split("."):
            try:
                subitem = subitem[subkey]
            except KeyError:
                return False
        return True
