import unittest
import numpy as np
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.vector_db import VectorDatabase, Document

class TestVectorDatabase(unittest.TestCase):
    """Test cases for VectorDatabase class"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.db = VectorDatabase()
        
        # Add some test documents
        self.test_docs = [
            {
                "id": "doc1",
                "content": "Artificial intelligence is a branch of computer science",
                "metadata": {"topic": "AI", "type": "definition"}
            },
            {
                "id": "doc2", 
                "content": "Machine learning algorithms can learn from data",
                "metadata": {"topic": "ML", "type": "explanation"}
            },
            {
                "id": "doc3",
                "content": "Neural networks are inspired by biological neurons",
                "metadata": {"topic": "Neural Networks", "type": "concept"}
            }
        ]
        
        for doc in self.test_docs:
            self.db.add_document(doc["id"], doc["content"], doc["metadata"])

    def test_add_document(self):
        """Test adding a document to the database"""
        doc_id = "test_doc"
        content = "This is a test document"
        metadata = {"topic": "test", "type": "unit_test"}
        
        # Add document
        self.db.add_document(doc_id, content, metadata)
        
        # Check if document was added
        self.assertIn(doc_id, self.db.documents)
        self.assertEqual(self.db.documents[doc_id].content, content)
        self.assertEqual(self.db.documents[doc_id].metadata, metadata)

    def test_search(self):
        """Test searching the database"""
        # Search for AI-related content
        results = self.db.search("artificial intelligence", top_k=2)
        
        # Should return results
        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), 2)
        
        # Results should have required fields
        for result in results:
            self.assertIn("id", result)
            self.assertIn("content", result)
            self.assertIn("metadata", result)
            self.assertIn("similarity_score", result)
            self.assertIsInstance(result["similarity_score"], float)

    def test_get_document(self):
        """Test retrieving a specific document"""
        doc = self.db.get_document("doc1")
        
        self.assertIsNotNone(doc)
        self.assertEqual(doc.id, "doc1")
        self.assertIn("Artificial intelligence", doc.content)

    def test_list_documents(self):
        """Test listing all document IDs"""
        doc_ids = self.db.list_documents()
        
        self.assertEqual(len(doc_ids), 3)
        self.assertIn("doc1", doc_ids)
        self.assertIn("doc2", doc_ids)
        self.assertIn("doc3", doc_ids)

    def test_delete_document(self):
        """Test deleting a document"""
        # Delete a document
        success = self.db.delete_document("doc2")
        
        self.assertTrue(success)
        self.assertNotIn("doc2", self.db.documents)
        
        # Try to delete non-existent document
        success = self.db.delete_document("non_existent")
        self.assertFalse(success)

    def test_update_document(self):
        """Test updating an existing document"""
        new_content = "Updated content about artificial intelligence"
        new_metadata = {"topic": "AI", "type": "updated"}
        
        # Update document
        self.db.add_document("doc1", new_content, new_metadata)
        
        # Check if document was updated
        doc = self.db.get_document("doc1")
        self.assertEqual(doc.content, new_content)
        self.assertEqual(doc.metadata, new_metadata)

    def test_get_stats(self):
        """Test getting database statistics"""
        stats = self.db.get_stats()
        
        self.assertIn("total_documents", stats)
        self.assertIn("dimension", stats)
        self.assertEqual(stats["total_documents"], 3)
        self.assertIsNotNone(stats["dimension"])

    def test_empty_search(self):
        """Test search with empty database"""
        empty_db = VectorDatabase()
        results = empty_db.search("test query")
        
        self.assertEqual(len(results), 0)

    def test_embedding_consistency(self):
        """Test that embeddings are consistent"""
        content = "Test content for embedding"
        
        # Get embedding twice
        embedding1 = self.db._get_embedding(content)
        embedding2 = self.db._get_embedding(content)
        
        # Should be identical
        np.testing.assert_array_equal(embedding1, embedding2)

if __name__ == '__main__':
    unittest.main()
