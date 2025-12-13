"""Semantic document retrieval using embeddings."""

from typing import List, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import hashlib
from constants import EMBEDDING_DIM


# Sample document corpus for retrieval
DOCUMENT_CORPUS = [
    {
        "id": "doc_1",
        "content": "Effective social media posts start with a strong hook that captures attention within the first 3 seconds. Use questions, bold statements, or surprising facts.",
        "category": "social_media"
    },
    {
        "id": "doc_2",
        "content": "Instagram content performs best with authentic storytelling, behind-the-scenes content, and relatable experiences. Use 3-5 relevant hashtags for optimal reach.",
        "category": "instagram"
    },
    {
        "id": "doc_3",
        "content": "LinkedIn posts should provide professional value through insights, lessons learned, or industry expertise. Personal stories with professional takeaways drive engagement.",
        "category": "linkedin"
    },
    {
        "id": "doc_4",
        "content": "YouTube scripts need a compelling hook in the first 15 seconds, clear structure with timestamps, and a strong call-to-action for subscriptions and engagement.",
        "category": "youtube"
    },
    {
        "id": "doc_5",
        "content": "Call-to-action phrases that convert: 'Join now', 'Get started today', 'Don't miss out', 'Limited time offer', 'Click the link in bio'.",
        "category": "cta"
    },
    {
        "id": "doc_6",
        "content": "Engaging content uses the AIDA framework: Attention (hook), Interest (value proposition), Desire (benefits), Action (clear CTA).",
        "category": "framework"
    },
    {
        "id": "doc_7",
        "content": "Storytelling elements that resonate: conflict and resolution, personal transformation, lessons from failure, unexpected insights, and authentic vulnerability.",
        "category": "storytelling"
    },
    {
        "id": "doc_8",
        "content": "Content formatting tips: Use short paragraphs, bullet points for lists, emojis for visual breaks, and white space for readability on mobile devices.",
        "category": "formatting"
    },
    {
        "id": "doc_9",
        "content": "Emotional triggers in content: curiosity, fear of missing out, desire for belonging, aspiration for success, and need for validation.",
        "category": "psychology"
    },
    {
        "id": "doc_10",
        "content": "Video content structure: Hook (0-15s), Context (15-60s), Main Content (1-5min), Summary (30s), Call-to-Action (15s).",
        "category": "video"
    }
]



def _simple_embed(text: str, dim: int = EMBEDDING_DIM) -> np.ndarray:
    """
    Create a simple deterministic embedding for text.
    Uses character-based hashing for consistent embeddings.
    
    Args:
        text: Text to embed
        dim: Embedding dimension (defaults to EMBEDDING_DIM from constants)
        
    Returns:
        Numpy array embedding of specified dimension
    """
    text_lower = text.lower()
    
    # Create hash-based embedding - handle dimension properly
    hash_obj = hashlib.sha256(text_lower.encode())
    hash_bytes = hash_obj.digest()
    
    # Convert to float array, pad with zeros if needed to reach dim
    hash_values = [b / 255.0 for b in hash_bytes]
    if len(hash_values) < dim:
        # Pad with additional hash-derived values
        additional_hash = hashlib.md5(text_lower.encode()).digest()
        while len(hash_values) < dim:
            for b in additional_hash:
                hash_values.append(b / 255.0)
                if len(hash_values) >= dim:
                    break
    embedding = np.array(hash_values[:dim])
    
    # Add word-based features
    words = text_lower.split()
    word_features = np.zeros(dim)
    
    for i, word in enumerate(words[:dim]):
        word_hash = hashlib.md5(word.encode()).digest()
        word_features[i % dim] += word_hash[0] / 255.0
    
    # Combine embeddings
    combined = (embedding + word_features) / 2
    
    # Normalize
    norm = np.linalg.norm(combined)
    if norm > 0:
        combined = combined / norm
    
    return combined


def _compute_document_embeddings() -> List[Tuple[dict, np.ndarray]]:
    """
    Compute embeddings for all documents in corpus.
    
    Returns:
        List of (document, embedding) tuples
    """
    return [(doc, _simple_embed(doc["content"])) for doc in DOCUMENT_CORPUS]


# Pre-compute document embeddings
_DOC_EMBEDDINGS = _compute_document_embeddings()


def retrieve_documents(query: str, top_k: int = 3) -> List[str]:
    """
    Retrieve most relevant documents for a query.
    
    Args:
        query: Search query
        top_k: Number of documents to retrieve
        
    Returns:
        List of relevant document contents
    """
    query_embedding = _simple_embed(query).reshape(1, -1)
    
    # Calculate similarities
    similarities = []
    for doc, doc_embedding in _DOC_EMBEDDINGS:
        sim = cosine_similarity(query_embedding, doc_embedding.reshape(1, -1))[0][0]
        similarities.append((doc, sim))
    
    # Sort by similarity
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Return top_k documents
    return [doc["content"] for doc, _ in similarities[:top_k]]


def retrieve_documents_with_scores(query: str, top_k: int = 3) -> List[Tuple[str, float]]:
    """
    Retrieve most relevant documents with similarity scores.
    
    Args:
        query: Search query
        top_k: Number of documents to retrieve
        
    Returns:
        List of (document_content, similarity_score) tuples
    """
    query_embedding = _simple_embed(query).reshape(1, -1)
    
    similarities = []
    for doc, doc_embedding in _DOC_EMBEDDINGS:
        sim = cosine_similarity(query_embedding, doc_embedding.reshape(1, -1))[0][0]
        similarities.append((doc["content"], sim))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return similarities[:top_k]
