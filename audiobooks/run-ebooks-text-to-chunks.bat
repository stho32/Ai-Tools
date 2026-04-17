@echo off
cd /d "%~dp0"
echo Starting EBooks Text to Chunks with uv...
uv run python ebooks_text_to_chunks.py %*
