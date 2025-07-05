import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the application"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Server settings
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # API Keys
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyDIYb_DLRxnoO430zXgeTqUm1t9sOgJQv8')
    
    # MCP Settings
    MCP_SERVER_PORT = int(os.environ.get('MCP_SERVER_PORT', 5001))
    
    # Database settings
    EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    VECTOR_DB_PATH = os.environ.get('VECTOR_DB_PATH', 'knowledge_base.index')
    
    # Memory settings
    SHORT_TERM_MEMORY_LIMIT = int(os.environ.get('SHORT_TERM_MEMORY_LIMIT', 20))
    LONG_TERM_MEMORY_LIMIT = int(os.environ.get('LONG_TERM_MEMORY_LIMIT', 100))
