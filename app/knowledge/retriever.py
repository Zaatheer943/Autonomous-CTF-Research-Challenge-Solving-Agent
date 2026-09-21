import chromadb
from chromadb.config import Settings
from typing import List, Optional
from sentence_transformers import SentenceTransformer
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings


class KnowledgeRetriever:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory
        )
        self.collection_name = "ctf_writeups"
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    def search(
        self,
        query: str,
        context: str = "",
        max_results: int = 5,
        category: Optional[str] = None
    ) -> List[str]:
        """Search for relevant knowledge chunks."""
        try:
            collection = self.chroma_client.get_collection(name=self.collection_name)

            # Combine query and context for better search
            search_query = f"{query} {context}".strip()

            # Generate embedding for query
            query_embedding = self.embedding_model.encode(search_query).tolist()

            # Build where clause for filtering
            where_clause = {}
            if category:
                where_clause["category"] = category

            # Search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results,
                where=where_clause if where_clause else None
            )

            # Extract relevant chunks
            retrieved_chunks = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    chunk_with_metadata = f"[{metadata.get('title', 'Unknown')} - {metadata.get('category', 'general')}]\n{doc}"
                    retrieved_chunks.append(chunk_with_metadata)

            return retrieved_chunks

        except Exception as e:
            print(f"Error during knowledge retrieval: {e}")
            return []


def main():
    """CLI entry point for search."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m app.knowledge.search <query>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    retriever = KnowledgeRetriever()
    results = retriever.search(query)

    print(f"Found {len(results)} relevant chunks:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result}")


if __name__ == "__main__":
    main()
