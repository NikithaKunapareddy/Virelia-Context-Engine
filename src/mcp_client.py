import requests
import json
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MCPClient:
    """MCP Client for communicating with MCP servers"""

    def __init__(self, server_url: str = "http://localhost:5001"):
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()

    def make_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to the MCP server"""
        try:
            request_data = {
                "id": str(time.time()),
                "method": method,
                "params": params or {}
            }

            response = self.session.post(
                f"{self.server_url}/mcp",
                json=request_data,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            if result.get('error'):
                logger.error(f"MCP request error: {result['error']}")
                return {}

            return result.get('result', {})

        except Exception as e:
            logger.error(f"MCP client error: {e}")
            return {}

    def search_knowledge(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Search the knowledge base"""
        return self.make_request("search", {"query": query, "top_k": top_k})

    def store_memory(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Store data in memory"""
        return self.make_request("memory_store", {"user_id": user_id, "data": data})

    def search_memory(self, user_id: str, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search memory"""
        return self.make_request("memory_search", {
            "user_id": user_id,
            "query": query,
            "limit": limit
        })

    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences"""
        return self.make_request("get_preferences", {"user_id": user_id})

    def add_document(self, doc_id: str, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add document to knowledge base"""
        return self.make_request("add_document", {
            "doc_id": doc_id,
            "content": content,
            "metadata": metadata or {}
        })

    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """Delete document from knowledge base"""
        return self.make_request("delete_document", {"doc_id": doc_id})

    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return self.make_request("get_stats")

    def get_capabilities(self) -> Dict[str, Any]:
        """Get server capabilities"""
        try:
            response = self.session.get(f"{self.server_url}/capabilities", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting capabilities: {e}")
            return {}

    def health_check(self) -> bool:
        """Check if the MCP server is healthy"""
        try:
            response = self.session.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
