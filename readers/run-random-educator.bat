@echo off
cd /d "%~dp0"
echo Starting Random Educator with uv...
uv run python random_educator.py %*
