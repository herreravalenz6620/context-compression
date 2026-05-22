# Paper Dataset Alignment

The benchmark should reuse paper datasets when they are public and directly
available. When a recent paper uses synthetic or unavailable data, use public
Hugging Face datasets that stress the same failure mode and keep the paper
baseline external.

## Current Mapping

| Paper / Baseline | Paper Data Status | Local Public Dataset Slice | Why It Matches |
| --- | --- | --- | --- |
| ONTO (`2604.17512`) | Reports synthetic operational datasets for IoT/CRM/e-commerce style records. | `julien-c/titanic-survival`, `OpenAssistant/oasst1`, GitHub repository metadata. | Covers schema-once/value-many records, nested metadata, repeated categorical fields, and operational-style rows without relying on private synthetic files. |
| Lossless dictionary encoding (`2604.13066`) | Evaluates on LogHub 2.0 for repetitive logs. | `bolu61/loghub_2`, plus `OpenAssistant/oasst1`, `SetFit/amazon_reviews_multi_en`, and `codeparrot/github-jupyter-code-to-text`. | Reuses a public Hugging Face LogHub 2.0 upload for the paper-aligned slice, then adds non-log repetitive data to avoid overfitting claims to one workload. |
| TOON / token-oriented structured notation | Public tool/spec, dataset mix depends on its benchmark harness. | Full HF corpus plus generated TOON baseline via `scripts/toon_baseline.mjs` and `benchmark.py --baseline-command`. | Lets TOON compete on the exact same files and tokenizer instead of comparing headline numbers from different corpora; the helper round-trips through the official `@toon-format/toon` decoder before writing output. |
| LLMLingua / semantic prompt compression | Public method, not lossless structured-data specific. | Optional external baseline on text-heavy slices only. | Useful for text-heavy records, but it should not be used as a default runtime candidate because the product contract is parsed-value lossless replacement. |

## Publication Rule

Use `benchmark.py verify-corpus` before publishing token, dollar, or adoption
claims. That gate requires the configured Hugging Face Dataset Viewer sources,
row scale, four supported materializations, and shape coverage across:

- flat/tabular data
- nested metadata
- long text records
- conversation-like agent data
- QA rows with nested answer arrays
- code/documentation cells
- repetitive log lines aligned with the LogHub 2.0 dictionary-compression paper

Toy corpora and local fixtures are allowed only for unit tests, hook smokes, and
plumbing checks.

## What Still Needs Real Comparator Evidence

The current corpus makes the selector evidence reproducible, but it does not
replace matched comparator runs. Publication-quality claims still need:

- TOON and ONTO-style outputs generated on this corpus with
  `benchmark.py --baseline-command`
- answer-parity summaries from `evals/summarize_context_quality.py` with a
  recorded `quality_gate`
- no raw-correct/optimized-wrong regressions, no missing raw/optimized pairs,
  and a declared optimized-accuracy floor on the accepted claim slice
- per-dataset reporting so wins are not hidden by a favorable aggregate
