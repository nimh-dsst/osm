import logging
import shutil
import socket
from pathlib import Path

import pytest
import requests
from click.testing import CliRunner

from osm.cli import extract_metrics
from osm.sciencebeam import PDFConverter

from .utils import verify_xml_structure

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("rpy2")


def test_cli_metrics(
    tmp_path, monkeypatch, mocked_requests_post, mocked_socket, caplog
):
    # set up temp dir
    tmp_pdfs = tmp_path / "pdfs"
    tmp_pdfs.mkdir()
    sample = shutil.copy2(
        Path("docs/examples/pdf_inputs/test_sample.pdf"), tmp_pdfs / "test_sample.pdf"
    )
    # (tmp_pdfs / sample).symlink_to(pdfs_dir / sample)

    with monkeypatch.context() as m:
        caplog.set_level(logging.INFO)
        m.setattr(requests, "post", mocked_requests_post)
        monkeypatch.setattr(socket, "socket", lambda *args, **kwargs: mocked_socket)
        result = CliRunner().invoke(extract_metrics, [str(tmp_pdfs), str(tmp_path)])
        if result.exit_code != 0:
            logger.error("Command failed with exit code %s", result.exit_code)
            logger.error("Output:\n%s", result.output)
            raise result.exception
        assert list(tmp_path.rglob("*txt"))[0].name == sample.with_suffix(".txt").name
        mocked_requests_post.assert_called_once()
        mocked_socket.connect.assert_called_once()


@pytest.mark.run_slow
def test_cli_metrics_oddpub(tmp_path):
    # set up temp dir
    tmp_pdfs = tmp_path / "pdfs"
    tmp_pdfs.mkdir()
    sample = shutil.copy2(
        Path("docs/examples/pdf_inputs/test_sample.pdf"), tmp_pdfs / "test_sample.pdf"
    )

    result = CliRunner().invoke(
        extract_metrics, [str(tmp_pdfs), str(tmp_path), "--parse-with-oddpub"]
    )
    if result.exit_code != 0:
        logger.error("Command failed with exit code %s", result.exit_code)
        logger.error("Output:\n%s", result.output)
        raise result.exception
    assert list(tmp_path.rglob("*txt"))[0].name == sample.with_suffix(".txt").name


def test_pdf_converter(sample_pdf):
    sample, _ = sample_pdf

    response = PDFConverter().convert(sample)
    verify_xml_structure(response)
