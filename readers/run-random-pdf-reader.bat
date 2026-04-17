@echo off
cd /d "%~dp0"
echo Starting Random PDF Reader with uv...
uv run python random_pdf_reader.py %*
