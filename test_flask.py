#!/usr/bin/env python3
"""
Simple test to verify Flask app startup
"""
import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask

print("Testing Flask app creation...")

try:
    # Test basic Flask app
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return "Hello World! Flask is working!"
    
    print("✅ Flask app created successfully")
    print("Starting development server...")
    
    # Run the app
    app.run(host='127.0.0.1', port=5000, debug=True)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
