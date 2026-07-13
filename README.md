# rascasse-bq-client

Shared BigQuery client for Rascasse Python services. Extracted from
`entity-operationalization-ml/eom/bq.py` (2026-07 codebase quality audit) to
stop `PROJECT_ID`/`DATASET_ID` constants and a `bigquery.Client()` bootstrap
being duplicated ad hoc across `rascasse-cloud-functions`, `rascasse-socialops`,
and `entity-enrichment`.

## Install

Use the GitHub release-tarball URL, **not** `git+https://...`. Several
consuming services build in minimal Docker images (`python:3.12-slim`) that
don't have the `git` binary installed, which makes `pip install git+https://...`
fail at build time ("Cannot find command 'git'") - a plain tarball URL has no
such dependency, pip just downloads and unpacks it like any other sdist.

```bash
pip install "rascasse-bq-client @ https://github.com/rascasse-com/rascasse-bq-client/archive/refs/tags/v0.1.0.tar.gz"
```

In `requirements.txt`:
```
rascasse-bq-client @ https://github.com/rascasse-com/rascasse-bq-client/archive/refs/tags/v0.1.0.tar.gz
```

For the `polars` extra, download the tarball as above then `pip install ".[polars]"` from
a local checkout, or vendor the optional deps (`polars`, `pyarrow`, `google-cloud-bigquery-storage`)
directly in the consumer's own requirements.txt - the extras syntax needs a package name,
which isn't available from a bare tarball URL.

## Usage

```python
from rascasse_bq_client import query_rows, table_ref, client

rows = query_rows(f"SELECT * FROM {table_ref('entities')} LIMIT 10")

# Direct client access for anything not covered by the helpers above:
job = client().query("SELECT 1")
```

## Configuration

`PROJECT`/`DATASET` default to `rascasse5`/`rascasse_analytics` (production).
Override via env vars for staging or other datasets:

```bash
export RASCASSE_BQ_PROJECT=rascasse5
export RASCASSE_BQ_DATASET=staging_analytics
```

## Why this exists

See memory `code-quality-audit-2026-07` / the 2026-07-12 audit report:
BigQuery client bootstrap was independently reimplemented in 20+ files across
`rascasse-cloud-functions`, `rascasse-socialops`, and `entity-enrichment`. This
package is the single source of truth going forward - new Python services
should depend on it instead of writing another copy.
