import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import workflow


class WorkflowTests(unittest.TestCase):
    def test_missing_required_arguments_stops_before_running(self):
        with patch.object(sys, 'argv', ['workflow.py']), patch.object(workflow, 'run') as run, \
             contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                workflow.main()
        self.assertEqual(error.exception.code, 2)
        run.assert_not_called()

    def test_declining_consent_never_invokes_codex(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for name in ('guidelines.txt', 'application.txt', 'organization.txt'):
                path = Path(directory) / name
                path.write_text('Fictional document with content.', encoding='utf-8')
                paths.append(str(path))
            args = SimpleNamespace(guidelines=paths[0], application=paths[1],
                                   organization=paths[2], supporting=[], model=None,
                                   output=str(Path(directory) / 'output'))
            with patch.object(workflow, 'ask_yes', return_value=False), \
                 patch.object(workflow.subprocess, 'run') as codex, \
                 contextlib.redirect_stdout(io.StringIO()):
                workflow.run(args)
            codex.assert_not_called()
            self.assertFalse(Path(args.output).exists())

    def test_reference_from_unknown_document_rejected(self):
        doc = workflow.Document('actual.txt', ['Evidence'], [])
        ref = SimpleNamespace(document='unknown.txt', page=1, quote='Evidence')
        with self.assertRaisesRegex(ValueError, 'Invalid source reference'):
            workflow.check_references([SimpleNamespace(references=[ref])], [doc])
