import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import workflow


class NewWorkflowTests(unittest.TestCase):
    def test_finds_vscode_codex_when_not_on_path(self):
        with tempfile.TemporaryDirectory() as directory:
            cli = Path(directory) / '.vscode/extensions/openai.chatgpt-1/bin/macos-aarch64/codex'
            cli.parent.mkdir(parents=True)
            cli.write_text('')
            cli.chmod(0o755)
            with patch.dict('os.environ', {}, clear=True), patch.object(Path, 'home', return_value=Path(directory)), \
                 patch('workflow.shutil.which', return_value=None), patch('workflow.platform.system', return_value='Darwin'), \
                 patch('workflow.platform.machine', return_value='arm64'):
                self.assertEqual(workflow.find_codex(), str(cli))

    def test_only_unique_approved_passage_can_be_replaced(self):
        self.assertEqual(workflow.apply_recommendation('old text', 'old', 'new'), 'new text')
        for text, passage in [('old old', 'old'), ('different', 'old'), ('text', '')]:
            with self.assertRaises(ValueError):
                workflow.apply_recommendation(text, passage, 'new')

    def test_text_read_and_empty_detection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.txt'
            path.write_text('Evidence for a grant', encoding='utf-8')
            document = workflow.read_document(path)
            self.assertEqual(document.pages, ['Evidence for a grant'])
            workflow.require_readable([document])
            path.write_text('', encoding='utf-8')
            with self.assertRaises(ValueError):
                workflow.require_readable([workflow.read_document(path)])

    def test_scanned_pdf_page_stops_workflow(self):
        document = workflow.Document('scan.pdf', [''], [1])
        with self.assertRaisesRegex(ValueError, 'OCR'):
            workflow.require_readable([document])

    def test_source_reference_must_match_document_page_and_quote(self):
        doc = workflow.Document('proof.txt', ['An exact supporting quotation.'], [])
        item = SimpleNamespace(references=[SimpleNamespace(document='proof.txt', page=1, quote='exact supporting quotation')])
        workflow.check_references([item], [doc])
        item.references[0].quote = 'fabricated quotation'
        with self.assertRaises(ValueError):
            workflow.check_references([item], [doc])
        item.references[0].quote = 'exact supporting quotation'
        item.references[0].page = 2
        with self.assertRaises(ValueError):
            workflow.check_references([item], [doc])

    def test_revised_text_corrects_pdf_page_number_when_quote_matches(self):
        doc = workflow.Document('revised_application.txt', ['Page 2\nEvidence'], [])
        ref = SimpleNamespace(document=doc.name, page=2, quote='Evidence')
        workflow.check_references([SimpleNamespace(references=[ref])], [doc])
        self.assertEqual(ref.page, 1)

    def test_explicit_consent(self):
        with patch('builtins.input', side_effect=['invalid', 'no']):
            self.assertFalse(workflow.ask_yes('Send?'))


if __name__ == '__main__':
    unittest.main()
