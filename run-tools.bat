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
    echo   News:
    echo     ai-news                - Analyze news sources
    echo     ai-news-deep           - Deep analysis of news sources
    echo.
    echo   Audiobooks:
    echo     md-to-mp3              - Convert markdown to MP3
    echo     md-to-mp3-pro          - Advanced markdown to MP3 conversion
    echo     ebooks-chunks-to-mp3   - Convert eBook chunks to MP3
    echo     ebooks-text-to-chunks  - Split eBooks into text chunks
    echo.
    echo   Readers:
    echo     random-educator        - Random educational content reader
    echo     random-pdf-reader      - Random PDF reader
    echo     random-text-reader     - Random text reader
    echo     cleanup                - Clean up temporary files
    echo.
    echo   Misc:
    echo     daily-run              - Run daily tasks
    echo.
    echo Usage: %0 ^<tool-name^> [arguments]
    echo Example: %0 ai-news
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

if "%TOOL%"=="ai-news" (
    echo Starting AI News Analysis...
    pushd "%~dp0\news" && uv run python ai-news.py --config ai-news-config.json !ARGS! & popd
) else if "%TOOL%"=="ai-news-deep" (
    echo Starting AI News Deep Analysis...
    pushd "%~dp0\news" && uv run python ai-news-deep.py --config ai-news-config.json !ARGS! & popd
) else if "%TOOL%"=="md-to-mp3" (
    echo Starting Markdown to MP3 conversion...
    pushd "%~dp0\audiobooks" && uv run python md_to_mp3.py !ARGS! & popd
) else if "%TOOL%"=="md-to-mp3-pro" (
    echo Starting Markdown to MP3 Pro conversion...
    pushd "%~dp0\audiobooks" && uv run python md_to_mp3_pro\md_to_mp3_pro.py !ARGS! & popd
) else if "%TOOL%"=="random-educator" (
    echo Starting Random Educator...
    pushd "%~dp0\readers" && uv run python random_educator.py !ARGS! & popd
) else if "%TOOL%"=="random-pdf-reader" (
    echo Starting Random PDF Reader...
    pushd "%~dp0\readers" && uv run python random_pdf_reader.py !ARGS! & popd
) else if "%TOOL%"=="random-text-reader" (
    echo Starting Random Text Reader...
    pushd "%~dp0\readers" && uv run python random_text_reader.py !ARGS! & popd
) else if "%TOOL%"=="ebooks-chunks-to-mp3" (
    echo Starting EBooks Chunks to MP3...
    pushd "%~dp0\audiobooks" && uv run python ebooks_chunks_to_mp3.py !ARGS! & popd
) else if "%TOOL%"=="ebooks-text-to-chunks" (
    echo Starting EBooks Text to Chunks...
    pushd "%~dp0\audiobooks" && uv run python ebooks_text_to_chunks.py !ARGS! & popd
) else if "%TOOL%"=="daily-run" (
    echo Starting Daily Run...
    uv run python "%~dp0\daily-run.py" !ARGS!
) else if "%TOOL%"=="cleanup" (
    echo Starting Cleanup...
    pushd "%~dp0\readers" && uv run python cleanup.py !ARGS! & popd
) else (
    echo Error: Unknown tool "%TOOL%"
    echo Run "%0" without arguments to see available tools.
    exit /b 1
)

:end
endlocal
