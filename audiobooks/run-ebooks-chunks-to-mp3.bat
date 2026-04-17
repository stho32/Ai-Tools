@echo off
cd /d "%~dp0"
echo Starting EBooks Chunks to MP3 with uv...
uv run python ebooks_chunks_to_mp3.py %*
