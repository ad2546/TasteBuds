"""Pinecone vector database client for Taste Twin matching."""

from typing import List, Dict, Optional, Any

from app.config import get_settings

settings = get_settings()


class PineconeClient:
    """Pinecone vector database client wrapper."""

    EMBEDDING_DIM = 512
    DEFAULT_NAMESPACE = "taste_embeddings"

    def __init__(self):
        self._index = None
        self._initialized = False
        self._pc = None

    def initialize(self):
        """Initialize Pinecone connection and index."""
        if self._initialized:
            return

        try:
            from pinecone import Pinecone, ServerlessSpec

            self._pc = Pinecone(api_key=settings.pinecone_api_key)

            # Create index if it doesn't exist
            index_name = settings.pinecone_index_name
            existing_indexes = [idx.name for idx in self._pc.list_indexes()]

            if index_name not in existing_indexes:
                self._pc.create_index(
                    name=index_name,
                    dimension=self.EMBEDDING_DIM,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.pinecone_environment or "us-east-1"
                    )
                )

            self._index = self._pc.Index(index_name)
            self._initialized = True
        except Exception as e:
            # Allow server to start even if Pinecone is not configured
            print(f"Warning: Pinecone initialization failed: {e}")
            self._initialized = True  # Mark as initialized to prevent retry loops

    @property
    def index(self):
        """Get Pinecone index."""
        if not self._initialized:
            self.initialize()
        return self._index

    async def upsert_user_embedding(
        self,
        user_id: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        namespace: str = None,
    ):
        """Store or update user taste embedding."""
        namespace = namespace or self.DEFAULT_NAMESPACE
        self.index.upsert(
            vectors=[
                {
                    "id": user_id,
                    "values": embedding,
                    "metadata": metadata,
                }
            ],
            namespace=namespace,
        )

    async def find_taste_twins(
        self,
        user_id: str,
        embedding: List[float],
        top_k: int = 10,
        namespace: str = None,
        filter_dict: Optional[Dict] = None,
    ) -> List[Dict]:
        """Find users with similar taste profiles (Taste Twins)."""
        namespace = namespace or self.DEFAULT_NAMESPACE

        # Query for similar vectors
        results = self.index.query(
            vector=embedding,
            top_k=top_k + 1,  # +1 to exclude self
            include_metadata=True,
            namespace=namespace,
            filter=filter_dict,
        )

        twins = []
        for match in results.matches:
            # Exclude self from results
            if match.id != user_id:
                twins.append({
                    "user_id": match.id,
                    "similarity_score": match.score,
                    "metadata": match.metadata,
                })

        return twins[:top_k]

    async def get_user_embedding(
        self,
        user_id: str,
        namespace: str = None,
    ) -> Optional[Dict]:
        """Retrieve user's stored embedding."""
        namespace = namespace or self.DEFAULT_NAMESPACE
        result = self.index.fetch(ids=[user_id], namespace=namespace)

        if user_id in result.vectors:
            vector_data = result.vectors[user_id]
            return {
                "embedding": vector_data.values,
                "metadata": vector_data.metadata,
            }
        return None

    async def delete_user_embedding(
        self,
        user_id: str,
        namespace: str = None,
    ):
        """Delete user's embedding."""
        namespace = namespace or self.DEFAULT_NAMESPACE
        self.index.delete(ids=[user_id], namespace=namespace)

    async def batch_upsert(
        self,
        vectors: List[Dict],
        namespace: str = None,
        batch_size: int = 100,
    ):
        """Batch upsert multiple vectors."""
        namespace = namespace or self.DEFAULT_NAMESPACE

        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch, namespace=namespace)

    def get_index_stats(self) -> Dict:
        """Get index statistics."""
        return self.index.describe_index_stats()

    def get_total_user_count(self, namespace: str = None) -> int:
        """Get total count of users in the index."""
        namespace = namespace or self.DEFAULT_NAMESPACE
        stats = self.index.describe_index_stats()

        # Get count from specific namespace if it exists
        if hasattr(stats, 'namespaces') and stats.namespaces:
            namespace_stats = stats.namespaces.get(namespace, {})
            if hasattr(namespace_stats, 'vector_count'):
                return namespace_stats.vector_count
            elif isinstance(namespace_stats, dict):
                return namespace_stats.get('vector_count', 0)

        # Fallback to total count
        if hasattr(stats, 'total_vector_count'):
            return stats.total_vector_count

        return 0


# Global Pinecone client instance
pinecone_client = PineconeClient()


def get_pinecone() -> PineconeClient:
    """Dependency to get Pinecone client."""
    return pinecone_client
