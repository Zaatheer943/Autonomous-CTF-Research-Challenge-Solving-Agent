# CTF Agent - Project Information

## Project-Specific Configuration

### Build and Verification Commands

**Install the project:**
```bash
pip install -e .
```

**Run tests:**
```bash
pytest
```

**Run specific test:**
```bash
pytest tests/test_flag_detector.py
```

**Run with coverage:**
```bash
pytest --cov=app tests/
```

**Start demo challenge:**
```bash
cd docker/demo-challenge
docker-compose up -d
```

**Ingest knowledge base:**
```bash
ctf-agent ingest ./data/writeups
```

**Run agent against demo:**
```bash
ctf-agent solve --challenge demo-web --target http://localhost:8000
```

**Start API server:**
```bash
ctf-agent server
```

**Run evaluation benchmark:**
```bash
python scripts/evaluate.py
```

### Key Design Decisions

1. **Import System**: Added `sys.path.append` to all modules to handle import issues in the MVP structure. This is a workaround for the current project layout and should be refactored in production.

2. **Sandbox Implementation**: Used a hybrid approach for terminal execution - tries Docker first, falls back to subprocess with safety checks. This ensures compatibility while maintaining security.

3. **Knowledge Base**: ChromaDB with sentence-transformers for embeddings. Chose for simplicity and local operation.

4. **LLM Abstraction**: Implemented provider pattern to support multiple LLM providers. Currently only OpenAI is implemented.

5. **Trajectory Storage**: JSON files for simplicity. Should be replaced with database in production.

6. **API State**: In-memory storage for MVP. Should use database for production.

### Dependencies

**Core:**
- fastapi, uvicorn - Web framework
- pydantic, pydantic-settings - Data validation
- chromadb - Vector database
- sentence-transformers - Embeddings
- openai - LLM API
- httpx - HTTP client
- playwright - Browser automation
- docker - Container management
- click - CLI framework

**Development:**
- pytest - Testing
- pytest-asyncio - Async testing
- pytest-cov - Coverage
- black - Code formatting
- ruff - Linting
- mypy - Type checking

### Environment Variables

Essential variables in `.env`:
- `OPENAI_API_KEY` - Required for LLM functionality
- `CTF_TARGET_HOST` - Default target host
- `CTF_TARGET_PORT` - Default target port
- `ALLOWED_NETWORKS` - Comma-separated list of allowed networks
- `MAX_AGENT_STEPS` - Maximum steps before timeout
- `FLAG_PATTERNS` - Regex patterns for flag detection

### File Structure Notes

- `app/` - Main application code
- `data/` - Runtime data (writeups, trajectories, chroma db)
- `docker/` - Challenge containers
- `tests/` - Test files
- `scripts/` - Utility scripts

### Demo Challenge Details

**Location:** `docker/demo-challenge/`

**Technology:** Flask web application

**Vulnerability:** SQL injection in login form

**Flag:** `CTF{demo_sql_injection_flag_12345}`

**Expected Solution:** Agent should discover the login form, recognize SQL injection potential, test with `' OR '1'='1` payload, bypass authentication, and retrieve the flag.

### Testing Strategy

**Unit Tests:**
- Flag detection patterns
- Tool security (URL validation, path restrictions)
- Knowledge retrieval (basic functionality)

**Integration Tests:**
- Agent controller with mocked LLM
- Tool executor with actual tools
- API endpoints

**End-to-End Tests:**
- Full agent run against demo challenge
- Knowledge ingestion and retrieval
- Trajectory logging and retrieval

### Known Issues

1. **Import Path**: Current workaround with `sys.path.append` should be replaced with proper package structure.

2. **Browser Tool**: Playwright requires browser installation - may fail on first run without setup.

3. **Docker Dependency**: Terminal tool requires Docker for full sandboxing - falls back to subprocess with limitations.

4. **Memory Storage**: In-memory API state doesn't persist across restarts.

5. **Error Handling**: Some error conditions could be more granular.

### Performance Considerations

- Embedding generation can be slow for large writeup collections
- LLM API calls add latency to each step
- Vector search is fast but depends on collection size
- Browser automation is resource-intensive

### Security Notes

- All tools validate targets against `ALLOWED_NETWORKS`
- Terminal tool blocks dangerous commands
- File tool restricts access to safe directories
- No credential exposure in logs
- No persistence mechanisms

### Extension Points

**Adding New Tools:**
1. Inherit from `BaseTool` in `app/tools/base.py`
2. Implement `get_schema()` and `execute()` methods
3. Register in `ToolExecutor`

**Adding New Challenges:**
1. Create Docker container in `docker/`
2. Add to `scripts/evaluate.py` benchmark
3. Create corresponding writeups in `data/writeups/`

**Adding LLM Providers:**
1. Inherit from `LLMProvider` in `app/agent/llm.py`
2. Implement `generate()` and `generate_with_tools()`
3. Add provider selection logic in `get_llm_provider()`

**Enhancing Knowledge Base:**
1. Add writeups in Markdown format with frontmatter
2. Run `ctf-agent ingest` to update vector database
3. Categories and tags help with retrieval
