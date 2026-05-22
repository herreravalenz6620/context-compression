import os
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import FieldSpec, json_dataset
from inspect_ai.scorer import accuracy, exact, stderr
from inspect_ai.solver import generate, system_message

DATASET_ENV = os.environ.get("CONTEXT_QUALITY_DATASET", "context-quality-smoke.jsonl")
DATASET = Path(DATASET_ENV)
if not DATASET.is_absolute():
    DATASET = Path(__file__).with_name(DATASET_ENV)


@task
def context_quality_smoke() -> Task:
    return Task(
        dataset=json_dataset(
            str(DATASET),
            FieldSpec(
                input="input",
                target="target",
                id="id",
                metadata=["variant", "source_file", "question_type"],
            ),
        ),
        solver=[
            system_message("Answer with the exact JSON value only. Do not explain."),
            generate(),
        ],
        scorer=exact(),
        metrics=[accuracy(), stderr()],
    )
