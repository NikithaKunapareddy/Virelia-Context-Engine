# Agentic RAG with MCP Servers

A sophisticated Retrieval-Augmented Generation (RAG) system that integrates with Model Context Protocol (MCP) servers for enhanced knowledge management and conversational AI capabilities.

## 🚀 Features

- **Agentic RAG System**: Intelligent retrieval and generation with context awareness
- **MCP Server Integration**: Full Model Context Protocol implementation
- **Vector Database**: FAISS-based semantic search and storage
- **Memory Management**: Short-term and long-term conversation memory
- **Real-time Chat Interface**: WebSocket-powered chat with typing indicators
- **Admin Dashboard**: System management and knowledge base administration
- **User Preferences**: Personalized experience with preference learning
- **Modern UI**: Responsive design with Bootstrap and custom styling

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask App     │    │  Agentic RAG    │
│   (HTML/JS)     │◄──►│   (app.py)      │◄──►│   System        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   MCP Server    │    │ Vector Database │
                       │   (REST API)    │    │   (FAISS)       │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Memory Manager  │    │   Gemini LLM    │
                       │   (Context)     │    │  (Generation)   │
                       └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- Google Gemini API Key
- Git (for cloning)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd agentic-rag-mcp
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env file with your API keys
   GEMINI_API_KEY=your_gemini_api_key_here
   SECRET_KEY=your_secret_key_here
   DEBUG=False
   ```

## 🚀 Quick Start

1. **Run the application**:
   ```bash
   python app.py
   ```

2. **Access the application**:
   - Main Chat Interface: http://localhost:5000
   - Admin Dashboard: http://localhost:5000/admin
   - MCP Server API: http://localhost:5001

3. **Start chatting**:
   - Open the main interface
   - Type your questions about AI, programming, or any topic
   - The system will retrieve relevant knowledge and provide contextual responses

## 💡 Usage Examples

### Basic Chat
```
You: What is machine learning?
Assistant: Machine learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed...
```

### Knowledge Search
```
You: Tell me about vector databases
Assistant: Vector databases are specialized databases designed to store and query high-dimensional vectors. They are essential for AI applications like similarity search...
```

### Follow-up Questions
```
You: Can you give me an example?
Assistant: [Based on conversation context] Sure! For vector databases, a common example would be...
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `SECRET_KEY` | Flask secret key | Auto-generated |
| `DEBUG` | Enable debug mode | `False` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `5000` |
| `MCP_SERVER_PORT` | MCP server port | `5001` |

### Advanced Configuration

Edit `config.py` to modify:
- Memory limits
- Embedding models
- Database settings
- MCP server configuration

## 📚 API Reference

### REST API Endpoints

#### Chat API
```
POST /api/chat
Content-Type: application/json

{
  "message": "Your question here"
}
```

#### Knowledge Management
```
POST /api/knowledge
Content-Type: application/json

{
  "content": "Document content",
  "metadata": {"topic": "AI"}
}
```

#### Search API
```
POST /api/search
Content-Type: application/json

{
  "query": "search terms",
  "top_k": 5
}
```

### WebSocket Events

- `connect`: Client connection
- `chat_message`: Send chat message
- `chat_response`: Receive AI response
- `typing`: Typing indicator
- `error`: Error messages

### MCP Server API

The MCP server provides these methods:

- `search`: Search knowledge base
- `memory_store`: Store conversation memory
- `memory_search`: Search conversation history
- `get_preferences`: Get user preferences
- `add_document`: Add knowledge document
- `delete_document`: Remove knowledge document
- `get_stats`: System statistics

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_vector_db.py

# Run with coverage
python -m pytest tests/ --cov=src/
```

## 📁 Project Structure

```
agentic-rag-mcp/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── src/                   # Source code modules
│   ├── vector_db.py       # Vector database implementation
│   ├── memory_manager.py  # Memory management
│   ├── mcp_server.py      # MCP server implementation
│   ├── mcp_client.py      # MCP client implementation
│   ├── agentic_rag.py     # Main RAG system
│   └── utils.py           # Utility functions
├── templates/             # HTML templates
├── static/                # CSS, JS, images
├── tests/                 # Unit tests
└── docs/                  # Documentation
```

## 🔒 Security

- Environment variables for sensitive data
- Input sanitization and validation
- CORS protection
- Session management
- Rate limiting (recommended for production)

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions, issues, or contributions:

1. Check the documentation
2. Search existing issues
3. Create a new issue
4. Join our community discussions

## 🔄 Changelog

### v1.0.0 (Current)
- Initial release
- Basic RAG functionality
- MCP server integration
- Web interface
- Memory management
- Vector database support

## 🗺️ Roadmap

- [ ] Plugin system for custom MCP servers
- [ ] Multi-modal support (images, documents)
- [ ] Advanced analytics dashboard
- [ ] API authentication
- [ ] Distributed deployment support
- [ ] Integration with external knowledge sources
