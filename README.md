# AI-Tools - Text Processing and Audio Conversion Tools

This project contains various tools for processing text, converting documents to audio, and analyzing news sources using AI.

Tools are grouped by topic into top-level folders:

- **`news/`** - Daily news scraper with HTML report
- **`audiobooks/`** - Markdown / eBook to MP3 pipelines
- **`readers/`** - Random PDF / text readers with TTS

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

Use the master launcher (prints all available tools):
```cmd
run-tools.bat
```

### News (`news/`)

```cmd
run-tools.bat ai-news
run-tools.bat ai-news-deep
```

Config lives in `news/ai-news-config.json` (see `news/ai-news-config.example.json`).
The state for diff-based updates is kept in `news/.ai-news-status/`.

### Audiobooks (`audiobooks/`)

```cmd
run-tools.bat md-to-mp3 "C:\Books\Input" "C:\Books\Output"
run-tools.bat md-to-mp3-pro "C:\Books\Input" "C:\Books\Output"
run-tools.bat ebooks-text-to-chunks "C:\Books\input.txt" "C:\Books\chunks\"
run-tools.bat ebooks-chunks-to-mp3 "C:\Books\chunks\"
```

### Readers (`readers/`)

```cmd
run-tools.bat random-educator
run-tools.bat random-pdf-reader
run-tools.bat random-text-reader
run-tools.bat cleanup
```

### Daily run

```cmd
run-tools.bat daily-run
REM or directly
run-daily.bat
```

### Individual Scripts

You can also run individual tools directly via the per-area batch files:
```cmd
news\run-ai-news.bat
audiobooks\run-md-to-mp3.bat "C:\Books\Input" "C:\Books\Output"
readers\run-random-educator.bat
```

### Direct uv Usage

For more control, you can use uv directly from inside a tool directory:
```cmd
cd news
uv run python ai-news.py --config ai-news-config.json

cd audiobooks
uv run python md_to_mp3.py "C:\Books\Input" "C:\Books\Output"
```

## Benefits of uv

- **Automatic Environment Management**: uv creates and manages virtual environments automatically
- **Fast Dependency Resolution**: Much faster than pip for installing packages
- **Reliable Dependencies**: Ensures consistent package versions across runs
- **No Manual Environment Setup**: No need to manually create or activate virtual environments
