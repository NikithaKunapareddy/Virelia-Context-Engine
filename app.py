import os
import sys
import logging
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import threading
import time
from datetime import datetime
import uuid

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.vector_db import VectorDatabase
from src.memory_manager import MemoryManager
from src.mcp_server import MCPServer
from src.mcp_client import MCPClient
from src.agentic_rag import AgenticRAG
from src.utils import setup_knowledge_base
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*", manage_session=False)

# Global variables for system components
vector_db = None
memory_manager = None
mcp_server = None
mcp_client = None
agent = None

def initialize_system():
    """Initialize the Agentic RAG system"""
    global vector_db, memory_manager, mcp_server, mcp_client, agent
    
    try:
        logger.info("🚀 Starting Agentic RAG with MCP Servers...")
        
        # Initialize components
        vector_db = VectorDatabase()
        memory_manager = MemoryManager(gemini_api_key=Config.GEMINI_API_KEY)
        
        # Setup knowledge base
        setup_knowledge_base(vector_db)
        
        # Start MCP server
        mcp_server = MCPServer(vector_db, memory_manager)
        server_thread = mcp_server.start_server()
        
        # Wait for server to start
        time.sleep(2)
        
        # Initialize MCP client and agent
        mcp_client = MCPClient()
        agent = AgenticRAG(mcp_client)
        
        logger.info("✅ System initialized successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ System initialization failed: {e}")
        return False

# Routes
@app.route('/')
def index():
    """Main chat interface"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/admin')
def admin():
    """Admin interface for system management"""
    return render_template('admin.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat API endpoint"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        user_id = session.get('user_id', 'default_user')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        if not agent:
            return jsonify({'error': 'System not initialized'}), 500
        
        # Process the query
        response = agent.process_query(user_message, user_id)
        
        return jsonify({
            'response': response,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def status():
    """System status endpoint"""
    return jsonify({
        'status': 'healthy' if agent else 'initializing',
        'components': {
            'vector_db': vector_db is not None,
            'memory_manager': memory_manager is not None,
            'mcp_server': mcp_server is not None,
            'mcp_client': mcp_client is not None,
            'agent': agent is not None
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/knowledge', methods=['POST'])
def add_knowledge():
    """Add new knowledge to the system"""
    try:
        data = request.get_json()
        doc_id = data.get('id') or str(uuid.uuid4())
        content = data.get('content', '')
        metadata = data.get('metadata', {})
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        if not vector_db:
            return jsonify({'error': 'Vector database not initialized'}), 500
        
        vector_db.add_document(doc_id, content, metadata)
        
        return jsonify({
            'success': True,
            'doc_id': doc_id,
            'message': 'Knowledge added successfully'
        })
        
    except Exception as e:
        logger.error(f"Add knowledge error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search():
    """Search knowledge base"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        if not vector_db:
            return jsonify({'error': 'Vector database not initialized'}), 500
        
        results = vector_db.search(query, top_k)
        
        return jsonify({
            'results': results,
            'query': query,
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': str(e)}), 500


# Socket.IO events
@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('status', {'message': 'Connected to Agentic RAG system'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle real-time chat messages"""
    try:
        user_message = data.get('message', '').strip()
        user_id = session.get('user_id', request.sid)
        logger.info(f"Received message: {user_message} from user: {user_id}")

        if not user_message:
            logger.warning("No message provided by user.")
            emit('error', {'message': 'Message is required'}, to=request.sid)
            emit('typing', {'status': False}, to=request.sid)
            return

        if not agent:
            logger.error("Agent is not initialized!")
            emit('error', {'message': 'System not initialized'}, to=request.sid)
            emit('typing', {'status': False}, to=request.sid)
            return

        emit('typing', {'status': True}, to=request.sid)

        try:
            response = agent.process_query(user_message, user_id)
            logger.info(f"Agent response: {response}")
        except Exception as agent_exc:
            logger.error(f"Agent processing error: {agent_exc}")
            emit('error', {'message': f'Agent error: {agent_exc}'}, to=request.sid)
            emit('typing', {'status': False}, to=request.sid)
            return

        emit('chat_response', {
            'response': response,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }, to=request.sid)

        emit('typing', {'status': False}, to=request.sid)

    except Exception as e:
        logger.error(f"Socket chat error: {e}")
        emit('error', {'message': str(e)}, to=request.sid)
        emit('typing', {'status': False}, to=request.sid)


if __name__ == '__main__':
    print("Starting app.py ...")
    # Initialize system
    success = initialize_system()

    if success:
        # Run the Flask app with SocketIO on all interfaces, port 5003
        socketio.run(
            app,
            debug=True,
            host='0.0.0.0',
            port=5003
        )
    else:
        logger.error("❌ Failed to start application")
        sys.exit(1)