from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class RetrievalMode(str, Enum):
    AUTOMATIC = "AUTOMATIC"
    REVIEW_ONLY = "REVIEW_ONLY"

class RetrievedChunk(BaseModel):
    rule_id: str
    text: str
    score: float
    source_document: str
    source_section: str
    corpus_hash: str
    chunk_index: int

class RetrievalResult(BaseModel):
    query: str
    retrieval_mode: RetrievalMode
    chunks: List[RetrievedChunk]
    corpus_hash: str
    error: Optional[str] = None
