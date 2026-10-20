# M3.1 extraction preparation — proposal only, NOT started

This file specifies future work and acceptance criteria; M3.0 implements no
opportunity extractor, production crawler, database writer or raw-to-domain bridge.
All current labels are provisional AI-assisted observations. No precision/recall
claim or label-truth certification is made.

## Entry gates (technical review required)

1. Review M3.0 protocol, coverage gaps, safe acquisition logs and label evidence.
2. Authorize human review governance and appoint two independent reviewers plus
   adjudication authority. Freeze independent annotations before predictions.
3. Resolve semantic disagreements, audience/stage/cutoff ambiguity and any source
   restrictions; publish an approved reference release with immutable hashes and
   documented authorization. Do not make provisional labels definitive by fiat.
4. Approve a versioned source-specific passive text adapter design. Native raw
   bytes and derived text must remain independently addressable. M23D-F02 oracle
   observability and F04 URL-boundary divergence remain known baseline limitations;
   decide transport policy separately, do not hide them with dataset labels.
5. Recheck offline baseline, dependency lock and no-promotion constraints. Human
   reference review does not authenticate an M1 ReviewAttestation or enable writes.

## Work packages and acceptance artifacts

WP1 — Benchmark specification (research owner, authority to be appointed).
  Freeze tasks, unit scope, eligible labels, metrics, reference day, held-out
  grouping and abstention handling before experiments. Produce protocol checksum,
  reviewed reference checksum, split/group manifest and empty prediction schema.
  Acceptance: uncertain/out-of-scope records cannot enter a binary negative set.

WP2 — Passive document adapter spike (engineer, only after separate approval).
  Use only frozen bytes, bounded local parsing, no scripts/macros/network. Preserve
  source-byte hash, derivation version, page/section/offsets and failure reasons.
  Return explicit per-record segments; never turn an entire multi-record page into
  one opportunity. Handle HTML menu leakage, PDF layout/hyphenation and conflicting
  attachments. Unknown/unsupported layouts abstain, not silently truncate.
  Acceptance: fixture-level deterministic segment provenance and adversarial size,
  malformed-document and cross-record contamination tests. Parsing text is not
  yet extracting a financial opportunity.

WP3 — Claim extraction experiment (not production implementation in M3.0).
  Extract evidence-backed original expressions with individual stage/role scopes.
  Missing values stay absent; preserve proposed program versus access route,
  grant budget versus per-proposal cap, loan versus equity and unknown timezones.
  Store predictions SEPARATELY, including prompt/model/parser versions, input hash,
  decoding settings, run ID and failures. Never overwrite reference labels.
  Acceptance: original source spans/pages resolve; no fabricated application URLs,
  eligibility, rates, equity terms, dates, continuous status or canonical codes.

WP4 — Explicit reviewed bridge to M1/M2 (separate design approval).
  Map one segmented record into sanitized JSON, typed FieldAssertions and a real
  DocumentUnit with direct-field RFC6901 pointers. Keep original HTTP/PDF digest
  distinct from RawSnapshot's sanitized UTF-8 payload digest and report digests.
  Preserve source UUID/context, publisher/funder roles, namespace and explicitly
  supported publication cycle. No implicit claim that the current integrate API
  accepts raw HTML/PDF or that M2 normalization sets M1 fields automatically.
  Acceptance: M1/M2 contract tests and scope replay pass without changing their
  historical expectations; promotion and merge remain false/absent.

WP5 — Task-specific scoring/error analysis (research/QA, after reviewed labels).
  Join predictions to record IDs plus frozen document/view hashes; fail on missing,
  duplicated, wrong-version or wrong-reference predictions. Report abstentions and
  operational failures separately; never erase failed runs from the denominator.
  Produce per-task confusion matrices, field witnesses, error ledger and coverage.

WP6 — Independent technical review.
  Audit false positives, especially completed deals, awards, budget supplements,
  generic fund descriptions, related-story teasers and manager/startup audience
  confusion. Verify no hidden cross-record/cross-document joins or privileged
  review claim. Re-run original 2,000 regressions and new offline tests. Approval
  of an extraction experiment is not production, Supabase or crawling approval.

