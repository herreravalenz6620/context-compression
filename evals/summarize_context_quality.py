#!/usr/bin/env python3
"""Summarize raw-vs-optimized context quality results."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Inspect .eval/.json log or JSONL prediction export.")
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--markdown-out", type=Path, default=None)
    parser.add_argument(
        "--fail-on-optimized-regression",
        action="store_true",
        help="Exit non-zero if any paired item has raw correct and optimized incorrect.",
    )
    parser.add_argument(
        "--fail-on-missing-pairs",
        action="store_true",
        help="Exit non-zero if any source/question slice is missing either raw or optimized.",
    )
    parser.add_argument(
        "--min-optimized-accuracy",
        type=float,
        default=None,
        help="Exit non-zero unless optimized variant accuracy is at least this value, e.g. 0.99.",
    )
    parser.add_argument(
        "--min-pairs",
        type=int,
        default=None,
        help="Exit non-zero unless at least this many raw/optimized pairs are present.",
    )
    args = parser.parse_args()

    samples = load_samples(args.input)
    summary = summarize_samples(samples)
    summary["quality_gate"] = build_quality_gate(
        summary,
        fail_on_optimized_regression=args.fail_on_optimized_regression,
        fail_on_missing_pairs=args.fail_on_missing_pairs,
        min_optimized_accuracy=args.min_optimized_accuracy,
        min_pairs=args.min_pairs,
    )

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        print(json.dumps(summary, indent=2, ensure_ascii=False))

    if args.markdown_out:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(markdown_summary(summary), encoding="utf-8")

    if not summary["quality_gate"]["passed"]:
        return 1
    return 0


def load_samples(path: Path) -> list[dict[str, Any]]:
    if path.suffix == ".jsonl":
        return [normalize_jsonl_record(record) for record in load_jsonl(path)]
    return load_inspect_samples(path)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(record, dict):
                raise SystemExit(f"{path}:{line_number}: record must be an object")
            records.append(record)
    return records


def normalize_jsonl_record(record: dict[str, Any]) -> dict[str, Any]:
    answer = record.get("answer", record.get("output"))
    target = record.get("target")
    correct = record.get("correct")
    if correct is None:
        correct = normalize_answer(answer) == normalize_answer(target)
    return {
        "id": str(record.get("id", "")),
        "variant": str(record.get("variant", "")),
        "source_file": str(record.get("source_file", "")),
        "question_type": str(record.get("question_type", "")),
        "target": target,
        "answer": answer,
        "correct": bool(correct),
    }


def load_inspect_samples(path: Path) -> list[dict[str, Any]]:
    try:
        from inspect_ai.log import read_eval_log
    except Exception as exc:
        raise SystemExit("Inspect AI is required to read non-JSONL eval logs") from exc

    log = read_eval_log(path)
    if not log.samples:
        raise SystemExit(f"{path} contains no samples")
    return [normalize_inspect_sample(sample) for sample in log.samples]


def normalize_inspect_sample(sample: Any) -> dict[str, Any]:
    metadata = sample.metadata or {}
    score = first_score(sample.scores)
    answer = getattr(sample.output, "completion", None)
    target = sample.target
    correct = score_correct(score)
    if correct is None:
        correct = normalize_answer(answer) == normalize_answer(target)
    return {
        "id": str(sample.id),
        "variant": str(metadata.get("variant", "")),
        "source_file": str(metadata.get("source_file", "")),
        "question_type": str(metadata.get("question_type", "")),
        "target": target,
        "answer": answer,
        "correct": bool(correct),
    }


def first_score(scores: Any) -> Any:
    if isinstance(scores, dict) and scores:
        return next(iter(scores.values()))
    return None


def score_correct(score: Any) -> bool | None:
    if score is None:
        return None
    value = getattr(score, "value", score)
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value == 1
    if isinstance(value, str):
        return value.strip().lower() in {"c", "correct", "true", "1", "yes"}
    return None


def normalize_answer(value: Any) -> str:
    if isinstance(value, list):
        return "\n".join(normalize_answer(item) for item in value)
    return str(value).strip() if value is not None else ""


def summarize_samples(samples: list[dict[str, Any]]) -> dict[str, Any]:
    if not samples:
        raise SystemExit("no samples to summarize")

    return {
        "total": aggregate(samples),
        "by_variant": aggregate_by(samples, "variant"),
        "by_question_type": aggregate_by(samples, "question_type"),
        "by_question_type_variant": aggregate_by_question_type_variant(samples),
        "pair_parity": pair_parity(samples),
    }


def aggregate(samples: list[dict[str, Any]]) -> dict[str, Any]:
    correct = sum(1 for sample in samples if sample["correct"])
    total = len(samples)
    return {
        "samples": total,
        "correct": correct,
        "accuracy": 0.0 if total == 0 else correct / total,
    }


def aggregate_by(samples: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for sample in samples:
        buckets[str(sample.get(key, ""))].append(sample)
    return {name: aggregate(bucket) for name, bucket in sorted(buckets.items())}


def aggregate_by_question_type_variant(samples: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for sample in samples:
        grouped[str(sample.get("question_type", ""))][str(sample.get("variant", ""))].append(sample)
    return {
        question_type: {
            variant: aggregate(bucket)
            for variant, bucket in sorted(variants.items())
        }
        for question_type, variants in sorted(grouped.items())
    }


def pair_parity(samples: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for sample in samples:
        key = (str(sample.get("source_file", "")), str(sample.get("question_type", "")))
        groups[key][str(sample.get("variant", ""))] = sample

    summary = {
        "pairs": 0,
        "missing_pairs": 0,
        "both_correct": 0,
        "raw_only_correct": 0,
        "optimized_only_correct": 0,
        "both_wrong": 0,
        "optimized_regressions": [],
    }
    for (source_file, question_type), variants in sorted(groups.items()):
        raw = variants.get("raw")
        optimized = variants.get("optimized")
        if raw is None or optimized is None:
            summary["missing_pairs"] += 1
            continue
        summary["pairs"] += 1
        raw_correct = bool(raw["correct"])
        optimized_correct = bool(optimized["correct"])
        if raw_correct and optimized_correct:
            summary["both_correct"] += 1
        elif raw_correct and not optimized_correct:
            summary["raw_only_correct"] += 1
            summary["optimized_regressions"].append(
                {
                    "source_file": source_file,
                    "question_type": question_type,
                    "raw_answer": raw.get("answer"),
                    "optimized_answer": optimized.get("answer"),
                    "target": raw.get("target"),
                }
            )
        elif optimized_correct:
            summary["optimized_only_correct"] += 1
        else:
            summary["both_wrong"] += 1
    return summary


def build_quality_gate(
    summary: dict[str, Any],
    fail_on_optimized_regression: bool,
    fail_on_missing_pairs: bool,
    min_optimized_accuracy: float | None,
    min_pairs: int | None,
) -> dict[str, Any]:
    failures: list[str] = []
    parity = summary["pair_parity"]
    optimized = summary["by_variant"].get("optimized")
    optimized_accuracy = None if optimized is None else optimized["accuracy"]

    if fail_on_optimized_regression and parity["raw_only_correct"] > 0:
        failures.append(f"optimized regressions: {parity['raw_only_correct']}")
    if fail_on_missing_pairs and parity["missing_pairs"] > 0:
        failures.append(f"missing raw/optimized pairs: {parity['missing_pairs']}")
    if min_optimized_accuracy is not None:
        if optimized_accuracy is None:
            failures.append("optimized variant missing")
        elif optimized_accuracy < min_optimized_accuracy:
            failures.append(
                f"optimized accuracy {optimized_accuracy:.6f} below minimum {min_optimized_accuracy:.6f}"
            )
    if min_pairs is not None and parity["pairs"] < min_pairs:
        failures.append(f"pairs {parity['pairs']} below minimum {min_pairs}")

    return {
        "passed": not failures,
        "failures": failures,
        "criteria": {
            "fail_on_optimized_regression": fail_on_optimized_regression,
            "fail_on_missing_pairs": fail_on_missing_pairs,
            "min_optimized_accuracy": min_optimized_accuracy,
            "min_pairs": min_pairs,
        },
    }


def markdown_summary(summary: dict[str, Any]) -> str:
    lines = [
        "# Context Quality Summary",
        "",
        "## Total",
        "",
        "| Samples | Correct | Accuracy |",
        "| ---: | ---: | ---: |",
        metric_row(summary["total"]),
        "",
        "## By Variant",
        "",
        "| Variant | Samples | Correct | Accuracy |",
        "| --- | ---: | ---: | ---: |",
    ]
    for variant, bucket in summary["by_variant"].items():
        lines.append(f"| `{variant}` | {bucket['samples']} | {bucket['correct']} | {bucket['accuracy']:.1%} |")
    lines.extend(
        [
            "",
            "## Pair Parity",
            "",
            "| Pairs | Missing | Both correct | Raw only correct | Optimized only correct | Both wrong |",
            "| ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    parity = summary["pair_parity"]
    lines.append(
        f"| {parity['pairs']} | {parity['missing_pairs']} | {parity['both_correct']} | "
        f"{parity['raw_only_correct']} | {parity['optimized_only_correct']} | {parity['both_wrong']} |"
    )
    if "quality_gate" in summary:
        gate = summary["quality_gate"]
        lines.extend(
            [
                "",
                "## Quality Gate",
                "",
                f"Status: {'pass' if gate['passed'] else 'fail'}",
            ]
        )
        if gate["failures"]:
            lines.append("")
            for failure in gate["failures"]:
                lines.append(f"- {failure}")
    lines.extend(
        [
            "",
            "## By Question Type",
            "",
            "| Question type | Variant | Samples | Correct | Accuracy |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    for question_type, variants in summary["by_question_type_variant"].items():
        for variant, bucket in variants.items():
            lines.append(
                f"| `{question_type}` | `{variant}` | {bucket['samples']} | "
                f"{bucket['correct']} | {bucket['accuracy']:.1%} |"
            )
    lines.append("")
    return "\n".join(lines)


def metric_row(bucket: dict[str, Any]) -> str:
    return f"| {bucket['samples']} | {bucket['correct']} | {bucket['accuracy']:.1%} |"


if __name__ == "__main__":
    raise SystemExit(main())
