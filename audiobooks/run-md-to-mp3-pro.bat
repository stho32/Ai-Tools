@echo off
cd /d "%~dp0"
echo Starting MD to MP3 Pro with uv...
if "%~2"=="" (
    echo Usage: %0 ^<input_path^> ^<output_path^> [options]
    echo Example: %0 "C:\Books\MyBook" "C:\Output"
    exit /b 1
)
uv run python md_to_mp3_pro\md_to_mp3_pro.py %*
