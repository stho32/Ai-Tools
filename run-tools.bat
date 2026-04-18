@echo off
setlocal EnableDelayedExpansion

echo.
echo ======================================
echo          AI-TOOLS LAUNCHER
echo ======================================
echo.

if "%1"=="" (
    echo Available tools:
    echo.
    echo   1. md-to-mp3           - Convert markdown to MP3
    echo   2. md-to-mp3-pro       - Advanced markdown to MP3 conversion
    echo   3. random-educator     - Random educational content reader
    echo   4. random-pdf-reader   - Random PDF reader
    echo   5. random-text-reader  - Random text reader
    echo   6. ebooks-chunks-to-mp3 - Convert eBook chunks to MP3
    echo   7. ebooks-text-to-chunks - Split eBooks into text chunks
    echo   8. daily-run           - Run daily tasks
    echo   9. cleanup             - Clean up temporary files
    echo.
    echo Usage: %0 ^<tool-name^> [arguments]
    echo Example: %0 md-to-mp3 "C:\Books\Input" "C:\Books\Output"
    echo.
    goto :end
)

set TOOL=%1
shift

REM Remove the first parameter and pass the rest
set ARGS=
:loop
if "%1"=="" goto :continue
set ARGS=!ARGS! %1
shift
goto :loop
:continue

if "%TOOL%"=="md-to-mp3" (
    echo Starting Markdown to MP3 conversion...
    uv run python md_to_mp3.py !ARGS!
) else if "%TOOL%"=="md-to-mp3-pro" (
    echo Starting Markdown to MP3 Pro conversion...
    uv run python md_to_mp3_pro\md_to_mp3_pro.py !ARGS!
) else if "%TOOL%"=="random-educator" (
    echo Starting Random Educator...
    uv run python random_educator.py !ARGS!
) else if "%TOOL%"=="random-pdf-reader" (
    echo Starting Random PDF Reader...
    uv run python random_pdf_reader.py !ARGS!
) else if "%TOOL%"=="random-text-reader" (
    echo Starting Random Text Reader...
    uv run python random_text_reader.py !ARGS!
) else if "%TOOL%"=="ebooks-chunks-to-mp3" (
    echo Starting EBooks Chunks to MP3...
    uv run python ebooks_chunks_to_mp3.py !ARGS!
) else if "%TOOL%"=="ebooks-text-to-chunks" (
    echo Starting EBooks Text to Chunks...
    uv run python ebooks_text_to_chunks.py !ARGS!
) else if "%TOOL%"=="daily-run" (
    echo Starting Daily Run...
    uv run python daily-run.py !ARGS!
) else if "%TOOL%"=="cleanup" (
    echo Starting Cleanup...
    uv run python cleanup.py !ARGS!
) else (
    echo Error: Unknown tool "%TOOL%"
    echo Run "%0" without arguments to see available tools.
    exit /b 1
)

:end
endlocal
