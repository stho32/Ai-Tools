# AI-Tools - Text Processing and Audio Conversion Tools

This project contains various tools for processing text, converting documents to audio, and analyzing news sources using AI.

## Requirements

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver

## Installation

1. Install uv if you haven't already:
   ```bash
   pip install uv
   ```

2. Clone this repository and navigate to the directory:
   ```bash
   cd C:\Projekte\Ai-Tools
   ```

3. Install dependencies (uv will create and manage a virtual environment automatically):
   ```bash
   uv sync
   ```

## Usage

### Quick Start

Use the master launcher to see all available tools:
```cmd
run-tools.bat
```

### Available Tools

#### 1. AI News Analysis
```cmd
run-tools.bat ai-news
run-tools.bat ai-news-deep
```

#### 2. Markdown to MP3 Conversion
```cmd
run-tools.bat md-to-mp3 "C:\Books\Input" "C:\Books\Output"
run-tools.bat md-to-mp3-pro "C:\Books\Input" "C:\Books\Output"
```

#### 3. Random Content Readers
```cmd
run-tools.bat random-educator
run-tools.bat random-pdf-reader
run-tools.bat random-text-reader
```

#### 4. EBook Processing
```cmd
run-tools.bat ebooks-text-to-chunks "C:\Books\input.txt" "C:\Books\chunks\"
run-tools.bat ebooks-chunks-to-mp3 "C:\Books\chunks\"
```

#### 5. Utility Tools
```cmd
run-tools.bat daily-run
run-tools.bat cleanup
```

### Individual Scripts

You can also run individual tools directly:
```cmd
run-ai-news.bat
run-md-to-mp3.bat "C:\Books\Input" "C:\Books\Output"
run-random-educator.bat
```

### Direct uv Usage

For more control, you can use uv directly:
```cmd
uv run python ai-news.py --config ai-news-config.json
uv run python md_to_mp3.py "C:\Books\Input" "C:\Books\Output"
```

## Benefits of uv

- **Automatic Environment Management**: uv creates and manages virtual environments automatically
- **Fast Dependency Resolution**: Much faster than pip for installing packages
- **Reliable Dependencies**: Ensures consistent package versions across runs
- **No Manual Environment Setup**: No need to manually create or activate virtual environments
