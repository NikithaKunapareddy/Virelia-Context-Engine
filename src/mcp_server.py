import json
import logging
import time
from typing import Dict, Any
from dataclasses import dataclass
from flask import Flask, request, jsonify
import threading

from .vector_db import VectorDatabase
from .memory_manager import MemoryManager

logger = logging.getLogger(__name__)

@dataclass
class MCPRequest:
    """MCP protocol request structure"""
    id: str
    method: str
    params: Dict[str, Any]

@dataclass
class MCPResponse:
    """MCP protocol response structure"""
    id: str
    result: Dict[str, Any] = None
    error: str = None

class MCPServer:
    """MCP Server for knowledge base access"""

    def __init__(self, vector_db: VectorDatabase, memory_manager: MemoryManager):
        self.vector_db = vector_db
        self.memory_manager = memory_manager
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        """Setup Flask routes for MCP protocol"""

        @self.app.route('/mcp', methods=['POST'])
        def handle_mcp_request():
            try:
                data = request.json
                mcp_request = MCPRequest(
                    id=data.get('id', str(time.time())),
                    method=data.get('method'),
                    params=data.get('params', {})
                )

                response = self.process_request(mcp_request)
                return jsonify({
                    "id": response.id,
                    "result": response.result,
                    "error": response.error
                })
            except Exception as e:
                logger.error(f"Error processing MCP request: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({"status": "healthy"})

        @self.app.route('/capabilities', methods=['GET'])
        def get_capabilities():
            return jsonify(self._get_capabilities())

    def process_request(self, request: MCPRequest) -> MCPResponse:
        """Process MCP request and return response"""
        try:
            if request.method == "search":
                return self._handle_search(request)
            elif request.method == "memory_store":
                return self._handle_memory_store(request)
            elif request.method == "memory_search":
                return self._handle_memory_search(request)
            elif request.method == "get_preferences":
                return self._handle_get_preferences(request)
            elif request.method == "list_capabilities":
                return self._handle_list_capabilities(request)
            elif request.method == "add_document":
                return self._handle_add_document(request)
            elif request.method == "delete_document":
                return self._handle_delete_document(request)
            elif request.method == "get_stats":
                return self._handle_get_stats(request)
            else:
                return MCPResponse(
                    id=request.id,
                    error=f"Unknown method: {request.method}"
                )
        except Exception as e:
            return MCPResponse(
                id=request.id,
                error=str(e)
            )

    def _handle_search(self, request: MCPRequest) -> MCPResponse:
        """Handle knowledge base search"""
        query = request.params.get("query", "")
        top_k = request.params.get("top_k", 5)

        results = self.vector_db.search(query, top_k)

        return MCPResponse(
            id=request.id,
            result={"results": results}
        )

    def _handle_memory_store(self, request: MCPRequest) -> MCPResponse:
        """Handle memory storage"""
        user_id = request.params.get("user_id")
        data = request.params.get("data")

        self.memory_manager.store_conversation(user_id, data)

        return MCPResponse(
            id=request.id,
            result={"status": "stored"}
        )

    def _handle_memory_search(self, request: MCPRequest) -> MCPResponse:
        """Handle memory search"""
        user_id = request.params.get("user_id")
        query = request.params.get("query")
        limit = request.params.get("limit", 10)

        context = self.memory_manager.retrieve_context(user_id, query, limit)

        return MCPResponse(
            id=request.id,
            result={"data": context}
        )

    def _handle_get_preferences(self, request: MCPRequest) -> MCPResponse:
        """Handle get user preferences"""
        user_id = request.params.get("user_id")
        preferences = self.memory_manager.get_user_preferences(user_id)

        return MCPResponse(
            id=request.id,
            result={"preferences": preferences}
        )

    def _handle_add_document(self, request: MCPRequest) -> MCPResponse:
        """Handle add document to knowledge base"""
        doc_id = request.params.get("doc_id")
        content = request.params.get("content")
        metadata = request.params.get("metadata", {})

        self.vector_db.add_document(doc_id, content, metadata)

        return MCPResponse(
            id=request.id,
            result={"status": "added", "doc_id": doc_id}
        )

    def _handle_delete_document(self, request: MCPRequest) -> MCPResponse:
        """Handle delete document from knowledge base"""
        doc_id = request.params.get("doc_id")
        success = self.vector_db.delete_document(doc_id)

        return MCPResponse(
            id=request.id,
            result={"status": "deleted" if success else "not_found", "doc_id": doc_id}
        )

    def _handle_get_stats(self, request: MCPRequest) -> MCPResponse:
        """Handle get system statistics"""
        db_stats = self.vector_db.get_stats()
        memory_stats = self.memory_manager.get_memory_stats()

        return MCPResponse(
            id=request.id,
            result={
                "database": db_stats,
                "memory": memory_stats
            }
        )

    def _handle_list_capabilities(self, request: MCPRequest) -> MCPResponse:
        """List server capabilities"""
        return MCPResponse(
            id=request.id,
            result=self._get_capabilities()
        )

    def _get_capabilities(self) -> Dict[str, Any]:
        """Get server capabilities"""
        return {
            "methods": [
                {
                    "name": "search",
                    "description": "Search the knowledge base",
                    "params": {"query": "string", "top_k": "number"}
                },
                {
                    "name": "memory_store",
                    "description": "Store data in memory",
                    "params": {"user_id": "string", "data": "object"}
                },
                {
                    "name": "memory_search",
                    "description": "Search memory",
                    "params": {"user_id": "string", "query": "string", "limit": "number"}
                },
                {
                    "name": "get_preferences",
                    "description": "Get user preferences",
                    "params": {"user_id": "string"}
                },
                {
                    "name": "add_document",
                    "description": "Add document to knowledge base",
                    "params": {"doc_id": "string", "content": "string", "metadata": "object"}
                },
                {
                    "name": "delete_document",
                    "description": "Delete document from knowledge base",
                    "params": {"doc_id": "string"}
                },
                {
                    "name": "get_stats",
                    "description": "Get system statistics",
                    "params": {}
                }
            ]
        }

    def start_server(self, port: int = 5001):
        """Start the MCP server"""
        def run_server():
            self.app.run(host='0.0.0.0', port=port, debug=False)

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        logger.info(f"MCP Server started on port {port}")
        return server_thread
