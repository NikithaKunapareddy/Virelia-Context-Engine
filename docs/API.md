# API Documentation

## Overview

The Agentic RAG system provides multiple API interfaces for different types of interactions:

1. **REST API** - Standard HTTP endpoints for web applications (Port 5000)
2. **WebSocket API** - Real-time communication for chat interfaces (Port 5000)
3. **MCP Server API** - Model Context Protocol server for agent interactions (Port 5001)

## Service Ports

- **Main Flask Application**: `http://localhost:5000`
  - Web interface, REST API, WebSocket connections
  - **Access the chat interface**: Open `http://localhost:5000` in your browser
- **MCP Server**: `http://localhost:5001`
  - Model Context Protocol server for agent communications
  - **Not for direct browser access** - used by agents and programmatic clients

## Authentication

Currently, the system uses session-based authentication. Each user session is assigned a unique user ID for memory and preference management.

Future versions will include:
- API key authentication
- OAuth integration
- Role-based access control

## REST API

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### 1. Chat Endpoint

Send a message to the AI assistant.

**Endpoint:** `POST /api/chat`

**Request:**
```json
{
  "message": "What is machine learning?"
}
```

**Response:**
```json
{
  "response": "Machine learning is a subset of artificial intelligence...",
  "user_id": "user_uuid",
  "timestamp": "2024-01-01T12:00:00"
}
```

**Status Codes:**
- `200 OK` - Successful response
- `400 Bad Request` - Missing or invalid message
- `500 Internal Server Error` - System error

#### 2. Knowledge Management

Add new knowledge to the system.

**Endpoint:** `POST /api/knowledge`

**Request:**
```json
{
  "id": "doc_123",
  "content": "Vector databases are specialized databases...",
  "metadata": {
    "topic": "databases",
    "source": "manual_input",
    "date": "2024-01-01"
  }
}
```

**Response:**
```json
{
  "success": true,
  "doc_id": "doc_123",
  "message": "Knowledge added successfully"
}
```

#### 3. Search Knowledge Base

Search the knowledge base for relevant information.

**Endpoint:** `POST /api/search`

**Request:**
```json
{
  "query": "vector databases",
  "top_k": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "doc_123",
      "content": "Vector databases are specialized databases...",
      "metadata": {
        "topic": "databases"
      },
      "similarity_score": 0.85
    }
  ],
  "query": "vector databases",
  "count": 1
}
```

#### 4. System Status

Check the health and status of system components.

**Endpoint:** `GET /api/status`

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "vector_db": true,
    "memory_manager": true,
    "mcp_server": true,
    "mcp_client": true,
    "agent": true
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

## WebSocket API

### Connection

Connect to the WebSocket server:

```javascript
const socket = io('http://localhost:5000');
```

### Events

#### Client to Server Events

**chat_message**
```javascript
socket.emit('chat_message', {
  message: "What is artificial intelligence?"
});
```

#### Server to Client Events

**connect**
```javascript
socket.on('connect', () => {
  console.log('Connected to server');
});
```

**chat_response**
```javascript
socket.on('chat_response', (data) => {
  console.log('AI Response:', data.response);
  // data: { response, user_id, timestamp }
});
```

**typing**
```javascript
socket.on('typing', (data) => {
  console.log('Typing status:', data.status);
  // data: { status: true/false }
});
```

**error**
```javascript
socket.on('error', (data) => {
  console.error('Error:', data.message);
  // data: { message }
});
```

**disconnect**
```javascript
socket.on('disconnect', () => {
  console.log('Disconnected from server');
});
```

## MCP Server API

### Base URL
```
http://localhost:5001
```

### Protocol

The MCP server follows the Model Context Protocol specification.

### Request Format

