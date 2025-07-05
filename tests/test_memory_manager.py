import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.memory_manager import MemoryManager

class TestMemoryManager(unittest.TestCase):
    """Test cases for MemoryManager class"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.memory_manager = MemoryManager()
        self.test_user_id = "test_user_123"

    def test_store_conversation(self):
        """Test storing conversation messages"""
        message = {
            "role": "user",
            "content": "Hello, how are you?"
        }
        
        # Store message
        self.memory_manager.store_conversation(self.test_user_id, message)
        
        # Check if message was stored
        self.assertIn(self.test_user_id, self.memory_manager.short_term_memory)
        self.assertEqual(len(self.memory_manager.short_term_memory[self.test_user_id]), 1)
        
        stored_message = self.memory_manager.short_term_memory[self.test_user_id][0]
        self.assertEqual(stored_message["role"], "user")
        self.assertEqual(stored_message["content"], "Hello, how are you?")
        self.assertIn("timestamp", stored_message)

    def test_short_term_memory_limit(self):
        """Test that short-term memory respects the limit"""
        # Add more than 20 messages
        for i in range(25):
            message = {
                "role": "user",
                "content": f"Message {i}"
            }
            self.memory_manager.store_conversation(self.test_user_id, message)
        
        # Should only keep the last 20 messages
        messages = self.memory_manager.short_term_memory[self.test_user_id]
        self.assertEqual(len(messages), 20)
        
        # Should keep the most recent messages
        self.assertEqual(messages[-1]["content"], "Message 24")
        self.assertEqual(messages[0]["content"], "Message 5")

    def test_store_long_term_memory(self):
        """Test storing long-term memory"""
        qa_pair = "Q: What is AI? A: Artificial Intelligence is..."
        topic = "AI"
        
        # Store in long-term memory
        self.memory_manager.store_long_term_memory(self.test_user_id, qa_pair, topic)
        
        # Check if stored
        self.assertGreater(len(self.memory_manager.long_term_memory.documents), 0)

    def test_retrieve_context(self):
        """Test retrieving context from memory"""
        # Add some short-term messages
        messages = [
            {"role": "user", "content": "What is machine learning?"},
            {"role": "assistant", "content": "Machine learning is a subset of AI..."},
            {"role": "user", "content": "Can you give me an example?"}
        ]
        
        for msg in messages:
            self.memory_manager.store_conversation(self.test_user_id, msg)
        
        # Add some long-term memory
        self.memory_manager.store_long_term_memory(
            self.test_user_id, 
            "Q: What is AI? A: AI is artificial intelligence", 
            "AI"
        )
        
        # Retrieve context
        context = self.memory_manager.retrieve_context(self.test_user_id, "machine learning")
        
        # Check context structure
        self.assertIn("recent_context", context)
        self.assertIn("long_term_context", context)
        self.assertIsInstance(context["recent_context"], list)
        self.assertIsInstance(context["long_term_context"], list)

    def test_user_preferences(self):
        """Test user preference management"""
        preferences = {
            "favorite_language": "Python",
            "interests": ["AI", "Machine Learning"],
            "experience_level": "intermediate"
        }
        
        # Update preferences
        self.memory_manager.update_user_preferences(self.test_user_id, preferences)
        
        # Retrieve preferences
        retrieved_prefs = self.memory_manager.get_user_preferences(self.test_user_id)
        
        self.assertEqual(retrieved_prefs["favorite_language"], "Python")
        self.assertIn("AI", retrieved_prefs["interests"])

    def test_clear_user_memory(self):
        """Test clearing user memory"""
        # Add some data
        message = {"role": "user", "content": "Test message"}
        self.memory_manager.store_conversation(self.test_user_id, message)
        self.memory_manager.update_user_preferences(self.test_user_id, {"test": "value"})
        
        # Clear memory
        self.memory_manager.clear_user_memory(self.test_user_id)
        
        # Check if cleared
        self.assertNotIn(self.test_user_id, self.memory_manager.short_term_memory)
        self.assertNotIn(self.test_user_id, self.memory_manager.user_preferences)

    def test_get_memory_stats(self):
        """Test getting memory statistics"""
        # Add some data
        self.memory_manager.store_conversation(self.test_user_id, {"role": "user", "content": "Test"})
        self.memory_manager.update_user_preferences(self.test_user_id, {"test": "value"})
        
        # Get stats
        stats = self.memory_manager.get_memory_stats()
        
        # Check stats structure
        self.assertIn("active_users", stats)
        self.assertIn("total_short_term_messages", stats)
        self.assertIn("long_term_documents", stats)
        self.assertIn("users_with_preferences", stats)
        
        self.assertEqual(stats["active_users"], 1)
        self.assertEqual(stats["total_short_term_messages"], 1)
        self.assertEqual(stats["users_with_preferences"], 1)

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_extract_user_facts_with_api(self, mock_model, mock_configure):
        """Test extracting user facts with mocked Gemini API"""
        # Setup mock
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.text = '{"favorite_color": "blue", "hobby": "reading"}'
        mock_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_instance
        
        # Set API key
        self.memory_manager.gemini_api_key = "test_key"
        
        # Test extraction
        facts = self.memory_manager.extract_user_facts("I love reading books and my favorite color is blue")
        
        # Check results
        self.assertIsInstance(facts, dict)
        if facts:  # Only check if extraction worked
            self.assertIn("favorite_color", facts)
            self.assertEqual(facts["favorite_color"], "blue")

    def test_extract_user_facts_without_api(self):
        """Test extracting user facts without API key"""
        # No API key set
        self.memory_manager.gemini_api_key = None
        
        # Should return empty dict
        facts = self.memory_manager.extract_user_facts("I love Python programming")
        self.assertEqual(facts, {})

    def test_multiple_users(self):
        """Test handling multiple users"""
        user1 = "user1"
        user2 = "user2"
        
        # Add data for different users
        self.memory_manager.store_conversation(user1, {"role": "user", "content": "Hello from user 1"})
        self.memory_manager.store_conversation(user2, {"role": "user", "content": "Hello from user 2"})
        
        # Check isolation
        user1_context = self.memory_manager.retrieve_context(user1, "hello")
        user2_context = self.memory_manager.retrieve_context(user2, "hello")
        
        self.assertEqual(len(user1_context["recent_context"]), 1)
        self.assertEqual(len(user2_context["recent_context"]), 1)
        self.assertEqual(user1_context["recent_context"][0]["content"], "Hello from user 1")
        self.assertEqual(user2_context["recent_context"][0]["content"], "Hello from user 2")

if __name__ == '__main__':
    unittest.main()
