"""Shared BigQuery client helpers.

Extracted from entity-operationalization-ml/eom/bq.py (2026-07 codebase
quality audit - BigQuery client bootstrap was duplicated ad hoc across
rascasse-cloud-functions, rascasse-socialops, and entity-enrichment). This is
the single canonical version; consuming repos should depend on this package
instead of re-implementing client()/query_rows()/table_ref().

Project/dataset default to the production values but are overridable via
env vars so callers that need the staging dataset (e.g. rascasse-cloud-functions'
staging deploys) don't need a second copy of this module.
"""
import io
import json
import os
from typing import Any, Dict, Iterable, List

from google.cloud import bigquery

PROJECT = os.environ.get("RASCASSE_BQ_PROJECT", "rascasse5")
DATASET = os.environ.get("RASCASSE_BQ_DATASET", "rascasse_analytics")

_client = None


def client() -> bigquery.Client:
    """Lazily-created, process-wide singleton BigQuery client."""
    global _client
    if _client is None:
        _client = bigquery.Client(project=PROJECT)
    return _client


def table_ref(name: str) -> str:
    """Fully-qualified, backtick-quoted table reference for use in SQL:
    table_ref("entities") -> "`rascasse5.rascasse_analytics.entities`"
    """
    return f"`{PROJECT}.{DATASET}.{name}`"


def query_rows(sql: str) -> List[Dict[str, Any]]:
    """Run a query and return rows as a list of dicts."""
    return [dict(r) for r in client().query(sql).result()]


def query_polars(sql: str):
    """Run a query and return a polars DataFrame (via Arrow for speed).
    Requires the optional `polars` extra - only imported if actually called."""
    import polars as pl
    table = client().query(sql).to_arrow(create_bqstorage_client=True)
    return pl.from_arrow(table)


def load_json_rows(table_id: str, rows: Iterable[Dict[str, Any]], schema: list):
    """Batch-load rows into a table (WRITE_TRUNCATE)."""
    buf = io.BytesIO()
    for r in rows:
        buf.write((json.dumps(r) + "\n").encode("utf-8"))
    buf.seek(0)
    cfg = bigquery.LoadJobConfig(
        schema=schema,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    client().load_table_from_file(buf, table_id, job_config=cfg).result()
