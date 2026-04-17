@echo off
cd /d "%~dp0"
echo Starting AI News Deep with uv...
uv run python ai-news-deep.py --config ai-news-config.json %*
