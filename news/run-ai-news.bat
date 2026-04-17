@echo off
cd /d "%~dp0"
echo Starting AI News with uv...
uv run python ai-news.py --config ai-news-config.json %*
