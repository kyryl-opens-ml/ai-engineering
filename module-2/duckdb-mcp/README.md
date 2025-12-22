# DuckDB MCP

This folder contains a small MCP server that exposes DuckDB via tools, plus an example agent client.

## Run the MCP server

From `module-2/`:

```bash
uv sync
uv run python duckdb-mcp/duckdb_mcp.py
```

The server is available at `http://127.0.0.1:8000/sse`.

## Run the example agent

From `module-2/`:

```bash
export OPENAI_API_KEY=...
uv run python duckdb-mcp/duckdb_agent.py
```

Example prompts:

- Show me the tables
- What is the schema for the users table?
- Show me all users
