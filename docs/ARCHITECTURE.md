# Architecture Overview

## System Architecture

The Agentic RAG with MCP Servers is designed as a modular, scalable system that combines retrieval-augmented generation with the Model Context Protocol for enhanced AI interactions.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Web UI    │  │  Admin UI   │  │  REST API   │              │
│  │ (templates) │  │ (templates) │  │ (endpoints) │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   Flask App       │
                    │   (app.py)        │
                    │   - Routing       │
                    │   - Session Mgmt  │
                    │   - WebSocket     │
                    └─────────┬─────────┘
                              │
┌─────────────────────────────▼─────────────────────────────────────┐
│                      Core Business Logic                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Agentic RAG │  │  MCP Client │  │ MCP Server  │              │
│  │   System    │  │             │  │             │              │
│  │ - Query     │  │ - Protocol  │  │ - Methods   │              │
│  │   Processing│  │   Handler   │  │ - Endpoints │              │
│  │ - Response  │  │ - Requests  │  │ - Routing   │              │
│  │   Generation│  │             │  │             │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────────────┐
│                        Data Layer                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Vector DB   │  │ Memory Mgr  │  │ Gemini LLM  │              │
│  │ (FAISS)     │  │             │  │             │              │
│  │ - Embeddings│  │ - Short-term│  │ - Generation│              │
│  │ - Similarity│  │ - Long-term │  │ - Analysis  │              │
│  │ - Storage   │  │ - Prefs     │  │             │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend Layer

#### Web Interface (`templates/`)
- **Purpose**: User-facing chat interface
- **Technology**: HTML5, Bootstrap 5, JavaScript
- **Features**:
  - Real-time chat with WebSocket
  - Responsive design
  - Typing indicators
  - Message history

#### Admin Interface (`templates/admin.html`)
- **Purpose**: System management and monitoring
- **Features**:
  - Knowledge base management
  - System status monitoring
  - Search functionality
  - Statistics dashboard

#### REST API (`app.py`)
- **Purpose**: HTTP-based API for external integrations
- **Endpoints**:
  - `/api/chat` - Send messages
  - `/api/knowledge` - Manage knowledge
  - `/api/search` - Search functionality
  - `/api/status` - System health

### 2. Application Layer

#### Flask Application (`app.py`)
- **Purpose**: Main application server
- **Responsibilities**:
  - Request routing
  - Session management
  - WebSocket handling
  - Component orchestration
- **Key Features**:
  - Auto-initialization
  - Error handling
  - Logging
  - CORS support

### 3. Business Logic Layer

#### Agentic RAG System (`src/agentic_rag.py`)

```python
class AgenticRAG:
    """Main orchestrator for RAG operations"""
    
    def process_query(self, query, user_id):
        # 1. Store user message
        # 2. Retrieve context (knowledge + memory)
        # 3. Generate response
        # 4. Store response
        # 5. Return to user
```

**Core Workflow:**
1. **Input Processing**: Sanitize and analyze user input
2. **Context Retrieval**: Search knowledge base and memory
3. **Response Generation**: Use LLM with retrieved context
4. **Memory Storage**: Store conversation for future reference
5. **Response Delivery**: Return formatted response

#### MCP Client (`src/mcp_client.py`)

```python
class MCPClient:
    """Client for communicating with MCP servers"""
    
    def make_request(self, method, params):
        # Format MCP request
        # Send to MCP server
        # Handle response
        # Return results
```

**Features:**
- Protocol-compliant requests
- Error handling and retry logic
- Connection pooling
- Async operations support

#### MCP Server (`src/mcp_server.py`)

```python
class MCPServer:
    """MCP protocol server implementation"""
    
    def process_request(self, request):
        # Route to appropriate handler
        # Execute operation
        # Format response
        # Return results
```

**Supported Methods:**
- `search` - Knowledge base search
- `memory_store` - Store conversation data
- `memory_search` - Search conversation history
- `get_preferences` - Retrieve user preferences
- `add_document` - Add knowledge document
- `delete_document` - Remove document
- `get_stats` - System statistics

