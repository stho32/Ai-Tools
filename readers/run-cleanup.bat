@echo off
cd /d "%~dp0"
echo Running cleanup with uv...
uv run python cleanup.py %*
