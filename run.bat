@echo off
cd /d "%~dp0\news"
uv run python ai-news.py --config ai-news-config.json
