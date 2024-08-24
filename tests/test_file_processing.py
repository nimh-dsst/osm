import pytest


@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = tmp_path / "test_sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%Test PDF content\n")
    yield pdf_path
    pdf_path.unlink()
