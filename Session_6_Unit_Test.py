"""
Protocol: PyMuPDF PDF text extraction

Citable source:
PyMuPDF Page.get_text() documentation:
https://pymupdf.readthedocs.io/en/latest/page.html

Input -> output contract:
PyMuPDF PDF Document/Page -> extracted page text as a Python str
using Page.get_text("text").

Package versions these tests were written for:
PyMuPDF==1.26.7
pytest==9.0.2
"""

import pytest
import pymupdf


def _make_text_pdf(text="", fontname="helv"):
    """Create a small synthetic PDF fixture using documented PyMuPDF APIs."""
    doc = pymupdf.open()
    page = doc.new_page()

    if text:
        y = 72
        for line in text.split("\n"):
            page.insert_text((72, y), line, fontname=fontname)
            y += 20

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def _make_image_only_pdf():
    """Create a PDF whose visible words exist only inside an embedded image."""
    source_doc = pymupdf.open()
    source_page = source_doc.new_page(width=300, height=100)
    source_page.insert_text((20, 50), "Grant requirement")
    pixmap = source_page.get_pixmap()

    target_doc = pymupdf.open()
    target_page = target_doc.new_page(width=300, height=100)
    target_page.insert_image(target_page.rect, pixmap=pixmap)

    pdf_bytes = target_doc.tobytes()

    target_doc.close()
    source_doc.close()
    return pdf_bytes


def test_output_datatype():
    pdf_bytes = _make_text_pdf(
        "Grant requirement: Applicants must be nonprofit organizations."
    )

    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
        result = doc[0].get_text("text")

    assert isinstance(result, str)
    assert result.strip() == (
        "Grant requirement: Applicants must be nonprofit organizations."
    )


def test_blank_page_returns_empty_string():
    pdf_bytes = _make_text_pdf("")

    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
        result = doc[0].get_text("text")

    assert result == ""


def test_multiline_text_extraction():
    pdf_bytes = _make_text_pdf(
        "Eligibility Requirements\nApplicants must qualify."
    )

    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
        result = doc[0].get_text("text")

    assert "Eligibility Requirements" in result
    assert "Applicants must qualify." in result


def test_image_only_pdf_returns_no_text():
    pdf_bytes = _make_image_only_pdf()

    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
        result = doc[0].get_text("text")

    assert result == ""
    assert "Grant requirement" not in result


@pytest.mark.parametrize("expected_character", ["$", "–", "≥", "%"])
def test_special_characters_are_preserved(expected_character):
    pdf_bytes = _make_text_pdf(
        "Funding range: $50,000–$100,000; match ≥ 10%.",
        fontname="china-s",
    )

    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
        result = doc[0].get_text("text")

    assert expected_character in result


def test_non_pdf_file_raises():
    invalid_pdf_bytes = b"This is not a PDF."

    with pytest.raises(pymupdf.FileDataError):
        pymupdf.open(stream=invalid_pdf_bytes, filetype="pdf")
