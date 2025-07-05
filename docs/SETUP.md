# Setup Instructions

This guide will help you set up the Agentic RAG with MCP Servers project from scratch.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

1. **Python 3.8 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - Verify installation: `python --version`

2. **Git** (optional, for cloning)
   - Download from [git-scm.com](https://git-scm.com/)
   - Verify installation: `git --version`

3. **Google Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Keep it secure for later use

### System Requirements

- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: At least 2GB free space
- **Network**: Internet connection for downloading dependencies and API calls

## Installation Methods

### Method 1: Download and Extract (Recommended)

1. **Download the project files**
   - Save all files to a folder named `agentic-rag-mcp`

2. **Navigate to the project directory**
   ```bash
   cd agentic-rag-mcp
   ```

### Method 2: Clone from Repository

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agentic-rag-mcp
   ```

## Environment Setup

### 1. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Verification:**
Your command prompt should show `(venv)` at the beginning.

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed Flask-2.3.3 Flask-SocketIO-5.3.6 sentence-transformers-2.2.2 ...
```

### 3. Configure Environment Variables

1. **Copy the environment template:**
   ```bash
   copy .env.example .env    # Windows
   cp .env.example .env      # macOS/Linux
   ```

2. **Edit the .env file:**
   
   Open `.env` in a text editor and configure:
   
   ```env
   # Required: Your Google Gemini API Key
   GEMINI_API_KEY=your_actual_api_key_here
   
   # Required: Flask Secret Key (generate a random string)
   SECRET_KEY=your_secret_key_here_make_it_random_and_long
   
   # Optional: Development settings
   DEBUG=True
   HOST=127.0.0.1
   PORT=5000
   
   # Optional: MCP Server settings
   MCP_SERVER_PORT=5001
   ```

### 4. Generate Secret Key

**Generate a secure secret key:**

```python
# Run this in Python
import secrets
print(secrets.token_hex(32))
```

Copy the output and use it as your `SECRET_KEY` in the `.env` file.

## Initial Setup Verification

### 1. Test Python Environment

```bash
python -c "import flask, sentence_transformers, faiss; print('Dependencies OK')"
```

### 2. Test API Key

```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', 'OK' if os.getenv('GEMINI_API_KEY') else 'Missing')"
```

## Running the Application

### 1. Start the Application

```bash
python app.py
```

**Expected output:**
```
2024-01-01 12:00:00,000 - __main__ - INFO - 🚀 Starting Agentic RAG with MCP Servers...
2024-01-01 12:00:00,000 - __main__ - INFO - ✅ System initialized successfully!
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://[::1]:5000
```

### 2. Access the Application

Open your web browser and navigate to:

- **Main Chat Interface**: http://localhost:5000
- **Admin Dashboard**: http://localhost:5000/admin
- **API Status**: http://localhost:5000/api/status

## First Steps

### 1. Test the Chat Interface

1. Go to http://localhost:5000
2. Type a message: "What is artificial intelligence?"
3. Press Enter or click Send
4. You should receive an AI-generated response

### 2. Explore the Admin Dashboard

1. Go to http://localhost:5000/admin
2. Check system status
3. Try adding knowledge to the database
4. Test the search functionality

### 3. Test API Endpoints

```bash
# Test chat API
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'

# Test status API
curl http://localhost:5000/api/status
```

## Common Issues and Solutions

### Issue 1: "ModuleNotFoundError"

**Problem:** Missing Python packages

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue 2: "GEMINI_API_KEY not found"

**Problem:** Missing or incorrect API key

**Solution:**
1. Check your `.env` file exists
2. Verify the API key is correctly set
3. Ensure no extra spaces or quotes

### Issue 3: "Port already in use"

**Problem:** Port 5000 is occupied

**Solution:**
```bash
# Option 1: Change port in .env file
PORT=5001

# Option 2: Kill existing process
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F

# macOS/Linux:
lsof -ti:5000 | xargs kill -9
```

### Issue 4: "Permission denied"

**Problem:** Virtual environment or file permissions

**Solution:**
```bash
# Windows: Run as Administrator
# macOS/Linux: Check file permissions
chmod +x app.py
```

### Issue 5: "Vector database initialization failed"

**Problem:** FAISS installation issues

**Solution:**
```bash
# Reinstall FAISS
pip uninstall faiss-cpu
pip install faiss-cpu

# Or try alternative:
pip install faiss-gpu  # If you have GPU
```

## Advanced Setup

### Development Mode

For development, enable debug mode:

```env
DEBUG=True
```

This enables:
- Auto-reload on code changes
- Detailed error messages
- Debug toolbar

### Production Setup

For production deployment:

1. **Set production environment:**
   ```env
   DEBUG=False
   SECRET_KEY=strong_random_secret_key
   ```

2. **Use production server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Set up reverse proxy (Nginx example):**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Docker Setup (Optional)

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   EXPOSE 5000
   
   CMD ["python", "app.py"]
   ```

2. **Build and run:**
   ```bash
   docker build -t agentic-rag .
   docker run -p 5000:5000 --env-file .env agentic-rag
   ```

## Testing the Installation

### Run Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src/
```

### Load Testing

```bash
# Install locust for load testing
pip install locust

# Create locustfile.py and run
locust -f tests/load_test.py --host=http://localhost:5000
```

## Monitoring and Logs

### Enable Logging

Add to your `.env` file:
```env
LOG_LEVEL=INFO
LOG_FILE=app.log
```

### Monitor System Resources

```bash
# Monitor Python processes
ps aux | grep python

# Monitor ports
netstat -tlnp | grep :5000

# Monitor logs
tail -f app.log
```

## Backup and Maintenance

### Backup Knowledge Base

The vector database is stored in memory by default. For persistence:

1. **Implement database backup:**
   ```python
   # Add to your maintenance script
   import pickle
   
   # Save vector database
   with open('backup_vectordb.pkl', 'wb') as f:
       pickle.dump(vector_db, f)
   ```

2. **Schedule regular backups:**
   ```bash
   # Linux/macOS crontab
   0 2 * * * /path/to/backup_script.sh
   ```

### Update Dependencies

```bash
# Check for updates
pip list --outdated

# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade flask
```

## Security Considerations

### 1. API Key Security

- Never commit API keys to version control
- Use environment variables
- Rotate keys regularly
- Monitor API usage

### 2. Network Security

- Use HTTPS in production
- Implement rate limiting
- Add authentication for admin endpoints
- Use firewall rules

### 3. Input Validation

The system includes basic input validation, but consider:
- Adding more strict validation
- Implementing content filtering
- Monitoring for abuse

## Getting Help

### Documentation

- **API Reference**: `docs/API.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **Code Documentation**: Check docstrings in source files

### Community Support

1. Check existing issues in the repository
2. Create a new issue with:
   - Detailed description
   - Steps to reproduce
   - System information
   - Error logs

### Development

To contribute or modify the system:

1. Fork the repository
2. Create a development branch
3. Make changes with tests
4. Submit a pull request

## Next Steps

Once your setup is complete:

1. **Customize the knowledge base** - Add your own documents
2. **Modify the UI** - Update templates and styles
3. **Extend functionality** - Add new MCP methods
4. **Deploy to production** - Use proper hosting and monitoring
5. **Integrate with other systems** - Connect to your existing tools

Congratulations! Your Agentic RAG system is now ready to use.
