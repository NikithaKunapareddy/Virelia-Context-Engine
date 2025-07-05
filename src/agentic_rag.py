import logging
import json
import sys
import os
from typing import Dict, Any, List
from datetime import datetime
import google.generativeai as genai
from .mcp_client import MCPClient

# Add parent directory to path for config import
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import Config

logger = logging.getLogger(__name__)

class AgenticRAG:
    """Main Agentic RAG system that combines retrieval and generation"""

    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
        self.llm = None
        self.setup_llm()

    def setup_llm(self):
        """Setup Google Gemini LLM"""
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.llm = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("✅ LLM initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {e}")

    def process_query(self, query: str, user_id: str) -> str:
        """Process user query using agentic RAG approach"""
        try:
            # Step 1: Store user message in memory
            self.mcp_client.store_memory(user_id, {
                "role": "user",
                "content": query,
                "timestamp": datetime.now().isoformat()
            })

            # Step 2: Retrieve relevant knowledge and memory
            knowledge_results = self.mcp_client.search_knowledge(query, top_k=5)
            memory_results = self.mcp_client.search_memory(user_id, query, limit=5)
            user_preferences = self.mcp_client.get_user_preferences(user_id)
            
            # Debug logging
            logger.info(f"🔍 User preferences: {user_preferences}")
            logger.info(f"💭 Memory context: {memory_results}")
            logger.info(f"📚 Knowledge results: {len(knowledge_results.get('results', []))} documents")

            # Step 3: Generate response using retrieved context
            response = self.generate_response(
                query=query,
                knowledge_context=knowledge_results.get('results', []),
                memory_context=memory_results.get('data', {}),
                user_preferences=user_preferences.get('preferences', {})
            )

            # Step 4: Store assistant response in memory
            self.mcp_client.store_memory(user_id, {
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })

            return response

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"I apologize, but I encountered an error processing your request: {str(e)}"

    def generate_response(self, query: str, knowledge_context: List[Dict], 
                         memory_context: Dict, user_preferences: Dict) -> str:
        """Generate response using LLM with retrieved context"""
        try:
            if not self.llm:
                return "I apologize, but the language model is not available right now."

            # Build context for the LLM
            context_parts = []

            # Add knowledge context
            if knowledge_context:
                context_parts.append("📚 **Relevant Knowledge:**")
                for i, doc in enumerate(knowledge_context[:3], 1):
                    context_parts.append(f"{i}. {doc['content'][:500]}...")

            # Add memory context
            if memory_context.get('recent_context'):
                context_parts.append("\n💭 **Recent Conversation:**")
                for msg in memory_context['recent_context'][-3:]:
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    context_parts.append(f"- {role.title()}: {content}")

            # Add user preferences
            if user_preferences:
                context_parts.append("\n👤 **User Preferences:**")
                for key, value in user_preferences.items():
                    context_parts.append(f"- {key}: {value}")

            # Build the prompt
            system_prompt = """You are an intelligent AI assistant with access to a knowledge base and user memory. 

CRITICAL INSTRUCTIONS:
1. ALWAYS prioritize user preferences and conversation history over general knowledge
2. If the user has mentioned preferences (food, activities, etc.), use those in your responses
3. Reference previous conversation context when relevant
4. Be conversational and remember what the user has told you
5. Only use knowledge base information when it's directly relevant to the current question

Remember: You're having a conversation with someone who has shared personal preferences with you. Use that information!

Use the provided context to give helpful, accurate, and personalized responses.

Guidelines:
- Use the knowledge base information when relevant
- Consider the user's conversation history and preferences
- Be conversational and helpful
- If you don't know something, say so clearly
- Provide specific, actionable information when possible
"""

            context_text = "\n".join(context_parts) if context_parts else "No specific context available."

            full_prompt = f"""
            {system_prompt}

            **Context:**
            {context_text}

            **User Query:** {query}

            **Response:**
            """

            # Generate response
            response = self.llm.generate_content(full_prompt)
            return response.text.strip()

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."

    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze user query to determine intent and required actions"""
        try:
            if not self.llm:
                return {"intent": "unknown", "actions": []}

            intent_prompt = f"""
            Analyze the following user query and determine:
            1. The primary intent (question, request, conversation, etc.)
            2. Whether it requires knowledge base search
            3. Whether it requires memory/context
            4. Any specific actions needed

            Query: {query}

            Respond with JSON format:
            {{
                "intent": "question|request|conversation|other",
                "needs_knowledge": true|false,
                "needs_memory": true|false,
                "actions": ["search", "remember", "generate"]
            }}
            """

            response = self.llm.generate_content(intent_prompt)
            result = json.loads(response.text.strip())
            return result

        except Exception as e:
            logger.error(f"Error analyzing query intent: {e}")
            return {
                "intent": "question",
                "needs_knowledge": True,
                "needs_memory": True,
                "actions": ["search", "remember", "generate"]
            }

    def get_system_status(self) -> Dict[str, Any]:
        """Get system status for debugging"""
        try:
            mcp_healthy = self.mcp_client.health_check()
            stats = self.mcp_client.get_stats()
            
            return {
                "llm_ready": self.llm is not None,
                "mcp_healthy": mcp_healthy,
                "stats": stats,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "llm_ready": False,
                "mcp_healthy": False,
                "stats": {},
                "error": str(e)
            }