### 4. Data Layer

#### Vector Database (`src/vector_db.py`)

```python
class VectorDatabase:
    """FAISS-based vector storage and search"""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer()
        self.index = None  # FAISS index
        self.documents = {}  # Document storage
```

**Architecture:**
- **Embedding Model**: SentenceTransformers for text vectorization
- **Index**: FAISS for efficient similarity search
- **Storage**: In-memory document storage with metadata
- **Operations**: Add, search, update, delete documents

**Search Process:**
1. Convert query to embedding
2. Search FAISS index for similar vectors
3. Return ranked results with similarity scores

#### Memory Manager (`src/memory_manager.py`)

```python
class MemoryManager:
    """Manages conversation memory and user preferences"""
    
    def __init__(self):
        self.short_term_memory = {}  # Recent conversations
        self.long_term_memory = VectorDatabase()  # Persistent memory
        self.user_preferences = {}  # User-specific data
```

**Memory Types:**
- **Short-term**: Recent conversation context (sliding window)
- **Long-term**: Vectorized conversation history for semantic search
- **Preferences**: User-specific settings and learned preferences

**Memory Workflow:**
1. Store each message with timestamp and user ID
2. Extract user facts and preferences using LLM
3. Maintain conversation context within limits
4. Enable semantic search across conversation history

#### Gemini LLM Integration

```python
# Integration with Google Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
```

**Usage Patterns:**
- **Response Generation**: Main chat responses
- **Intent Analysis**: Understanding user goals
- **Fact Extraction**: Learning user preferences
- **Content Analysis**: Processing knowledge documents

## Data Flow

### 1. Chat Message Flow

```
User Input → Flask → AgenticRAG → MCP Client → MCP Server
    ↓              ↑                            ↓
Response ← UI ← Response ← LLM ← Context ← Memory/Vector DB
```

**Detailed Steps:**

1. **User sends message** via web interface or API
2. **Flask receives** and validates the request
3. **AgenticRAG processes** the query:
   - Stores user message in memory
   - Searches knowledge base for relevant documents
   - Retrieves conversation context and user preferences
   - Generates response using LLM with context
   - Stores assistant response in memory
4. **Response returned** to user interface

### 2. Knowledge Addition Flow

```
Admin Input → Flask API → MCP Server → Vector DB
                                        ↓
                              Document Processing
                                        ↓
                              Embedding Generation
                                        ↓
                              Index Update
```

### 3. Memory Processing Flow

```
Conversation → Memory Manager → Short-term Storage
                    ↓
             Fact Extraction (LLM)
                    ↓
             User Preferences Update
                    ↓
             Long-term Vectorization
```

## Scalability Considerations

### Current Architecture Limitations

1. **In-Memory Storage**: Vector database and memory stored in RAM
2. **Single Process**: All components run in one Python process
3. **No Persistence**: Data lost on restart
4. **Limited Concurrency**: Single-threaded processing

### Scaling Strategies

#### Horizontal Scaling

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Web Server  │  │ Web Server  │  │ Web Server  │
│  Instance   │  │  Instance   │  │  Instance   │
└─────────────┘  └─────────────┘  └─────────────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
              ┌─────────────┐
              │ Load        │
              │ Balancer    │
              └─────────────┘
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Redis     │  │ PostgreSQL  │  │  Vector DB  │
│  (Session)  │  │ (Metadata)  │  │ (Pinecone)  │
└─────────────┘  └─────────────┘  └─────────────┘
```

#### Microservices Architecture

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│    Web      │  │   Memory    │  │   Vector    │
│   Service   │  │  Service    │  │  Service    │
└─────────────┘  └─────────────┘  └─────────────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
              ┌─────────────┐
              │  Message    │
              │    Bus      │
              │ (RabbitMQ)  │
              └─────────────┘
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│    LLM      │  │   Search    │  │    MCP      │
│  Service    │  │  Service    │  │  Service    │
└─────────────┘  └─────────────┘  └─────────────┘
```

## Security Architecture

