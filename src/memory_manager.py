import json
import logging
from typing import Dict, List, Any
from datetime import datetime
import hashlib
import time
from .vector_db import VectorDatabase
import google.generativeai as genai

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages long-term and short-term memory for the agent"""

    def __init__(self, gemini_api_key: str = None):
        self.short_term_memory: Dict[str, List[Dict]] = {}
        self.long_term_memory = VectorDatabase()
        self.user_preferences: Dict[str, Dict] = {}
        self.gemini_api_key = gemini_api_key

    def store_conversation(self, user_id: str, message: Dict[str, Any]):
        """Store conversation in short-term memory"""
        try:
            if user_id not in self.short_term_memory:
                self.short_term_memory[user_id] = []

            self.short_term_memory[user_id].append({
                **message,
                "timestamp": datetime.now().isoformat()
            })

            # Limit short-term memory size
            if len(self.short_term_memory[user_id]) > 20:
                self.short_term_memory[user_id] = self.short_term_memory[user_id][-20:]

            # Extract user preferences/facts from message
            if message.get("role") == "user":
                content = message.get("content", "")
                extracted = self.extract_user_facts(content)
                if extracted:
                    self.update_user_preferences(user_id, extracted)
                    
        except Exception as e:
            logger.error(f"Error storing conversation: {e}")

    def extract_user_facts(self, text: str) -> Dict:
        """Extract user facts/preferences using Gemini LLM"""
        try:
            if not self.gemini_api_key:
                return {}
                
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = (
                "Extract all facts, preferences, or personal information about the user from the following message. "
                "Return a JSON object where each key is a descriptive label for the fact or preference, "
                "and each value is the corresponding value(s) as stated or implied by the user. "
                "If nothing is found, return an empty JSON object.\n"
                f"User message: {text}"
            )
            
            response = model.generate_content(prompt)
            extracted = response.text.strip()
            
            # Clean JSON if needed
            if extracted.startswith('```'):
                extracted = extracted.split('```')[1]
                if extracted.startswith('json'):
                    extracted = extracted[4:]
            
            facts = json.loads(extracted)
            if isinstance(facts, dict):
                return facts
            return {}
            
        except Exception as e:
            logger.error(f"User fact extraction failed: {e}")
            return {}

    def store_long_term_memory(self, user_id: str, qa_pair: str, topic: str = "general"):
        """Store Q&A in long-term vector memory"""
        try:
            memory_id = hashlib.md5(f"{user_id}_{qa_pair}_{time.time()}".encode()).hexdigest()
            self.long_term_memory.add_document(
                memory_id,
                qa_pair,
                {
                    "user_id": user_id,
                    "type": "Q&A",
                    "topic": topic,
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error storing long-term memory: {e}")

    def retrieve_context(self, user_id: str, query: str, limit: int = 10) -> Dict:
        """Retrieve relevant context from memory"""
        try:
            # Get short-term memory
            recent_context = self.short_term_memory.get(user_id, [])[-limit:]

            # Search long-term memory
            long_term_results = self.long_term_memory.search(query, top_k=3)

            return {
                "recent_context": recent_context,
                "long_term_context": long_term_results
            }
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return {"recent_context": [], "long_term_context": []}

    def get_user_preferences(self, user_id: str) -> Dict:
        """Get stored user preferences"""
        try:
            prefs = self.user_preferences.get(user_id, {})
            # Deduplicate list values
            for k, v in prefs.items():
                if isinstance(v, list):
                    prefs[k] = list(dict.fromkeys([str(d).strip().lower() for d in v if str(d).strip()]))
            return prefs
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {}

    def update_user_preferences(self, user_id: str, preferences: Dict):
        """Update user preferences"""
        try:
            if user_id not in self.user_preferences:
                self.user_preferences[user_id] = {}
            self.user_preferences[user_id].update(preferences)
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")

    def clear_user_memory(self, user_id: str):
        """Clear all memory for a user"""
        try:
            if user_id in self.short_term_memory:
                del self.short_term_memory[user_id]
            if user_id in self.user_preferences:
                del self.user_preferences[user_id]
            logger.info(f"Cleared memory for user {user_id}")
        except Exception as e:
            logger.error(f"Error clearing user memory: {e}")

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        return {
            "active_users": len(self.short_term_memory),
            "total_short_term_messages": sum(len(msgs) for msgs in self.short_term_memory.values()),
            "long_term_documents": len(self.long_term_memory.documents),
            "users_with_preferences": len(self.user_preferences)
        }
