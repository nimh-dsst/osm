import os


def get_version():
    try:
        from . import _version

        return _version.version
    except ImportError:
        generate_version_file()
        from . import _version

        return _version.version


def generate_version_file():
    import pkg_resources

    if os.getenv("SETUPTOOLS_SCM_PRETEND_VERSION_FOR_OSM"):
        version = os.getenv("SETUPTOOLS_SCM_PRETEND_VERSION_FOR_OSM")
    else:
        version = pkg_resources.get_distribution("osm").version
    version_file_content = f"version = '{version}'\n"

    version_file_path = os.path.join(os.path.dirname(__file__), "_version.py")
    with open(version_file_path, "w") as version_file:
        version_file.write(version_file_content)


__version__ = get_version()