### Current Security Measures

1. **Input Sanitization**: Basic validation and cleaning
2. **Session Management**: Flask sessions with secure tokens
3. **Environment Variables**: Sensitive data in environment
4. **CORS Protection**: Controlled cross-origin requests

### Enhanced Security (Future)

```
┌─────────────────────────────────────────────────────────────────┐
│                      Security Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │     WAF     │  │   Auth      │  │ Rate Limit  │              │
│  │             │  │ (OAuth2)    │  │             │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────────────┐
│                    Application Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Input Val.  │  │ Encryption  │  │   Audit     │              │
│  │             │  │ (at rest)   │  │  Logging    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Performance Optimization

### Current Performance Characteristics

- **Response Time**: 1-3 seconds for typical queries
- **Concurrent Users**: 10-20 users (single process)
- **Memory Usage**: 500MB-2GB depending on knowledge base size
- **CPU Usage**: Moderate during embedding generation

### Optimization Strategies

#### 1. Caching Strategy

```python
# Response caching
@lru_cache(maxsize=1000)
def search_cache(query_hash):
    return vector_db.search(query)

# Embedding caching
embedding_cache = {}
def get_cached_embedding(text):
    if text not in embedding_cache:
        embedding_cache[text] = model.encode(text)
    return embedding_cache[text]
```

#### 2. Async Processing

```python
import asyncio
import aiohttp

class AsyncMCPClient:
    async def make_request(self, method, params):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                return await response.json()
```

#### 3. Database Optimization

```python
# Batch processing
def add_documents_batch(documents):
    embeddings = model.encode([doc.content for doc in documents])
    index.add(embeddings)
    
# Index optimization
def optimize_index():
    index.train(training_vectors)
    index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
```

## Monitoring and Observability

### Current Monitoring

- Basic logging to console/file
- System status endpoint
- Error tracking in responses

### Enhanced Monitoring (Future)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Monitoring Stack                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Prometheus  │  │   Grafana   │  │ ELK Stack   │              │
│  │ (Metrics)   │  │ (Dashboards)│  │   (Logs)    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Jaeger    │  │  AlertMgr   │  │  Health     │              │
│  │ (Tracing)   │  │ (Alerts)    │  │  Checks     │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### Key Metrics

- **Response times** per endpoint
- **Error rates** and types
- **Memory usage** trends
- **API usage** patterns
- **User engagement** metrics

## Deployment Architecture

### Development Environment

```
Developer Machine
├── Python Virtual Environment
├── Local Flask Server (Debug Mode)
├── In-Memory Vector Database
└── File-based Configuration
```

### Production Environment

```
┌─────────────────────────────────────────────────────────────────┐
│                     Production Stack                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Nginx     │  │  Gunicorn   │  │   Redis     │              │
│  │ (Reverse    │  │ (WSGI)      │  │ (Session)   │              │
│  │  Proxy)     │  │             │  │             │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ PostgreSQL  │  │  Pinecone   │  │  Docker     │              │
│  │ (Metadata)  │  │ (Vectors)   │  │ (Container) │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Future Architecture Enhancements

### 1. Plugin System

```python
class PluginManager:
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, name, plugin):
        self.plugins[name] = plugin
    
    def execute_plugin(self, name, *args, **kwargs):
        return self.plugins[name].execute(*args, **kwargs)
```

### 2. Multi-Modal Support

```python
class MultiModalProcessor:
    def process_input(self, input_data):
        if input_data.type == 'text':
            return self.process_text(input_data)
        elif input_data.type == 'image':
            return self.process_image(input_data)
        elif input_data.type == 'document':
            return self.process_document(input_data)
```

### 3. Distributed Vector Database

```python
class DistributedVectorDB:
    def __init__(self, nodes):
        self.nodes = nodes
        self.shard_strategy = ConsistentHashing()
    
    def search(self, query, top_k):
        # Distribute search across nodes
        # Merge and rank results
        pass
```

This architecture provides a solid foundation for building a scalable, maintainable, and extensible Agentic RAG system with MCP server integration.
