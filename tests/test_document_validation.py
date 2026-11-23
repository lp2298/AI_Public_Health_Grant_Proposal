import tempfile
import unittest
from pathlib import Path

import pymupdf
import workflow


class TestDocumentValidation(unittest.TestCase):
    def test_extracts_text_from_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'application.pdf'
            pdf = pymupdf.open()
            pdf.new_page().insert_text((72, 72), 'A complete fictional grant application with sufficient text.')
            pdf.save(path)
            pdf.close()
            document = workflow.read_document(path)
            self.assertIn('fictional grant application', document.pages[0])
            self.assertEqual(document.scanned_pages, [])
            workflow.require_readable([document])

    def test_flags_image_only_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'scan.pdf'
            pdf = pymupdf.open()
            pdf.new_page()
            pdf.save(path)
            pdf.close()
            document = workflow.read_document(path)
            self.assertEqual(document.scanned_pages, [1])
            with self.assertRaisesRegex(ValueError, 'OCR'):
                workflow.require_readable([document])

    def test_rejects_unsupported_input(self):
        with self.assertRaisesRegex(ValueError, 'Unsupported file type'):
            workflow.read_document(Path('application.docx'))
