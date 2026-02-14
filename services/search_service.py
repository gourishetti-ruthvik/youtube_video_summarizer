"""
Semantic search service using FAISS
"""
import faiss
import numpy as np
from typing import List, Dict, Tuple
from pathlib import Path
import pickle


class SearchService:
    """Service for semantic search using FAISS"""
    
    def __init__(self):
        """Initialize search service"""
        self.index = None
        self.chunks = None
        self.video_id = None
    
    def create_index(self, embeddings: np.ndarray, chunks: List[Dict], 
                     video_id: str) -> None:
        """
        Create FAISS index from embeddings
        
        Args:
            embeddings: Numpy array of embeddings (n_chunks x dim)
            chunks: List of transcript chunks
            video_id: YouTube video ID
        """
        # Ensure embeddings are float32
        embeddings = embeddings.astype('float32')
        
        # Create FAISS index (inner product for normalized vectors = cosine similarity)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        
        # Add embeddings to index
        self.index.add(embeddings)
        self.chunks = chunks
        self.video_id = video_id
        
        print(f"FAISS index created with {self.index.ntotal} vectors")
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict]:
        """
        Search for similar chunks using query embedding
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
        
        Returns:
            List of matching chunks with scores and metadata
        """
        if self.index is None:
            raise ValueError("Index not created. Call create_index first.")
        
        # Ensure query is float32 and 2D
        query_embedding = query_embedding.astype('float32')
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Search for more candidates initially for better filtering
        initial_k = min(top_k * 3, self.index.ntotal)
        scores, indices = self.index.search(query_embedding, initial_k)
        
        # Format results with enhanced scoring
        results = []
        seen_timestamps = set()
        
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx]
                
                # Skip duplicate or very similar timestamps (within 5 seconds)
                skip = False
                for seen_ts in seen_timestamps:
                    if abs(chunk['start_time'] - seen_ts) < 5:
                        skip = True
                        break
                
                if skip:
                    continue
                
                seen_timestamps.add(chunk['start_time'])
                
                results.append({
                    'chunk_id': chunk['chunk_id'],
                    'text': chunk['text'],
                    'timestamp': chunk['timestamp'],
                    'start_time': chunk['start_time'],
                    'end_time': chunk['end_time'],
                    'score': float(score),
                    'relevance': self._score_to_relevance(float(score)),
                })
                
                # Stop when we have enough unique results
                if len(results) >= top_k:
                    break
        
        print(f"  Filtered {len(results)} unique chunks from {initial_k} candidates")
        return results
    
    def save_index(self, directory: str) -> str:
        """
        Save FAISS index and metadata to disk
        
        Args:
            directory: Directory to save to
        
        Returns:
            File path
        """
        if self.index is None:
            raise ValueError("No index to save")
        
        index_path = Path(directory) / f"{self.video_id}_faiss.index"
        metadata_path = Path(directory) / f"{self.video_id}_metadata.pkl"
        
        # Save FAISS index
        faiss.write_index(self.index, str(index_path))
        
        # Save metadata
        metadata = {
            'chunks': self.chunks,
            'video_id': self.video_id,
        }
        
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"FAISS index saved to {index_path}")
        return str(index_path)
    
    def load_index(self, video_id: str, directory: str) -> None:
        """
        Load FAISS index and metadata from disk
        
        Args:
            video_id: YouTube video ID
            directory: Directory to load from
        """
        index_path = Path(directory) / f"{video_id}_faiss.index"
        metadata_path = Path(directory) / f"{video_id}_metadata.pkl"
        
        if not index_path.exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")
        
        # Load FAISS index
        self.index = faiss.read_index(str(index_path))
        
        # Load metadata
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        
        self.chunks = metadata['chunks']
        self.video_id = metadata['video_id']
        
        print(f"FAISS index loaded with {self.index.ntotal} vectors")
    
    def _score_to_relevance(self, score: float) -> str:
        """
        Convert similarity score to relevance label
        
        Args:
            score: Cosine similarity score (0-1 for normalized vectors)
        
        Returns:
            Relevance label
        """
        # Adjusted thresholds for better granularity
        if score >= 0.60:
            return "High"
        elif score >= 0.40:
            return "Medium"
        else:
            return "Low"
    
    def get_chunk_by_id(self, chunk_id: int) -> Dict:
        """
        Get chunk by ID
        
        Args:
            chunk_id: Chunk ID
        
        Returns:
            Chunk dictionary
        """
        if self.chunks is None:
            raise ValueError("No chunks loaded")
        
        for chunk in self.chunks:
            if chunk['chunk_id'] == chunk_id:
                return chunk
        
        return None
    
    def get_all_chunks(self) -> List[Dict]:
        """
        Get all chunks
        
        Returns:
            List of all chunks
        """
        return self.chunks if self.chunks else []
