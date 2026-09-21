# CTF Agent - Running Guide

## ✅ System Status

All core components have been successfully built and tested:

- **Configuration**: ✅ Working (OpenAI API key configured)
- **Flag Detection**: ✅ Working (all patterns tested)
- **Tool Security**: ✅ Working (unauthorized URLs/paths blocked)
- **Agent State**: ✅ Working (state management functional)
- **Knowledge Base**: ✅ Working (schemas and data models functional)
- **API Routes**: ⚠️  May hang on first load due to ML model downloads

## 🚀 How to Run the System

### Option 1: Start API Server (Recommended)

```bash
# Start the API server (may take 30-60 seconds on first run due to ML model downloads)
python -m app.main

# Or using the CLI
ctf-agent server
```

Once running, access:
- **Web UI**: http://localhost:5000
- **API Docs**: http://localhost:5000/docs
- **Health Check**: http://localhost:5000/health

### Option 2: Run Agent Directly

```bash
# Run agent against a target (requires target to be running)
python -c "
import sys
sys.path.append('.')
from app.agent.controller import AgentController
controller = AgentController(
    challenge_id='demo-web',
    challenge_description='Simple web login challenge with SQL injection',
    target_url='http://localhost:8000'
)
result = controller.run()
print(result)
"
```

### Option 3: Use Individual Components

```bash
# Test flag detection
python -c "import sys; sys.path.append('.'); from app.flags.detector import FlagDetector; print(FlagDetector().detect('CTF{test}'))"

# Test tool security
python -c "import sys; sys.path.append('.'); from app.tools.http import HTTPTool; print(HTTPTool().execute({'method': 'GET', 'url': 'http://evil.com'}))"
```

## 🐳 Running the Demo Challenge

### Prerequisites
- Docker Desktop must be installed and running
- Port 8000 must be available

### Start the Challenge

```bash
cd docker/demo-challenge
docker compose up -d
```

Verify it's running:
```bash
curl http://localhost:8000
```

### Stop the Challenge

```bash
cd docker/demo-challenge
docker compose down
```

## 📚 Knowledge Base Setup

### Ingest Writeups

```bash
# This may take time on first run due to ML model downloads
python -m app.knowledge.ingest ./data/writeups

# Or using CLI
ctf-agent ingest ./data/writeups
```

### Search Knowledge Base

```bash
python -m app.knowledge.search "SQL injection"

# Or using CLI
ctf-agent search "SQL injection"
```

## 🧪 Testing

### Run Component Tests

```bash
python test_components.py
```

### Run Unit Tests

```bash
pytest tests/
```

### Run with Coverage

```bash
pytest --cov=app tests/
```

## 📊 Evaluation Benchmark

```bash
python scripts/evaluate.py
```

This will run the agent against defined challenges and generate performance metrics.

## 🔧 Troubleshooting

### API Server Hangs on Startup
- **Cause**: ML model downloads from HuggingFace (sentence-transformers)
- **Solution**: Wait for initial download to complete (30-60 seconds)
- **Alternative**: Use individual components directly without loading the full API

### Import Errors
- **Cause**: Python path issues
- **Solution**: Always use `sys.path.append('.')` when running direct Python scripts
- **Alternative**: Use the installed package: `ctf-agent <command>`

### Docker Not Available
- **Cause**: Docker Desktop not running or not installed
- **Solution**: Install Docker Desktop and start it
- **Alternative**: Use web challenges that don't require Docker

### OpenAI API Errors
- **Cause**: Invalid API key or quota issues
- **Solution**: Verify API key in `.env` file
- **Check**: https://platform.openai.com/api-keys

### Memory Issues
- **Cause**: Large ML models and embeddings
- **Solution**: Close other applications, increase system RAM
- **Alternative**: Use smaller embedding models

## 📝 Example Workflow

### Complete End-to-End Test

1. **Start the demo challenge** (if Docker is available):
   ```bash
   cd docker/demo-challenge
   docker compose up -d
   ```

2. **Ingest knowledge base** (one-time setup):
   ```bash
   python -m app.knowledge.ingest ./data/writeups
   ```

3. **Start the API server**:
   ```bash
   python -m app.main
   ```

4. **Use the web UI**:
   - Open http://localhost:5000
   - Enter challenge details
   - Start the agent
   - Monitor progress in real-time

5. **Review results**:
   - Check the trajectory logs
   - View discovered flags
   - Analyze agent decisions

## 🎯 Next Steps

1. **Configure Environment**: Ensure `.env` has your OpenAI API key
2. **Start Demo Challenge**: Launch the Docker container if available
3. **Test Components**: Run `python test_components.py`
4. **Start API Server**: Run `python -m app.main`
5. **Use Web UI**: Open http://localhost:5000

## 📞 Support

If you encounter issues:
1. Check the main README.md for architecture details
2. Review AGENTS.md for project-specific decisions
3. Run component tests to isolate the issue
4. Check error messages for specific guidance

---

**System Status**: ✅ Core components functional, ready for deployment
**API Key**: ✅ Configured
**Dependencies**: ✅ Installed
**Tests**: ✅ Passing
