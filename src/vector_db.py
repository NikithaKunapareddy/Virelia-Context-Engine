import numpy as np
import faiss
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

@dataclass
class Document:
    """Represents a document in the knowledge base"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None

class VectorDatabase:
    """FAISS-based vector database for knowledge storage"""

    def __init__(self, embedding_model_name: str = "all-MiniLM-L6-v2"):
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.documents: Dict[str, Document] = {}
        self.index = None
        self.dimension = None
        self.doc_ids = []  # Keep track of document order

    def _get_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        return self.embedding_model.encode([text])[0]

    def add_document(self, doc_id: str, content: str, metadata: Dict[str, Any] = None):
        """Add document to the vector database"""
        try:
            embedding = self._get_embedding(content)

            if self.index is None:
                self.dimension = len(embedding)
                self.index = faiss.IndexFlatL2(self.dimension)

            # Store document
            doc = Document(
                id=doc_id,
                content=content,
                metadata=metadata or {},
                embedding=embedding
            )
            
            # If document already exists, update it
            if doc_id in self.documents:
                # Find and update existing document
                idx = self.doc_ids.index(doc_id)
                self.documents[doc_id] = doc
                # Update embedding in index (rebuild for simplicity)
                self._rebuild_index()
            else:
                # Add new document
                self.documents[doc_id] = doc
                self.doc_ids.append(doc_id)
                self.index.add(embedding.reshape(1, -1))

            logger.info(f"Added/Updated document {doc_id} to vector database")
            
        except Exception as e:
            logger.error(f"Error adding document {doc_id}: {e}")
            raise

    def _rebuild_index(self):
        """Rebuild the FAISS index"""
        if not self.documents:
            return
            
        self.index = faiss.IndexFlatL2(self.dimension)
        embeddings = []
        
        for doc_id in self.doc_ids:
            if doc_id in self.documents:
                embeddings.append(self.documents[doc_id].embedding)
        
        if embeddings:
            embeddings_array = np.array(embeddings)
            self.index.add(embeddings_array)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            if self.index is None or len(self.documents) == 0:
                return []

            query_embedding = self._get_embedding(query)
            distances, indices = self.index.search(query_embedding.reshape(1, -1), min(top_k, len(self.doc_ids)))

            results = []
            for distance, idx in zip(distances[0], indices[0]):
                if idx < len(self.doc_ids):
                    doc_id = self.doc_ids[idx]
                    doc = self.documents[doc_id]
                    results.append({
                        "id": doc.id,
                        "content": doc.content,
                        "metadata": doc.metadata,
                        "similarity_score": float(1 / (1 + distance))
                    })

            return results
            
        except Exception as e:
            logger.error(f"Error searching vector database: {e}")
            return []

    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get a specific document by ID"""
        return self.documents.get(doc_id)

    def list_documents(self) -> List[str]:
        """List all document IDs"""
        return list(self.documents.keys())

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the database"""
        try:
            if doc_id in self.documents:
                del self.documents[doc_id]
                self.doc_ids.remove(doc_id)
                self._rebuild_index()
                logger.info(f"Deleted document {doc_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            "total_documents": len(self.documents),
            "dimension": self.dimension,
            "model": self.embedding_model.get_sentence_embedding_dimension() if hasattr(self.embedding_model, 'get_sentence_embedding_dimension') else 'unknown'
        }
