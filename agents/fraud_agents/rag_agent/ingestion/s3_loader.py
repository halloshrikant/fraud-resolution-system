# agents/rag_agent/ingestion/s3_loader.py
"""Lightweight S3 fetcher — unit-testable in isolation."""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Iterator

import boto3

s3_client = boto3.client("s3")


def iter_s3_keys(bucket: str, prefix: str = "compliance/") -> Iterator[str]:
    """Yield all object keys under the given prefix."""
    paginator = s3_client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            yield obj["Key"]


def download_s3_object(bucket: str, key: str) -> tempfile.NamedTemporaryFile:
    """
    Download an S3 object to a temp file and return the open handle.
    Caller must close or use as a context manager.
    """
    tmp = tempfile.NamedTemporaryFile(suffix=Path(key).suffix, delete=False)
    s3_client.download_fileobj(bucket, key, tmp)
    tmp.flush()
    return tmp