# rascasse-bq-client

Shared BigQuery client for Rascasse Python services. Extracted from
`entity-operationalization-ml/eom/bq.py` (2026-07 codebase quality audit) to
stop `PROJECT_ID`/`DATASET_ID` constants and a `bigquery.Client()` bootstrap
being duplicated ad hoc across `rascasse-cloud-functions`, `rascasse-socialops`,
and `entity-enrichment`.

## Install

```bash
pip install "git+https://github.com/rascasse-com/rascasse-bq-client.git"
# with polars support:
pip install "git+https://github.com/rascasse-com/rascasse-bq-client.git#egg=rascasse-bq-client[polars]"
```

Pin to a commit/tag in `requirements.txt` once this stabilizes, e.g.:
```
rascasse-bq-client @ git+https://github.com/rascasse-com/rascasse-bq-client.git@v0.1.0
```

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
