import os
import sys

__all__ = ["echo", "example_sum"]
__version__ = "0.0.0dev0"


def _enable_sharedlib_loading():
    basedir = os.path.dirname(__file__)
    subdir = os.path.join(basedir, "submodule")
    if os.name == "nt":
        os.add_dll_directory(subdir)
    elif sys.platform == "cygwin":
        os.environ["PATH"] = f'os.environ["PATH"]{os.pathsep}{subdir}'


_enable_sharedlib_loading()


from ._core import echo, example_sum  # noqa: E402
