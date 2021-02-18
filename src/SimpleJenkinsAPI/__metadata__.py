import sys
from importlib import import_module


# importlib.metadata is implemented in Python 3.8
# Previous versions require the backport, https://pypi.org/project/importlib-metadata/
if sys.version_info >= (3, 7):
    metadata = import_module("importlib.metadata")
else:
    metadata = import_module("importlib_metadata")

__data = metadata.metadata(__name__.split(".")[0])

name = __data.get("Name", "Unknown")
version = __data.get("Version", "0.0.0")
description = __data.get("Summary", "")
homepage = __data.get("Home-page", "")
