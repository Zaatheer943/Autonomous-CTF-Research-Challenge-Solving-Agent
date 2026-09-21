import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Any
import json
import re
import sys
import os
from sentence_transformers import SentenceTransformer

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.knowledge.schemas import WriteupMetadata, WriteupChunk
from app.config import settings


class KnowledgeIngestor:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory
        )
        self.collection_name = "ctf_writeups"
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    def ingest_directory(self, directory_path: str) -> Dict[str, Any]:
        """Ingest all writeup files from a directory."""
        directory = Path(directory_path)
        if not directory.exists():
            return {"success": False, "error": f"Directory not found: {directory_path}"}

        # Get or create collection
        collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        total_chunks = 0
        files_processed = 0
        errors = []

        for file_path in directory.glob("**/*.md"):
            try:
                chunks = self._process_file(file_path)
                if chunks:
                    self._add_chunks_to_collection(collection, chunks, file_path)
                    total_chunks += len(chunks)
                    files_processed += 1
            except Exception as e:
                errors.append(f"{file_path}: {str(e)}")

        return {
            "success": True,
            "files_processed": files_processed,
            "total_chunks": total_chunks,
            "errors": errors
        }

    def _process_file(self, file_path: Path) -> List[WriteupChunk]:
        """Process a single writeup file and extract chunks."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract metadata from frontmatter or create default
        metadata = self._extract_metadata(content, file_path)

        # Split content into chunks
        chunks = self._split_into_chunks(content, metadata, str(file_path))

        # Generate embeddings
        for chunk in chunks:
            chunk.embedding = self.embedding_model.encode(chunk.content).tolist()

        return chunks

    def _extract_metadata(self, content: str, file_path: Path) -> WriteupMetadata:
        """Extract metadata from writeup content."""
        # Try to extract YAML frontmatter
        metadata = WriteupMetadata(
            title=file_path.stem,
            category="general",
            techniques=[],
            difficulty="medium"
        )

        # Simple frontmatter parsing
        if content.startswith("---"):
            try:
                parts = content.split("---", 2)
                if len(parts) >= 2:
                    frontmatter = parts[1]
                    # Parse simple key-value pairs
                    for line in frontmatter.split("\n"):
                        if ":" in line:
                            key, value = line.split(":", 1)
                            key = key.strip().lower()
                            value = value.strip()

                            if key == "title":
                                metadata.title = value
                            elif key == "category":
                                metadata.category = value
                            elif key == "difficulty":
                                metadata.difficulty = value
                            elif key == "techniques":
                                # Parse list
                                metadata.techniques = [
                                    t.strip().strip('"\'')
                                    for t in value.strip("[]").split(",")
                                    if t.strip()
                                ]
                            elif key == "tags":
                                metadata.tags = [
                                    t.strip().strip('"\'')
                                    for t in value.strip("[]").split(",")
                                    if t.strip()
                                ]
            except Exception:
                pass

        return metadata

    def _split_into_chunks(
        self,
        content: str,
        metadata: WriteupMetadata,
        source_file: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[WriteupChunk]:
        """Split content into overlapping chunks."""
        # Remove frontmatter if present
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2]

        chunks = []
        words = content.split()
        current_chunk = []

        for i, word in enumerate(words):
            current_chunk.append(word)

            if len(current_chunk) >= chunk_size:
                chunk_text = " ".join(current_chunk)
                chunk_id = f"{source_file}_{len(chunks)}"

                chunk = WriteupChunk(
                    content=chunk_text,
                    metadata=metadata,
                    source_file=source_file,
                    chunk_id=chunk_id
                )
                chunks.append(chunk)

                # Create overlap
                current_chunk = current_chunk[-overlap:]

        # Add remaining content
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk_id = f"{source_file}_{len(chunks)}"

            chunk = WriteupChunk(
                content=chunk_text,
                metadata=metadata,
                source_file=source_file,
                chunk_id=chunk_id
            )
            chunks.append(chunk)

        return chunks

    def _add_chunks_to_collection(
        self,
        collection,
        chunks: List[WriteupChunk],
        file_path: Path
    ):
        """Add chunks to ChromaDB collection."""
        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for chunk in chunks:
            ids.append(chunk.chunk_id)
            embeddings.append(chunk.embedding)
            documents.append(chunk.content)
            metadatas.append({
                "title": chunk.metadata.title,
                "category": chunk.metadata.category,
                "techniques": ",".join(chunk.metadata.techniques),
                "difficulty": chunk.metadata.difficulty,
                "source_file": chunk.source_file
            })

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )


def main():
    """CLI entry point for ingestion."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m app.knowledge.ingest <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    ingestor = KnowledgeIngestor()
    result = ingestor.ingest_directory(directory)

    if result["success"]:
        print(f"Successfully ingested {result['files_processed']} files")
        print(f"Created {result['total_chunks']} chunks")
        if result["errors"]:
            print(f"Errors: {len(result['errors'])}")
            for error in result["errors"]:
                print(f"  - {error}")
    else:
        print(f"Error: {result['error']}")


if __name__ == "__main__":
    main()
