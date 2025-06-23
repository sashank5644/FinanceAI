"""Pinecone vector database management."""

import logging
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
import numpy as np

from config import settings

logger = logging.getLogger(__name__)

_pinecone_client: Optional[Pinecone] = None
_index = None


def init_pinecone():
    """Initialize Pinecone client."""
    global _pinecone_client
    
    if not settings.pinecone_api_key:
        logger.warning("Pinecone API key not configured")
        return None
    
    try:
        _pinecone_client = Pinecone(api_key=settings.pinecone_api_key)
        logger.info("Pinecone client initialized")
        
        # Create index if it doesn't exist
        create_index_if_not_exists()
        
        return _pinecone_client
    except Exception as e:
        logger.error(f"Failed to initialize Pinecone: {e}")
        raise


def create_index_if_not_exists():
    """Create Pinecone index if it doesn't exist."""
    if not _pinecone_client:
        return
    
    index_name = settings.pinecone_index_name
    
    # Check if index exists
    existing_indexes = [idx.name for idx in _pinecone_client.list_indexes()]
    
    if index_name not in existing_indexes:
        logger.info(f"Creating Pinecone index: {index_name}")
        
        # Create index with serverless spec
        _pinecone_client.create_index(
            name=index_name,
            dimension=1536,  # OpenAI embedding dimension
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region=settings.pinecone_environment or "us-east-1"
            )
        )
        
        logger.info(f"Pinecone index '{index_name}' created")


def get_pinecone_index():
    """Get Pinecone index instance."""
    global _index
    
    if _index is None:
        if _pinecone_client is None:
            init_pinecone()
        
        if _pinecone_client:
            _index = _pinecone_client.Index(settings.pinecone_index_name)
    
    return _index


def upsert_embeddings(
    vectors: List[Dict[str, Any]],
    namespace: str = ""
):
    """Upsert embeddings to Pinecone.
    
    Args:
        vectors: List of dicts with 'id', 'values', and 'metadata'
        namespace: Optional namespace for organization
    """
    index = get_pinecone_index()
    if not index:
        raise Exception("Pinecone index not available")
    
    # Upsert in batches of 100
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch, namespace=namespace)
    
    logger.info(f"Upserted {len(vectors)} vectors to Pinecone")


def search_similar(
    query_vector: List[float],
    top_k: int = 10,
    namespace: str = "",
    filter: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """Search for similar vectors.
    
    Args:
        query_vector: Query embedding vector
        top_k: Number of results to return
        namespace: Optional namespace
        filter: Optional metadata filter
    
    Returns:
        List of matches with scores and metadata
    """
    index = get_pinecone_index()
    if not index:
        raise Exception("Pinecone index not available")
    
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        namespace=namespace,
        filter=filter,
        include_metadata=True
    )
    
    return results.matches


def delete_vectors(
    ids: List[str],
    namespace: str = ""
):
    """Delete vectors by ID."""
    index = get_pinecone_index()
    if not index:
        raise Exception("Pinecone index not available")
    
    index.delete(ids=ids, namespace=namespace)
    logger.info(f"Deleted {len(ids)} vectors from Pinecone")
