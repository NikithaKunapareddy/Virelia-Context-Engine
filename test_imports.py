#!/usr/bin/env python3
"""
Simple test script to verify all imports work correctly
"""

import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("Testing imports...")

try:
    print("✓ Testing basic imports...")
    import logging
    from datetime import datetime
    import uuid
    print("✓ Basic imports successful")

    print("✓ Testing Flask imports...")
    from flask import Flask, render_template, request, jsonify, session
    from flask_socketio import SocketIO, emit
    print("✓ Flask imports successful")

    print("✓ Testing configuration...")
    from config import Config
    print("✓ Configuration import successful")

    print("✓ Testing AI libraries...")
    import google.generativeai as genai
    from sentence_transformers import SentenceTransformer
    import faiss
    import numpy as np
    print("✓ AI libraries imports successful")

    print("✓ Testing project modules...")
    from src.vector_db import VectorDatabase
    from src.memory_manager import MemoryManager
    from src.mcp_server import MCPServer
    from src.mcp_client import MCPClient
    from src.agentic_rag import AgenticRAG
    from src.utils import setup_knowledge_base
    print("✓ Project modules imports successful")

    print("\n🎉 All imports successful! The application should work.")
    print("\nNow testing basic initialization...")

    # Test basic initialization
    app = Flask(__name__)
    app.config.from_object(Config)
    print("✓ Flask app created successfully")

    print("\n✅ Basic setup test completed successfully!")
    print("You can now run: python app.py")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install missing dependencies")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
