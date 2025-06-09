# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

This is an AI engineering interactive course repository with 8 self-contained modules covering the ML production pipeline:

- `module-1/` - Containerization and infrastructure basics
- `module-2/` - Data management and labeling  
- `module-3/` - Model training workflows
- `module-4/` - Pipeline orchestration
- `module-5/` - Serving with FastAPI
- `module-6/` - Large model optimization and load testing
- `module-7/` - Monitoring and observability
- `module-8/` - ML system design

Each module has its own dependencies and can be worked on independently.

## Common Commands

### Code Quality
```bash
# Format code (project-wide)
ruff format

# Check code style (project-wide)  
ruff check

# Module-specific formatting
ruff format module_name/ tests/

# Module-specific linting
ruff check module_name/ tests/
```