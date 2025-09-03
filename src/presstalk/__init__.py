try:
    from importlib.metadata import version

    __version__ = version("presstalk")
except ImportError:
    __version__ = "unknown"

__all__ = ["__version__"]
