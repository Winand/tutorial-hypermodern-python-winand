"""The hypermodern Python project."""

from importlib.metadata import PackageNotFoundError, version  # type: ignore


try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    # tried to get version of the package but it's not installed in environment
    __version__ = "unknown"
