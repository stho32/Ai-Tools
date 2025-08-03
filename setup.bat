@echo off
echo.
echo ======================================
echo       AI-TOOLS SETUP
echo ======================================
echo.

echo Checking if uv is installed...
uv --version > nul 2>&1
if %errorlevel% neq 0 (
    echo uv is not installed. Installing uv...
    pip install uv
    if %errorlevel% neq 0 (
        echo Failed to install uv. Please install it manually: pip install uv
        pause
        exit /b 1
    )
) else (
    echo uv is already installed.
)

echo.
echo Installing project dependencies...
uv sync

if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo ======================================
echo    Setup completed successfully!
echo ======================================
echo.
echo You can now run tools using:
echo   run-tools.bat [tool-name]
echo.
echo For a list of available tools, run:
echo   run-tools.bat
echo.
pause
