# PyMuPDF PDF Text Extraction Unit Tests

This repository holds unit tests for the **PDF text extraction** atomic protocol. The tests exercise PyMuPDF's `Page.get_text("text")` call using small, synthetic PDFs created in memory. The citable source is the [PyMuPDF Page.get_text() documentation](https://pymupdf.readthedocs.io/en/latest/page.html#Page.get_text).

## Contract

| | Type | Description |
|---|---|---|
| **Input** | PyMuPDF `Document` / `Page` | A PDF document opened from bytes and a page selected for extraction |
| **Output** | `str` | Extracted page text; an empty string for a blank page or an image-only page without OCR |

```python
with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
    result = doc[0].get_text("text")
```

## Tested versions

The unit tests specify these target versions:

- PyMuPDF 1.26.7
- pytest 9.0.2

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the tests

Save the test code in `Session_6_Unit_Test.py`, then run:

```bash
python -m pytest -v Session_6_Unit_Test.py
```

The filename is supplied explicitly because `Session_6_Unit_Test.py` does not match pytest's default test file naming patterns.

Expected result after correcting the blank-page fixture described below: **9 passed**. The special-character test runs four times, once for each parameter.

## What the tests cover

- **Typical input:** extraction returns a Python string containing the expected grant requirement text.
- **Blank pages:** a page with no text returns an empty string.
- **Multiple lines:** both lines of a two-line input appear in the extracted text.
- **Image-only pages:** words embedded in an image are not extracted by the plain text call.
- **Special characters:** `$`, `–`, `≥`, and `%` are preserved in the synthetic PDF fixture.
- **Invalid input:** opening non-PDF bytes as a PDF raises `pymupdf.FileDataError`.

## Known limitations and test correction

The supplied `test_blank_page_returns_empty_string()` inserts `"12"` into its PDF, so the page is not blank even though the assertion expects an empty string. Replace:

```python
pdf_bytes = _make_text_pdf("12")
```

with:

```python
pdf_bytes = _make_text_pdf("")
```

The image-only test does not perform OCR. The suite checks synthetic, single-page fixtures; it does not establish behavior for complex layouts, reading order, encrypted PDFs, or arbitrary fonts. The multiline test checks that both lines are present, without asserting their exact formatting or order.
