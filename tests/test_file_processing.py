import logging
import socket

import requests
from click.testing import CliRunner

from osm.cli import rtransparent
from osm.converters import PDFConverter

from .utils import verify_xml_structure


def test_cli_rtransparent(
    pdf_setup, monkeypatch, mocked_requests_post, mocked_socket, caplog
):
    caplog.set_level(logging.INFO)
    sample, output = pdf_setup
    with monkeypatch.context() as m:
        m.setattr(requests, "post", mocked_requests_post)
        monkeypatch.setattr(socket, "socket", lambda *args, **kwargs: mocked_socket)
        result = CliRunner().invoke(rtransparent, [str(sample), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        assert f"Converted: {sample}" in caplog.text
        mocked_requests_post.assert_called_once()
        mocked_socket.connect.assert_called_once()


def test_pdf_converter(caplog, pdf_setup):
    sample, _ = pdf_setup

    response = PDFConverter().convert(sample)
    verify_xml_structure(response)
