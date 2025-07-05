import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.agentic_rag import AgenticRAG

class TestAgenticRAG(unittest.TestCase):
    """Test cases for AgenticRAG class"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create mock MCP client
        self.mock_mcp_client = Mock()
        
        # Setup mock responses
        self.mock_mcp_client.search_knowledge.return_value = {
            "results": [
                {
                    "id": "doc1",
                    "content": "Artificial intelligence is a branch of computer science",
                    "metadata": {"topic": "AI"},
                    "similarity_score": 0.9
                }
            ]
        }
        
        self.mock_mcp_client.search_memory.return_value = {
            "data": {
                "recent_context": [
                    {"role": "user", "content": "What is AI?", "timestamp": "2024-01-01T10:00:00"}
                ],
                "long_term_context": []
            }
        }
        
        self.mock_mcp_client.get_user_preferences.return_value = {
            "preferences": {
                "favorite_language": "Python",
                "interests": ["AI", "Programming"]
            }
        }
        
        self.mock_mcp_client.store_memory.return_value = {"status": "stored"}
        
        # Create AgenticRAG instance
        self.agent = AgenticRAG(self.mock_mcp_client)

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_setup_llm(self, mock_model, mock_configure):
        """Test LLM setup"""
        # Create new instance to test setup
        agent = AgenticRAG(self.mock_mcp_client)
        
        # Check if LLM was configured
        mock_configure.assert_called()
        mock_model.assert_called_with('gemini-1.5-flash')

    def test_process_query_structure(self):
        """Test the structure of query processing"""
        # Mock the LLM response
        with patch.object(self.agent, 'generate_response') as mock_generate:
            mock_generate.return_value = "This is a test response"
            
            # Process query
            response = self.agent.process_query("What is AI?", "test_user")
            
            # Check if all steps were called
            self.mock_mcp_client.store_memory.assert_called()
            self.mock_mcp_client.search_knowledge.assert_called_with("What is AI?", top_k=5)
            self.mock_mcp_client.search_memory.assert_called_with("test_user", "What is AI?", limit=5)
            self.mock_mcp_client.get_user_preferences.assert_called_with("test_user")
            mock_generate.assert_called()
            
            # Check response
            self.assertEqual(response, "This is a test response")

    def test_process_query_with_error(self):
        """Test query processing with error handling"""
        # Make MCP client raise an exception
        self.mock_mcp_client.search_knowledge.side_effect = Exception("Test error")
        
        # Process query
        response = self.agent.process_query("What is AI?", "test_user")
        
        # Should return error message
        self.assertIn("error", response.lower())

    @patch('google.generativeai.GenerativeModel')
    def test_generate_response(self, mock_model):
        """Test response generation"""
        # Mock LLM response
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.text = "AI is artificial intelligence, a field of computer science."
        mock_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_instance
        
        # Set up agent with mock
        self.agent.llm = mock_instance
        
        # Test response generation
        response = self.agent.generate_response(
            query="What is AI?",
            knowledge_context=[{"content": "AI is artificial intelligence"}],
            memory_context={"recent_context": []},
            user_preferences={}
        )
        
        # Check response
        self.assertEqual(response, "AI is artificial intelligence, a field of computer science.")
        mock_instance.generate_content.assert_called_once()

    def test_generate_response_no_llm(self):
        """Test response generation without LLM"""
        # Set LLM to None
        self.agent.llm = None
        
        # Generate response
        response = self.agent.generate_response(
            query="What is AI?",
            knowledge_context=[],
            memory_context={},
            user_preferences={}
        )
        
        # Should return error message
        self.assertIn("language model", response.lower())

    @patch('google.generativeai.GenerativeModel')
    def test_analyze_query_intent(self, mock_model):
        """Test query intent analysis"""
        # Mock LLM response
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.text = '''
        {
            "intent": "question",
            "needs_knowledge": true,
            "needs_memory": true,
            "actions": ["search", "remember", "generate"]
        }
        '''
        mock_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_instance
        
        # Set up agent with mock
        self.agent.llm = mock_instance
        
        # Analyze intent
        intent = self.agent.analyze_query_intent("What is machine learning?")
        
        # Check intent structure
        self.assertIn("intent", intent)
        self.assertIn("needs_knowledge", intent)
        self.assertIn("needs_memory", intent)
        self.assertIn("actions", intent)
        
        self.assertEqual(intent["intent"], "question")
        self.assertTrue(intent["needs_knowledge"])
        self.assertTrue(intent["needs_memory"])

    def test_analyze_query_intent_no_llm(self):
        """Test query intent analysis without LLM"""
        # Set LLM to None
        self.agent.llm = None
        
        # Analyze intent
        intent = self.agent.analyze_query_intent("What is AI?")
        
        # Should return default intent
        self.assertEqual(intent["intent"], "question")
        self.assertTrue(intent["needs_knowledge"])
        self.assertTrue(intent["needs_memory"])

    def test_get_system_status(self):
        """Test getting system status"""
        # Mock health check
        self.mock_mcp_client.health_check.return_value = True
        self.mock_mcp_client.get_stats.return_value = {
            "database": {"total_documents": 10},
            "memory": {"active_users": 5}
        }
        
        # Get status
        status = self.agent.get_system_status()
        
        # Check status structure
        self.assertIn("llm_ready", status)
        self.assertIn("mcp_healthy", status)
        self.assertIn("stats", status)
        self.assertIn("timestamp", status)
        
        self.assertTrue(status["mcp_healthy"])
        self.assertEqual(status["stats"]["database"]["total_documents"], 10)

    def test_get_system_status_with_error(self):
        """Test getting system status with error"""
        # Make health check raise an exception
        self.mock_mcp_client.health_check.side_effect = Exception("Connection error")
        
        # Get status
        status = self.agent.get_system_status()
        
        # Should handle error gracefully
        self.assertIn("error", status)
        self.assertFalse(status["llm_ready"])
        self.assertFalse(status["mcp_healthy"])

    def test_context_building(self):
        """Test how context is built for LLM"""
        # Mock generate_response to capture the prompt
        with patch.object(self.agent, 'llm') as mock_llm:
            mock_response = Mock()
            mock_response.text = "Test response"
            mock_llm.generate_content.return_value = mock_response
            
            # Generate response with different contexts
            self.agent.generate_response(
                query="What is AI?",
                knowledge_context=[
                    {"content": "AI is artificial intelligence", "metadata": {"topic": "AI"}}
                ],
                memory_context={
                    "recent_context": [
                        {"role": "user", "content": "Hello"}
                    ]
                },
                user_preferences={"favorite_language": "Python"}
            )
            
            # Check if generate_content was called
            mock_llm.generate_content.assert_called_once()
            
            # Get the prompt that was passed
            call_args = mock_llm.generate_content.call_args[0]
            prompt = call_args[0]
            
            # Check if context elements are in the prompt
            self.assertIn("AI is artificial intelligence", prompt)
            self.assertIn("Hello", prompt)
            self.assertIn("Python", prompt)
            self.assertIn("What is AI?", prompt)

    def test_memory_storage_calls(self):
        """Test that memory storage is called correctly"""
        with patch.object(self.agent, 'generate_response') as mock_generate:
            mock_generate.return_value = "Test response"
            
            # Process query
            self.agent.process_query("Test query", "test_user")
            
            # Check memory storage calls
            calls = self.mock_mcp_client.store_memory.call_args_list
            self.assertEqual(len(calls), 2)  # User message + Assistant response
            
            # Check first call (user message)
            user_call = calls[0][1]
            self.assertEqual(user_call["user_id"], "test_user")
            self.assertEqual(user_call["data"]["role"], "user")
            self.assertEqual(user_call["data"]["content"], "Test query")
            
            # Check second call (assistant response)
            assistant_call = calls[1][1]
            self.assertEqual(assistant_call["user_id"], "test_user")
            self.assertEqual(assistant_call["data"]["role"], "assistant")
            self.assertEqual(assistant_call["data"]["content"], "Test response")

if __name__ == '__main__':
    unittest.main()
