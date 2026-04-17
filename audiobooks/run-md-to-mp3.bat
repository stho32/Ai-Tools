@echo off
cd /d "%~dp0"
echo Starting MD to MP3 with uv...
if "%~2"=="" (
    echo Usage: %0 ^<input_path^> ^<output_path^> [--model MODEL]
    echo Example: %0 "C:\Books\MyBook" "C:\Output" --model gpt-4o-mini-tts
    exit /b 1
)
uv run python md_to_mp3.py %*
