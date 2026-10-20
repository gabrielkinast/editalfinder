# M3.0 annotation protocol — m3.0-annotation-v1

Status: AI-assisted PROVISIONAL reference annotations. No human ground truth,
authorized reviewer, adjudication, signature, approval or production taxonomy is
claimed. This protocol implements the forward-looking product scope update,
which supersedes the earlier requirement to collect historical calls.

## 1. Selection and target of judgment

EditalFinder discovers fomento, crédito and investimentos, including instruments
on product pages, official communications and investment programs. Sample
purposefully, not randomly: a small bounded pilot, not a prevalence estimate or
representative sample of all opportunities. Prefer current/upcoming instruments,
access descriptions, forthcoming announcements, meaningful signals and difficult
non-actionable controls. Do not fill quotas with expired calls. An old publication
date alone does not make an evergreen instrument historical; a previous document
is admissible only if it interprets a current instrument. Absence of a verified
future announcement must be reported as a gap, not filled with invented content.

Official/primary hosting is a source-authority observation, not proof of truth,
cryptographic authorship, website permission for redistribution, institutional
readiness or applicant accessibility. Search results are discovery aids only.
Read selected final documents directly, freeze original bytes and annotate only
what can be traced to the frozen material. No recursively followed links, browser
scripts, authentication, CAPTCHA workarounds, submissions or external writes.

## 2. Existing terminology and non-competing annotation layer

Authorities remain docs/v2/DECISIONS_V1.md, DATA_CONTRACT.md, SOURCE_SCOPE.md,
IDENTITY_M21.md, SEMANTIC_NORMALIZATION_M22A.md / M22B.md,
INTEGRATION_AUDIT_REPROCESSING.md, INTEGRATION_CONSISTENCY_M23B.md and the
M23C_FROZEN_ORACLE.md. New labels here are dataset vocabulary ONLY.

* Source: collection portal/context, not automatically publisher or funder.
* Dataset document: local stable M30-* ID for one selected response entity.
  It is not an opportunity identity, production source UUID or canonical URL.
* Raw copy: exact downloaded response entity bytes. Original SHA-256 is a
  content fingerprint, not a semantic ID or authenticated chain of custody.
* RawSnapshot in M1/M2: immutable sanitized JSON text with UUID, source and
  execution context. Its sha256-utf8-v1 digest is NOT the HTTP/PDF byte hash here.
  The corpus does not construct or impersonate RawSnapshot objects.
* Candidate: existing OpportunityCandidate asserts fields for one structural
  DocumentUnit. Corpus record annotations are NOT automatically candidates.
* Record scope: one located announcement/program/event in a document. A corpus
  text-span locator is not an RFC6901 DocumentUnit pointer. A future explicit
  reviewed adapter must bind original -> derived text -> structured snapshot ->
  candidate -> field evidence, preserving the original byte digest separately.
* Evidence: existing domain evidence binds a snapshot, pointer, unit, role and
  value. Corpus evidence instead binds a derived-view character span to a frozen
  original document and its derivation metadata. These contracts are not swapped.
* Opportunity identity/publication cycle: source-scoped contextual identifier,
  namespace and explicitly evidenced cycle under M2.1. URL/title/hash/year/host
  alone proves neither identity nor cycle; never merge automatically.
* Validation decision: ACCEPTED/REJECTED/REVIEW is the existing domain result,
  not an annotation class. REVIEW is not a negative. No authenticated review
  adapter exists and promotion remains disabled.
* Temporal status: existing M1 emits encerrada/nao_determinada; M2 temporal
  normalization preserves original expressions, roles, stages and uncertainty.
  English corpus temporal labels below are evaluation labels, not added enums
  or a claim that M1 can emit open/continuous/future.

## 3. Four distinct levels

Document category describes the frozen document's function, supported by
category_evidence in its derived text. A multi-record page stays a document,
not a single positive opportunity. Relevant main-content records are scoped
separately; boilerplate, navigation and related-news teasers are not exhaustively
annotated. Unannotated text is OUTSIDE evaluation, never an implicit negative.

Record label identifies the specific program, proposed instrument or completed
event at unit_locator. Opportunity existence and discovery relevance judge THAT
record, not every program mentioned nearby. Temporal availability judges the
same access stage at the explicit reference_date. One news article can have a
completed-transaction negative and a confirmed-program record. Never import a
neighbor's deadline, budget, eligibility or application language.

## 4. Document categories (not SQL/catalog values)

