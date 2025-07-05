import logging
import os
import json
from typing import Dict, Any
from .vector_db import VectorDatabase

logger = logging.getLogger(__name__)

def setup_knowledge_base(vector_db: VectorDatabase):
    """Setup initial knowledge base with sample documents"""
    try:
        logger.info("Setting up knowledge base...")
        
        # Sample knowledge documents
        documents = [
            {
                "id": "ai_overview",
                "content": """
                Artificial Intelligence (AI) is a branch of computer science that aims to create 
                intelligent machines that can think and learn like humans. AI includes machine learning, 
                deep learning, neural networks, and natural language processing. Modern AI applications 
                include chatbots, recommendation systems, autonomous vehicles, and image recognition.
                """,
                "metadata": {"topic": "AI", "type": "overview"}
            },
            {
                "id": "machine_learning",
                "content": """
                Machine Learning (ML) is a subset of AI that enables computers to learn and improve 
                from experience without being explicitly programmed. There are three main types: 
                supervised learning (learning with labeled data), unsupervised learning (finding 
                patterns in unlabeled data), and reinforcement learning (learning through rewards 
                and penalties).
                """,
                "metadata": {"topic": "ML", "type": "educational"}
            },
            {
                "id": "rag_systems",
                "content": """
                Retrieval-Augmented Generation (RAG) is an AI technique that combines information 
                retrieval with text generation. RAG systems first retrieve relevant documents from 
                a knowledge base, then use this information to generate more accurate and contextual 
                responses. This approach helps reduce hallucinations and provides more factual answers.
                """,
                "metadata": {"topic": "RAG", "type": "technical"}
            },
            {
                "id": "vector_databases",
                "content": """
                Vector databases are specialized databases designed to store and query high-dimensional 
                vectors. They are essential for AI applications like similarity search, recommendation 
                systems, and RAG. Popular vector databases include Pinecone, Weaviate, Chroma, and 
                FAISS. They enable fast semantic search and similarity matching.
                """,
                "metadata": {"topic": "databases", "type": "technical"}
            },
            {
                "id": "python_programming",
                "content": """
                Python is a high-level, interpreted programming language known for its simplicity 
                and readability. It's widely used in AI, data science, web development, and automation. 
                Key features include dynamic typing, extensive libraries (NumPy, Pandas, TensorFlow), 
                and a strong community. Python's syntax makes it beginner-friendly while remaining 
                powerful for complex applications.
                """,
                "metadata": {"topic": "programming", "type": "overview"}
            },
            {
                "id": "web_development",
                "content": """
                Web development involves creating websites and web applications. It includes front-end 
                development (HTML, CSS, JavaScript) for user interfaces and back-end development 
                (Python, Node.js, databases) for server-side logic. Modern frameworks like React, 
                Vue.js, Flask, and Django make development more efficient and maintainable.
                """,
                "metadata": {"topic": "web-dev", "type": "overview"}
            }
        ]
        
        # Add documents to vector database
        for doc in documents:
            vector_db.add_document(
                doc["id"],
                doc["content"].strip(),
                doc["metadata"]
            )
        
        logger.info(f"✅ Added {len(documents)} documents to knowledge base")
        
    except Exception as e:
        logger.error(f"❌ Error setting up knowledge base: {e}")

def format_search_results(results: list) -> str:
    """Format search results for display"""
    if not results:
        return "No results found."
    
    formatted = []
    for i, result in enumerate(results, 1):
        content = result.get('content', '')[:200] + "..." if len(result.get('content', '')) > 200 else result.get('content', '')
        score = result.get('similarity_score', 0)
        topic = result.get('metadata', {}).get('topic', 'Unknown')
        
        formatted.append(f"{i}. [{topic}] {content} (Score: {score:.3f})")
    
    return "\n".join(formatted)

def validate_environment() -> Dict[str, Any]:
    """Validate the environment setup"""
    checks = {
        "python_version": True,  # If we're running, Python is available
        "required_packages": True,  # We'll assume imports work if we got this far
        "environment_variables": {
            "GEMINI_API_KEY": bool(os.environ.get('GEMINI_API_KEY')),
            "SECRET_KEY": bool(os.environ.get('SECRET_KEY'))
        }
    }
    
    return checks

def get_system_info() -> Dict[str, Any]:
    """Get system information for debugging"""
    import platform
    import sys
    
    return {
        "platform": platform.system(),
        "python_version": sys.version,
        "architecture": platform.architecture(),
        "processor": platform.processor()
    }

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove special characters that might cause issues
    text = text.replace('\x00', '')
    
    return text.strip()

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """Split text into overlapping chunks"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > start + chunk_size // 2:
                chunk = text[start:break_point + 1]
                end = break_point + 1
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return chunks

def safe_json_loads(json_str: str) -> Dict[str, Any]:
    """Safely load JSON with error handling"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return {}

def sanitize_user_input(user_input: str) -> str:
    """Sanitize user input for safety"""
    if not user_input:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '&', '"', "'", '\\', '/', '\x00']
    sanitized = user_input
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    # Limit length
    max_length = 1000
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()
