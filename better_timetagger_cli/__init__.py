# set __version__ dynamically
# fmt:off
def __getattr__(name):
    if name == "__version__":
        from importlib.metadata import version
        return version(__name__)
    return super().__getattr__(name)
# fmt:on
