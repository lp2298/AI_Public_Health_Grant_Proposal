# Grant application review workflow

This command-line prototype reviews an existing grant application against funder guidelines. It uses AI to extract requirements and assess evidence, then asks the applicant to accept or decline each proposed text change. The applicant must verify all results and decide whether to approve the application. The program does not submit it.

## Setup

Install dependencies with `python3 -m pip install -r requirements.txt`, install the Codex CLI, and sign in to Codex. The workflow starts a separate `codex exec` session for each analysis step; it does not reuse the conversation open in your IDE. Use `--model` only if you need to override your configured Codex model. Usage depends on your Codex account and plan.

```sh
python3 workflow.py \
  --guidelines "test_documents/Community_Health_Improvement_Grant_Guidelines.pdf" \
  --application "test_documents/Community_Health_Access_Grant_Application (1).pdf" \
  --organization "test_documents/Community_Wellness_Alliance_Organizational_Policies.pdf"
```

Add `--supporting budget.pdf letters.txt` for optional supporting documents. Inputs must be PDF or UTF-8 TXT, with distinct file names. The application, organization information and policies, and guidelines are required. Before processing, remove unnecessary sensitive information and review the provider's privacy policies. The program requests consent before processing text with Codex, including any evidence added later. Codex still uses an AI model, and document text is sent to the configured provider; this is not offline processing.

The applicant confirms or corrects extracted funding opportunity details, verifies the guidelines and checklist, can add evidence and repeat the assessment, and accepts or declines each suggested change. The program only applies an accepted change when its original passage occurs exactly once. It writes `revised_application.txt` and `review.json` in `output/workflow/` by default; these files are overwritten on subsequent runs. The report includes the checklist, evidence map, assessments, decisions, and approval. Approval records a SHA-256 hash of the reviewed text. Editing after approval invalidates the hash; the assessment also will not reflect edits made after it ran. Approval does not submit the application.

## Limits

PDF extraction uses PyMuPDF. Pages with fewer than 30 extracted characters are flagged as potentially scanned; run OCR externally and review the result before retrying. This heuristic can flag sparse pages and cannot detect all OCR errors. The output is plain text: layout, font, margins, spacing, page counts and PDF submission format require manual verification, and no formatted PDF/DOCX is produced. The program does not guarantee a submission-ready package or eligibility. AI can miss requirements, misunderstand documents, or suggest inaccurate changes even when quotations are valid. Check the official funder documents and every recommendation. References are checked for exact quotations, not for semantic correctness. It does not support links or Word input.

## Tests

Run the full test suite with `python3 -m unittest discover -s tests -v`. The GitHub Actions workflow currently runs `tests/test_workflow.py`.

Use fictional examples in a public repository. Documents and output can contain sensitive information. `output/`, environment files and Python caches are ignored by Git; review staged files before publishing, including files in `test_documents/`. Output is plain text without encryption or access controls.
