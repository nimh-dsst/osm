import subprocess as sp


def test_run_ruff_check():
    sp.check_output(["ruff", "check", "osm"])


def test_run_ruff_format():
    sp.check_output(["ruff", "format", "--check", "osm"])
