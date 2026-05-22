# Test Fixtures

## `hf-julien-c-titanic-survival.json`

Source: [`julien-c/titanic-survival`](https://hf.co/datasets/julien-c/titanic-survival)
on Hugging Face.

The upstream dataset is a CSV copy of the Titanic survival dataset from the
Stanford CS109 archive. Hugging Face metadata lists it as `license:cc`,
`format:csv`, `modality:tabular`, and `size_categories:n<1K`.

This fixture converts the upstream CSV rows to typed JSON so the optimizer test
exercises the common user path: a structured JSON upload that can be routed to a
lower-token tabular representation before model ingestion.
