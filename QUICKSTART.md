# Quick Start Guide

## ✅ Installation Complete!

The CTF Agent has been successfully installed and configured.

## ✅ Current Status

- **OpenAI API Key**: ✅ Configured
- **Core Components**: ✅ All tested and working
- **Dependencies**: ✅ Installed
- **Configuration**: ✅ Ready

## 🧪 Component Tests Passed

All core components have been tested successfully:
- ✅ Configuration loading
- ✅ Flag detection (all patterns)
- ✅ Tool security (URL/path validation)
- ✅ Agent state management
- ✅ Knowledge base schemas

Run `python test_components.py` to verify.

## 🚀 Quick Start

### Option 1: Start API Server

```bash
python -m app.main
```

Then open http://localhost:5000 for the web UI.

### Option 2: Test Individual Components

```bash
# Test flag detection
python -c "import sys; sys.path.append('.'); from app.flags.detector import FlagDetector; print(FlagDetector().detect('CTF{test}'))"

# Test tool security
python -c "import sys; sys.path.append('.'); from app.tools.http import HTTPTool; print(HTTPTool().execute({'method': 'GET', 'url': 'http://evil.com'}))"
```

### Option 3: Run Agent Directly

```bash
python -c "
import sys
sys.path.append('.')
from app.agent.controller import AgentController
controller = AgentController('demo-web', 'Test challenge', 'http://localhost:8000')
result = controller.run()
print(result)
"
```

## 🐳 Demo Challenge (Requires Docker)

If you have Docker available:

```bash
cd docker/demo-challenge
docker compose up -d
```

Then run the agent against it.

## 📚 Knowledge Base

```bash
# Ingest writeups (may take time on first run)
python -m app.knowledge.ingest ./data/writeups

# Search knowledge base
python -m app.knowledge.search "SQL injection"
```

## ⚠️ Known Issues

1. **API Server Loading**: May hang for 30-60 seconds on first run due to ML model downloads
2. **CLI**: May have similar issues due to model loading
3. **Docker**: Not available in current environment

## 📖 Documentation

- **RUNNING_GUIDE.md**: Detailed running instructions
- **README.md**: Complete documentation
- **AGENTS.md**: Project-specific decisions

## 🔧 Troubleshooting

### API server hangs
- Wait for ML model downloads to complete (first run only)
- Use individual components directly as shown above

### Import errors
- Always use `sys.path.append('.')` pattern for direct Python scripts
- Or use the installed CLI: `ctf-agent <command>`

### Docker not available
- The system works without Docker for web-based challenges
- Install Docker Desktop for the full demo experience
