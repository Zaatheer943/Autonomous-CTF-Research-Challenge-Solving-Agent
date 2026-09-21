from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class WriteupMetadata(BaseModel):
    title: str
    category: str
    techniques: List[str] = Field(default_factory=list)
    difficulty: str = "medium"
    author: Optional[str] = None
    year: Optional[int] = None
    tags: List[str] = Field(default_factory=list)


class WriteupChunk(BaseModel):
    content: str
    metadata: WriteupMetadata
    source_file: str
    chunk_id: str
    embedding: Optional[List[float]] = None


class KnowledgeQuery(BaseModel):
    query: str
    category: Optional[str] = None
    techniques: Optional[List[str]] = None
    max_results: int = 5