application_call: invites submissions to a specific selection process.
financing_program: loan/credit product description with purpose/conditions.
investment_program: equity, VC, co-investment or startup investment instrument.
institutional_news: journalistic/institutional communication; no default polarity.
selection_result: decisions about previously submitted/selected proposals.
program_information: general program information, index or overview.
rectification: explicitly modifies/corrects another document; relationship and
  precedence remain unverified unless separately evidenced and reviewed.
other_document: document not fitting those roles; rationale required.

Use the dominant function for a document, without propagating its category to
every record. Auxiliary annex links and full conditions not downloaded remain
unavailable evidence; do not invent their content.

## 5. Discovery and existence rubric

confirmed_opportunity: primary material establishes a real funding, credit or
  investment instrument, its target/access conditions and a supported route or
  invitation to seek support. Full commercial terms need not be complete. A
  conditional loan route qualifies; approval or funding is never guaranteed.
announced_future_opportunity: an authoritative statement expressly commits to a
  forthcoming access instrument/window, but submissions/full conditions are not
  established. Require an identifiable initiative and future access language;
  generic aspirations, an upcoming event or a future funded product do not pass.
opportunity_signal: meaningfully relevant information suggests possible access
  or a pipeline of funding, but a distinct instrument, its future commitment or
  access conditions cannot yet be confirmed from this record.
unrelated_or_non_actionable: the scoped content supplies no meaningful new,
  current or forthcoming access opportunity (e.g. completed deal, selection
  result, award payment, money for already assessed proposals). This is not a
  claim that the underlying historical instrument never existed.

genuine_opportunity: a distinct real instrument through which eligible parties
  can potentially seek support, regardless of whether its window is open.
not_opportunity: the scoped record does not establish such an instrument; a
  completed funding transaction is not itself an application instrument.
uncertain: insufficient primary evidence for that confirmation; do not force it
  into negatives. In this conservative pilot, confirmed maps to genuine,
  signals/future announcements to uncertain (access instrument not confirmed),
  and non-actionable records to not_opportunity. This is an explicit annotation
  convention, not an inference performed by M1/M2 or a universal ontology.

Borderlines must preserve rationale and uncertainty. A description of a fund may
be a confirmed instrument, a discovery signal, or irrelevant portfolio reporting
according to access evidence, NOT according to the word 'fund'. Manager selection
and startup eligibility are different audiences/stages. Report each explicitly.
A new fund targeting startups does not prove a startup application portal exists.

## 6. Temporal rubric and reference policy

All initial labels use reference_date=2026-10-19 (civil reference day; not an
implicit 'today'). Retrieval timestamps are UTC. A future re-evaluation must
version labels and reference date rather than overwrite this historical judgment.

open: explicit submission window/status plus evidence relating the application
  stage to the reference day, with no unresolved conflicting cutoff/suspension.
closed: evidenced deadline before the reference day or explicit closed status.
  The instrument can still be genuine; expired is NOT an existence negative.
future: a submission opening or expressly forthcoming application stage is after
  the reference day. A presentation/results date is NOT application opening.
continuous: source expressly establishes ongoing/rolling applications at that
  reference day, without an expired absolute cutoff or unresolved suspension.
undetermined: evidence insufficient to establish availability; the required
  temporal evidence shows the relevant record but does not manufacture a date.
not_applicable: a non-opportunity record has no access window to classify.

No deadline does NOT imply continuous. Request buttons and a live webpage do NOT
prove open. Evergreen program genre is not evidence of continuous funding.
Preserve original deadline, revised deadline, opening, stage, original expression,
rectification and conflicts separately. A civil day without hour is not 23:59:59;
unknown timezone/cutoff stays unknown. Interest, loan maturity, amortization,
grace period, investment horizon and funding dates are not submission deadlines.
Future award payment, vehicle launch or production of funded goods is not a future
application opportunity. Any temporal disagreement -> uncertainty, not a guessed
latest deadline. Historical closed examples are tested synthetically; collecting
expired real editais is not required under the scope update.

## 7. Modality and fields

Corpus modality: fomento (grants, scholarships, subvenção, non-repayable support),
credito (repayable loans/financing), investimentos (equity, VC, funds, co-investment)
or undetermined. A completed transaction can retain its financial subject while
being not_opportunity. 'Investimento em inovação' in a loan title is not equity;
'crédito não reembolsável' requires original terms/context rather than a keyword
rule. Hybrid instruments require separate component records if safely separable;
otherwise abstain and preserve original wording. No new production taxonomy.

