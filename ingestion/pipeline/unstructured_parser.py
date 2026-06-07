# ingestion/pipeline/unstructured_parser.py
import boto3
from unstructured.partition.auto import partition
from unstructured.chunking.title import chunk_by_title
from unstructured.documents.elements import CompositeElement
from pathlib import Path
import tempfile
from typing import Generator

s3_client = boto3.client("s3")


def stream_s3_documents(bucket: str, prefix: str = "compliance/") -> Generator[dict, None, None]:
    """
    Streams objects from S3, partitions with Unstructured.io,
    chunks by semantic title boundaries, and yields text chunks.
    """
    paginator = s3_client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if not key.lower().endswith((".pdf", ".docx", ".html")):
                continue

            with tempfile.NamedTemporaryFile(suffix=Path(key).suffix) as tmp:
                s3_client.download_fileobj(bucket, key, tmp)
                tmp.flush()

                # Unstructured.io auto-detects file type, handles tables + figures
                elements = partition(
                    filename=tmp.name,
                    strategy="hi_res",           # OCR + layout analysis for PDFs
                    infer_table_structure=True,   # Preserves table semantics
                    languages=["eng"],
                )

            # Chunk by document sections for coherent RAG retrieval
            chunks: list[CompositeElement] = chunk_by_title(
                elements,
                max_characters=1024,
                new_after_n_chars=768,
                combine_text_under_n_chars=200,
            )

            for i, chunk in enumerate(chunks):
                yield {
                    "doc_id":      key,
                    "chunk_index": i,
                    "policy_type": _classify_policy_type(key),
                    "chunk_text":  str(chunk),
                    "source_s3":   f"s3://{bucket}/{key}",
                }


def _classify_policy_type(key: str) -> str:
    key_lower = key.lower()
    if "chargeback" in key_lower:   return "chargeback"
    if "fraud"      in key_lower:   return "fraud"
    if "kyc"        in key_lower:   return "kyc"
    if "aml"        in key_lower:   return "aml"
    return "general"
