"""
Embedding generation service
"""
import os
# Disable TensorFlow to use PyTorch backend only
os.environ['TRANSFORMERS_NO_TF'] = '1'

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict
import pickle
from pathlib import Path


class EmbeddingService:
    """Service for generating embeddings from text"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding service
        
        Args:
            model_name: Sentence transformer model name
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def generate_embeddings(self, chunks: List[Dict]) -> np.ndarray:
        """
        Generate embeddings for transcript chunks
        
        Args:
            chunks: List of transcript chunks with text
        
        Returns:
            Numpy array of embeddings (n_chunks x embedding_dim)
        """
        texts = [chunk['text'] for chunk in chunks]
        
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            batch_size=32,
            normalize_embeddings=True,
        )
        
        return embeddings
    
    def generate_query_embedding(self, query: str) -> np.ndarray:
        """
        Generate embedding for a search query
        
        Args:
            query: Search query text
        
        Returns:
            Query embedding vector
        """
        embedding = self.model.encode(
            query,
            normalize_embeddings=True,
        )
        
        return embedding
    
    def save_embeddings(self, embeddings: np.ndarray, chunks: List[Dict], 
                       video_id: str, directory: str) -> str:
        """
        Save embeddings and chunk metadata to disk
        
        Args:
            embeddings: Numpy array of embeddings
            chunks: List of chunks
            video_id: YouTube video ID
            directory: Directory to save to
        
        Returns:
            File path
        """
        file_path = Path(directory) / f"{video_id}_embeddings.pkl"
        
        data = {
            'embeddings': embeddings,
            'chunks': chunks,
            'video_id': video_id,
            'embedding_dim': self.embedding_dim,
        }
        
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"Embeddings saved to {file_path}")
        return str(file_path)
    
    def load_embeddings(self, video_id: str, directory: str) -> Dict:
        """
        Load embeddings and metadata from disk
        
        Args:
            video_id: YouTube video ID
            directory: Directory to load from
        
        Returns:
            Dictionary with embeddings and chunks
        """
        file_path = Path(directory) / f"{video_id}_embeddings.pkl"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Embeddings file not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        return data
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
        
        Returns:
            Similarity score (0-1)
        """
        # Embeddings are already normalized, so dot product = cosine similarity
        similarity = np.dot(embedding1, embedding2)
        return float(similarity)