Annotate only supported original expressions as strings, including title,
official_identifier, publisher, funder, resource_type, program_budget,
proposal_maximum, credit_limit/minimum, investment_amount, publication/opening/
submission dates, geographic eligibility, applicant requirements, publication
cycle and application stage. Optional absent fields are omitted, not invented
placeholders. Explicit absence in a future schema should be null with reason.
All asserted field values must occur literally in referenced evidence; normalized
values are deferred to an approved M3.1 adapter. Source URL is authoritative
manifest provenance, not an invented field quote when absent in page text.

Budgets are not proposal maxima. Announced fund capital is not a startup ticket.
Do not turn equity percentages, valuations, guarantees or interest components
into normalized production terms unsupported by contracts. A publication year is
not sufficient evidence of publication cycle. Organization publishing a story is
not automatically the funder. A bank office address is not applicant geography.
No automatic document/opportunity association, fuzzy merge or canonicalization.

## 8. Evidence, derivation and audit trail

Each evidence item has a document link through its record, evidence_id, exact
quote and [start,end) Unicode-codepoint offsets into frozen UTF-8 text. These are
NOT byte offsets into HTML. unit_locator bounds the record in that same view;
every witness must be contained. label_evidence links each of the four judgment
dimensions to witnesses; each field has its own evidence_ids. Exact substring
checks prove traceability, NOT semantic entailment. Rationale supplies the
interpretation; an independent reviewer must examine the surrounding raw source.

HTML view is passive HTMLParser data concatenation (whitespace collapsed within
data nodes, script/style/noscript/template excluded), not rendered DOM, DOM CSS
visibility or a native opportunity extractor. Navigation may remain. PDF view is
local pdftotext UTF-8 output with formfeed page delimiters, not OCR. PDF page
numbers are physical 1-based pages in this exact view, not inferred printed page
labels. Both raw and view have separate SHA-256; a future parser must not silently
regenerate the view and retain obsolete character offsets. No generated text
stands in for inaccessible documents.

Original entity bytes are saved once; hashes are calculated before text cleanup.
Source headers selected for content type/date/etag etc are supplementary. URLs,
retrieval status, byte length, timestamps, authority and restrictions are required.
Failed acquisitions are logged separately and are NOT corpus documents, negatives
or evidence. The pilot provenance URL syntax policy is explicit: absolute HTTPS,
no credentials, whitespace/control characters or non-443 custom port. This is a
local acquisition/provenance boundary, not a replacement for M1/M2 URL semantics,
not DNS/SSRF certification and not a fix or normalization shortcut for F04.
No claim of unrestricted redistribution rights. Treat raw files as
untrusted; do not open active HTML online or run PDF actions/macros. No applicant
personal information is sought; institutional contacts and public attribution may
remain in original public pages. Record any incident and quarantine if necessary.

## 9. Review and adjudication

Recognized review vocabulary: provisional, independently_reviewed, disputed,
approved. The current pilot validator intentionally permits ONLY provisional:
there is no authenticated/authorized review artifact or adapter. Merely changing
review_status cannot confer approval. AI peer checks validate consistency only;
they are not independent human annotations and do not advance status.

Before any reviewed-reference evaluation: appoint and document authorized human
reviewers, identify scope/policy/version and access rights, and collect two blind
independent annotations against the same frozen corpus (without current pipeline
predictions or each other's labels). Preserve reviewer-specific records unchanged,
label/field/stage disagreements and abstentions. Adjudicator examines original
bytes, evidence and rationale; retain both originals, resolution and reason.
Bind approval to document/view/annotation digests, reviewer identity,
authorization, UTC review time, policy version, decision scope, revocation and
provenance under an approved process. Do not invent a signature or simulate one.

independently_reviewed requires actual separately documented independent review;
disputed preserves unresolved disagreement; approved requires approved authority
and adjudication rules. This transition needs a reviewed schema extension: it is
not enabled by the pilot validator. No unauthenticated JSON flag can grant it.
An integrity hash does not authenticate a reviewer or approval. Freeze a new
reviewed dataset release; do not relabel this provisional release as ground truth.

## 10. Verification boundary

Run the offline dataset CLI and tests described in README. It checks structural
schema, versions, vocabularies, provenance, hashes, paths, source types, IDs,
record/document links, exact spans, field witnesses, PDF page bounds, dates and
basic contradiction rules. It does not prove source truth, license compliance,
entailment, representativeness, current web availability or extraction accuracy.
It neither downloads documents nor calls any model/domain integration service.
Changes must be explicit, versioned and reviewed; invalid annotations fail, never
silently repaired. Preserve the M2.3c frozen synthetic oracle unchanged.
