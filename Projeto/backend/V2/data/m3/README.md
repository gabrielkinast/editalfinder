# EditalFinder V2 — M3.0 controlled real-document pilot

Dataset: m3.0-pilot-v1
Protocol: m3.0-annotation-v1
Temporal reference day: 2026-10-19 (explicit civil day)
Review: PROVISIONAL AI-assisted labels only, not authenticated human ground truth.
Scope: forward-looking discovery of fomento, crédito and investimentos. No
historical-editais quota. News can be positive, future-facing, ambiguous or
non-actionable depending on its scoped evidence, not its document type.

## Authoritative files

* corpus_manifest.json: complete acquired-document provenance; stable document
  IDs, original/final URLs, UTC retrieval timestamps, types, filenames, lengths,
  original SHA-256, derived-view SHA-256, authority/limitations and category proof.
* annotation_protocol.md: rubric, annotation levels, evidence contract, conservative
  time policy, review governance and alignment to existing M1/M2 terminology.
* annotations/records.json: machine-readable PROVISIONAL record/field references.
* annotations/REFERENCE_LABELS.md: human-readable rendering of the same labels,
  evidence IDs, locators, quotes, rationale, fields and uncertainties.
* raw/: untrusted exact HTTP response entity bytes (HTML/PDF), stored once.
* text/: deterministic passive text views for reading/span references; these are
  derived artifacts, NOT replacements for original downloaded documents.
* provenance/: selected transport headers, acquisition/failure logs, selection
  decisions and tools. Draft per-batch curation is not an independently approved
  reference source; corpus_manifest.json and annotations/records.json prevail.
* evaluation/M31_PREPARATION.md: separate future tasks, metrics, split/review
  prerequisites and acceptance artifacts; M3.1 is NOT started.
* evaluation/verification.json: executed quality-gate records and tool versions.
* evaluation/coverage.json: programmatically counted corpus/label distributions;
  counts describe this purposive pilot, not population prevalence or model quality.

Manifest null publication dates/versions mean unverified, not a guessed date or
version. An HTML and PDF referring to one program retain separate document IDs
and hashes. Record IDs are not canonical opportunity IDs. No production sources,
SQL catalogs, canonical identifiers or database entities are created here.

## Offline verification (from backend/V2)

    PYTHONPATH=src .venv/bin/python -B -m editalfinder_v2.dataset_m30 data/m3
    .venv/bin/python -B -m pytest -p no:cacheprovider -q
    .venv/bin/ruff check --no-cache src tests
    .venv/bin/ruff format --check --no-cache src tests
    .venv/bin/mypy --no-incremental --cache-dir=/dev/null src
    git diff --check

The verifier performs NO network access, model predictions, domain integration,
publication or persistence. It refuses invalid annotations; it does not silently
repair them. It verifies evidence traceability and structural contradictions,
NOT semantic truth, human approval, source authorship, source license or current
online availability. Exact field strings are not canonical normalized values.
All test/gate assertions refer to recorded executions in the M30 report, not to
historic baseline claims. Synthetic mutation fixtures are explicitly separate
from the real corpus; no generated document fills its quota.

## Reading evidence safely

Do not execute raw HTML/PDF embedded content or follow arbitrary embedded URLs.
Use frozen text and inspect the original passively. HTML evidence offsets are
[start,end) Unicode codepoints in the exact UTF-8 text view; script/style/
noscript/template data are excluded, but menus/hidden text can remain. No DOM
rendering or opportunity extraction is implied. PDF page numbers are physical,
1-based, with formfeed-delimited pdftotext output. View hashes are checked
separately from original response hashes. Do not regenerate text in place while
retaining old offsets.

unit_locator limits each evaluated record. This is not exhaustive annotation of
every menu, footer, related-story card or linked attachment. Unannotated content is
out of scope, not negative. A quote's presence does not prove its interpretation;
the human-readable rationale and authorized review must establish entailment.

## Reproduction and future revisions

Offline reproducibility uses the stored originals plus exact view/manifest/label
hashes; no live re-download is required. provenance/freeze_selected.py documents
the explicitly bounded HTTPS fetch/passive derivation helper used in curation,
not a recursive crawler or production acquisition service. No credentials/forms
are used. Selected URL lists and errors preserve acquisition decisions. The
helper refuses existing document IDs and restricts hosts/types/size/redirects;
no arbitrary CLI crawling entry point is provided. HTML conversion is stdlib;
PDF text conversion uses the already installed Poppler binary, whose actual
version is recorded. A website update may legitimately change bytes and hashes.
Any authorized reacquisition must use a NEW dataset directory/version with new
retrieval metadata and re-annotation, never overwrite this release. Automatic
re-fetching, source enumeration, rate-limit circumvention and unrestricted
crawling are outside scope.

No unrestricted redistribution license is inferred from public availability.
Public institutional contacts/attribution may remain in original documents;
applicant personal records are not a selection target. Review restrictions
before sharing raw files outside this controlled local pilot.

## Review and readiness

No approved human reference labels exist in this release. The four known review
statuses are protocol vocabulary, but the initial schema only admits provisional
because no approved review-authority artifact exists. AI peer review cannot
change that. See the protocol for independent blind review/adjudication and a
future explicit schema extension bound to approved review evidence.

READY in EDITALFINDER_V2_M30_RESULTADOS.md, if assigned after verification, means
only complete dataset PREPARATION for the controlled offline pilot. It does not
certify label truth, extraction accuracy, recall, authenticated review, source
readiness or production suitability. No predictions, precision/recall scores,
automatic promotion, merges, Supabase writes, deployment, commits or staging.
Stop after M3.0 and await technical review; do not start M3.1 automatically.
