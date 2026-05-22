# Context Compression Benchmark Report

Generated: `2026-05-21T21:42:51+00:00`
Corpus: `data/benchmark-corpus`
Corpus manifest SHA-256: `8d4783790f6c6ceae35e6f8667c69d832cedca4cc13f50132b25b55fc9f26605`
Model: `gpt-5.5` via `tiktoken`
Input price: `$5.0000` per 1M tokens
Monthly calls: `100000`

## Totals

| Files | Raw tokens | Optimized tokens | Saved tokens | Savings | Saved / call | Saved / month |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 28 | 17496442 | 15162406 | 2334036 | 13.3% | $11.670180 | $1167018.00 |

## Local Processing Time

| Load ms | Candidate ms | Token-count ms | Total ms | Saved tokens / ms | Break-even max input tok/s |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 354.5 | 8386.8 | 54369.8 | 66012.4 | 35.4 | 35357.5 |

Break-even interpretation: compression is latency-positive only when the downstream model's input throughput is at or below the break-even ceiling above.

## By Format

| Format | Files | Raw tokens | Optimized tokens | Saved tokens | Savings |
| --- | ---: | ---: | ---: | ---: | ---: |
| `csv` | 7 | 4110345 | 3798428 | 311917 | 7.6% |
| `json` | 7 | 4793580 | 3782764 | 1010816 | 21.1% |
| `jsonl` | 7 | 4478352 | 3782764 | 695588 | 15.5% |
| `tsv` | 7 | 4114165 | 3798450 | 315715 | 7.7% |

## By Source Dataset

| Source | Files | Raw tokens | Optimized tokens | Saved tokens | Savings | Winning formats |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `github-top-repos` | 4 | 822418 | 583066 | 239352 | 29.1% | codebook-json x4 |
| `hf-amazon-reviews` | 4 | 231889 | 196274 | 35615 | 15.4% | raw x1, typed-csv x3 |
| `hf-code-doc` | 4 | 12851724 | 12172584 | 679140 | 5.3% | typed-codebook-row x4 |
| `hf-loghub-2` | 4 | 162725 | 95180 | 67545 | 41.5% | codebook-json x4 |
| `hf-openassistant` | 4 | 2249389 | 1755212 | 494177 | 22.0% | codebook-json x4 |
| `hf-squad` | 4 | 1007209 | 275338 | 731871 | 72.7% | codebook-json x4 |
| `hf-titanic-tabular` | 4 | 171088 | 84752 | 86336 | 50.5% | codebook-json x4 |

## Projected Latency At Configured Throughput

| Configured input tok/s | API-side ms saved | Net ms saved after local overhead | Break-even |
| ---: | ---: | ---: | --- |
| 1500.0 | 1556024.0 | 1490011.6 | yes |


## External Baselines

| Baseline | Files | Missing | Tokens | Savings | Saved / month | W/T/L vs selector |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `toon` | 28 | 0 | 17864941 | -2.1% | $-184249.50 | 0/0/28 |

## Candidate Ablation

| Candidate | Files | Wins | Tokens | Savings | Avg rank | Rank range |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `codebook-json` | 28 | 20 | 16406096 | 6.2% | 2.07 | 1-5 |
| `typed-codebook-row` | 18 | 4 | 14374358 | 5.2% | 2.61 | 1-5 |
| `typed-csv` | 22 | 3 | 14532768 | 5.2% | 3.32 | 1-7 |
| `raw` | 28 | 1 | 17496442 | 0.0% | 5.29 | 1-10 |
| `typed-tsv` | 22 | 0 | 14541860 | 5.1% | 4.00 | 2-8 |
| `column-json` | 28 | 0 | 17476598 | 0.1% | 4.07 | 2-7 |
| `codebook-row` | 24 | 0 | 17875160 | -3.2% | 6.58 | 3-9 |
| `compact-json` | 28 | 0 | 17927812 | -2.5% | 6.71 | 3-10 |
| `csv` | 28 | 0 | 18175682 | -3.9% | 7.39 | 5-10 |
| `tsv` | 24 | 0 | 18022962 | -4.0% | 7.54 | 5-10 |

## Files

| File | Kind | Bytes | Best format | Raw tokens | Optimized tokens | Savings |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| `github-top-repos.csv` | csv | 637821 | codebook-json | 203946 | 147322 | 27.8% |
| `github-top-repos.json` | json | 788075 | codebook-json | 233167 | 144211 | 38.2% |
| `github-top-repos.jsonl` | jsonl | 645735 | codebook-json | 180876 | 144211 | 20.3% |
| `github-top-repos.tsv` | tsv | 637543 | codebook-json | 204429 | 147322 | 27.9% |
| `hf-amazon-reviews.csv` | csv | 192759 | raw | 49052 | 49052 | 0.0% |
| `hf-amazon-reviews.json` | json | 262978 | typed-csv | 74176 | 49074 | 33.8% |
| `hf-amazon-reviews.jsonl` | jsonl | 232976 | typed-csv | 59248 | 49074 | 17.2% |
| `hf-amazon-reviews.tsv` | tsv | 192039 | typed-csv | 49413 | 49074 | 0.7% |
| `hf-code-doc.csv` | csv | 11565523 | typed-codebook-row | 3045398 | 3043146 | 0.1% |
| `hf-code-doc.json` | json | 11988648 | typed-codebook-row | 3387571 | 3043146 | 10.2% |
| `hf-code-doc.jsonl` | jsonl | 11958646 | typed-codebook-row | 3372988 | 3043146 | 9.8% |
| `hf-code-doc.tsv` | tsv | 11565507 | typed-codebook-row | 3045767 | 3043146 | 0.1% |
| `hf-loghub-2.csv` | csv | 96769 | codebook-json | 37825 | 23795 | 37.1% |
| `hf-loghub-2.json` | json | 119784 | codebook-json | 45907 | 23795 | 48.2% |
| `hf-loghub-2.jsonl` | jsonl | 107782 | codebook-json | 41171 | 23795 | 42.2% |
| `hf-loghub-2.tsv` | tsv | 96743 | codebook-json | 37822 | 23795 | 37.1% |
| `hf-openassistant.csv` | csv | 1362436 | codebook-json | 510074 | 443022 | 13.1% |
| `hf-openassistant.json` | json | 2147942 | codebook-json | 700537 | 434584 | 38.0% |
| `hf-openassistant.jsonl` | jsonl | 1540917 | codebook-json | 526800 | 434584 | 17.5% |
| `hf-openassistant.tsv` | tsv | 1361960 | codebook-json | 511978 | 443022 | 13.5% |
| `hf-squad.csv` | csv | 1041306 | codebook-json | 240559 | 70875 | 70.5% |
| `hf-squad.json` | json | 1174016 | codebook-json | 278193 | 66794 | 76.0% |
| `hf-squad.jsonl` | jsonl | 1085014 | codebook-json | 247191 | 66794 | 73.0% |
| `hf-squad.tsv` | tsv | 1040498 | codebook-json | 241266 | 70875 | 70.6% |
| `hf-titanic-tabular.csv` | csv | 45385 | codebook-json | 23491 | 21216 | 9.7% |
| `hf-titanic-tabular.json` | json | 185451 | codebook-json | 74029 | 21160 | 71.4% |
| `hf-titanic-tabular.jsonl` | jsonl | 137551 | codebook-json | 50078 | 21160 | 57.7% |
| `hf-titanic-tabular.tsv` | tsv | 45385 | codebook-json | 23490 | 21216 | 9.7% |