## Evaluation tasks (separate denominators)

A. Opportunity existence: genuine_opportunity vs not_opportunity, only approved
   records. Exclude uncertain from binary confusion matrix and disclose excluded
   count. Report TP, FP, TN, FN, precision=TP/(TP+FP), recall=TP/(TP+FN),
   F1=2PR/(P+R), FPR=FP/(FP+TN), support and abstention coverage. Undefined
   denominators produce null/undefined, not 0 or invented perfect scores.

B. Discovery relevance: four-class confirmed / future announcement / signal /
   non-actionable. Report class confusion matrix and per-class precision/recall/F1;
   macro summary only within THIS task. Optionally preregister a broad relevance
   target (first three classes), never confuse it with confirmed accessibility.
   Signal is relevant discovery even when existence is uncertain.

C. Temporal availability: open/closed/future/continuous/undetermined, same explicit
   reference day and stage. Non-opportunity/not_applicable is outside this task.
   Evaluate exact temporal class and false-open rate on known non-open records;
   do not recode undetermined or operational REVIEW as closed/rejected. Report
   timezone/cutoff unknowns and reference-date sensitivity separately.

D. Financial modality: fomento/credito/investimentos on eligible reviewed records;
   undetermined is abstention, not a negative class fabricated for score inflation.
   Report per-modality confusion/support and ambiguous/hybrid exclusions.

E. Field extraction: exact match by field on supported original expressions and
   reviewed semantic role (title, official ID, dates by stage, amounts by role,
   organization roles, geography, applicants, cycle, resource type). Evaluate
   present-field precision/recall and missing-field hallucination rate separately.
   Any approved normalized-value metric must state the mapping/version and NOT
   silently replace original-expression exact match. Unsupported credit/equity
   semantics cannot be marked normalized/correct by a new ad hoc taxonomy.

F. Evidence attribution: measure resolvable witness rate separately from reviewer-
   judged entailment and correct record/field/stage attribution. Quote substring
   matching alone is not evidence attribution accuracy. Report exact page/span
   matches plus cross-record contamination rate; no invented PDF page numbers.

G. Identity resolution: separate pairwise task with adjudicated same/different/
   unresolved instrument AND cycle/context. URL/hash equality is not a gold match;
   different PDF/HTML bytes can describe one opportunity. No identity score is
   possible until pairs receive approved independent labels. Report conditional
   pairwise precision/recall/F1 on reviewed known pairs and abstention/conflict
   counts; do not automatically merge records or collapse cycles.

For each task report review/abstention rate with its denominator. Distinguish
semantic abstention, unresolved reference label, operational failure and domain
REVIEW. No single global accuracy mixes these tasks. Do not compute present
precision, recall or extraction performance: no predictions have been compared
against independently reviewed human reference labels in M3.0.

## Split, leakage and uncertainty controls

This tiny curated pilot is for protocol development and error discovery, not a
statistical generalization claim. No train/test benchmark is certified yet.
Group by source, instrument family, publication cycle, related announcement/PDF/
amendment and near-copy bytes before any split. A parent index and its details,
completed transaction and corresponding product page, or the same program in
multiple modalities must not leak across train/test because their document IDs
are different. Record suspected relations as unverified, not canonical merges.
Reserve a later time/source holdout and unseen instruments for external validation.

Evaluate model predictions blind to adjudication; freeze references before runs.
If learning/prompt tuning uses this pilot, call subsequent scores development
results, never held-out performance. Report full supports and cases, not unstable
percentages alone. Any future confidence intervals must state sampling/grouping
assumptions; purposive sampling cannot estimate whole-web prevalence or recall.
No minimum quality threshold is invented in M3.0: the technical/product authority
must preregister thresholds for each task and high-cost false positives.

## Deferred, not authorized by this plan

No automatic promotion/publication/merge, production deployment, unrestricted
acquisition, Supabase/database persistence, taxonomy seeds, SQL migration,
authentication workaround or automatic start of M3.1. Stop at M3.0 and await review.