```json
{
  "id": "request_id",
  "method": "method_name",
  "params": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

### Response Format

```json
{
  "id": "request_id",
  "result": {
    "data": "response_data"
  },
  "error": null
}
```

### Methods

#### 1. search

Search the knowledge base.

**Request:**
```json
{
  "id": "1",
  "method": "search",
  "params": {
    "query": "machine learning",
    "top_k": 5
  }
}
```

**Response:**
```json
{
  "id": "1",
  "result": {
    "results": [
      {
        "id": "doc1",
        "content": "Machine learning is...",
        "metadata": {},
        "similarity_score": 0.9
      }
    ]
  }
}
```

#### 2. memory_store

Store conversation data in memory.

**Request:**
```json
{
  "id": "2",
  "method": "memory_store",
  "params": {
    "user_id": "user123",
    "data": {
      "role": "user",
      "content": "Hello",
      "timestamp": "2024-01-01T12:00:00"
    }
  }
}
```

#### 3. memory_search

Search conversation memory.

**Request:**
```json
{
  "id": "3",
  "method": "memory_search",
  "params": {
    "user_id": "user123",
    "query": "previous conversation",
    "limit": 10
  }
}
```

#### 4. get_preferences

Get user preferences.

**Request:**
```json
{
  "id": "4",
  "method": "get_preferences",
  "params": {
    "user_id": "user123"
  }
}
```

#### 5. add_document

Add a document to the knowledge base.

**Request:**
```json
{
  "id": "5",
  "method": "add_document",
  "params": {
    "doc_id": "new_doc",
    "content": "Document content here",
    "metadata": {
      "topic": "AI"
    }
  }
}
```

#### 6. delete_document

Delete a document from the knowledge base.

**Request:**
```json
{
  "id": "6",
  "method": "delete_document",
  "params": {
    "doc_id": "doc_to_delete"
  }
}
```

#### 7. get_stats

Get system statistics.

**Request:**
```json
{
  "id": "7",
  "method": "get_stats",
  "params": {}
}
```

### Capabilities Endpoint

Get server capabilities:

**Endpoint:** `GET /capabilities`

**Response:**
```json
{
  "methods": [
    {
      "name": "search",
      "description": "Search the knowledge base",
      "params": {
        "query": "string",
        "top_k": "number"
      }
    }
  ]
}
```

### Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy"
}
```

## Error Handling

### HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Error Response Format

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "additional": "information"
  }
}
```

## Rate Limiting

Current rate limits (per user):
- Chat messages: 60 per minute
- Knowledge additions: 10 per minute
- Search requests: 100 per minute

## SDK Examples

### Python SDK Example

```python
import requests
import json

class AgenticRAGClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def chat(self, message):
        response = self.session.post(
            f"{self.base_url}/api/chat",
            json={"message": message}
        )
        return response.json()
    
    def search(self, query, top_k=5):
        response = self.session.post(
            f"{self.base_url}/api/search",
            json={"query": query, "top_k": top_k}
        )
        return response.json()

# Usage
client = AgenticRAGClient()
result = client.chat("What is AI?")
print(result["response"])
```

### JavaScript SDK Example

```javascript
class AgenticRAGClient {
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl;
    }
    
    async chat(message) {
        const response = await fetch(`${this.baseUrl}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });
        return response.json();
    }
    
    async search(query, topK = 5) {
        const response = await fetch(`${this.baseUrl}/api/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query, top_k: topK }),
        });
        return response.json();
    }
}

// Usage
const client = new AgenticRAGClient();
client.chat("What is machine learning?")
    .then(result => console.log(result.response));
```

## Testing the API

### Using curl

```bash
# Test chat endpoint
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is AI?"}'

# Test search endpoint
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "top_k": 3}'

# Test status endpoint
curl http://localhost:5000/api/status
```

### Using Postman

1. Import the API collection
2. Set the base URL to `http://localhost:5000`
3. Test each endpoint with sample data

## Webhooks (Future Feature)

The system will support webhooks for real-time notifications:

```json
{
  "webhook_url": "https://your-app.com/webhook",
  "events": ["chat_message", "knowledge_added"],
  "secret": "webhook_secret"
}
```
