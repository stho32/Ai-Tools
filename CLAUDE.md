# CLAUDE.md

## Projektbeschreibung

Sammlung von AI-Tools zur Textverarbeitung, Nachrichtenanalyse und Audio-Konvertierung.
Die Tools nutzen OpenAI und Anthropic APIs fuer KI-gestuetzte Analyse und Text-to-Speech.

## TechStack

- Python (>=3.8)
- Paketverwaltung: uv (pyproject.toml)
- APIs: OpenAI, Anthropic
- Architektur-Vorlage: python-uv-app

## Projektstruktur

Die Tools sind nach Themenbereich in eigene Oberverzeichnisse aufgeteilt:

```
Ai-Tools/
  news/                 # Daily News Scraper + HTML-Report
    ai-news.py
    ai-news-deep.py
    ai-news-config.example.json
    run-ai-news.bat
    run-ai-news-deep.bat
    lib/news_utils.py   # HTTP-Fetch, HTML-Clean, Diff, LLM-Call

  audiobooks/           # Text -> MP3 Workflows
    md_to_mp3.py
    ebooks_text_to_chunks.py
    ebooks_chunks_to_mp3.py
    run-md-to-mp3.bat
    run-md-to-mp3-pro.bat
    run-ebooks-text-to-chunks.bat
    run-ebooks-chunks-to-mp3.bat
    lib/text_split.py
    lib/audio_tools.py  # chunk_to_speech (OpenAI TTS)

  readers/              # Random PDF/Text-Reader + TTS
    random_pdf_reader.py
    random_educator.py
    random_text_reader.py
    cleanup.py
    run-random-pdf-reader.bat
    run-random-educator.bat
    run-random-text-reader.bat
    run-cleanup.bat
    lib/pdf_audio_tools.py  # PDF-Extract, call_gpt, text_to_speech, play_audio

  daily-run.py          # Orchestrator: news + readers-Loop (bleibt im Root)
  run-daily.bat
  run-tools.bat         # Master-Launcher fuer alle Bereiche
  run.bat               # Shortcut fuer news/ai-news.py
  setup.bat

  Ai-Documents/         # Projektdokumentation (coding-style, structure)
  Anforderungen/        # Anforderungsdokumente
  pyproject.toml
```

## Befehle

### Setup

```bash
uv sync
```

### Scripts ausfuehren (direkt via uv)

```bash
# Nachrichtenanalyse
cd news && uv run python ai-news.py --config ai-news-config.json
cd news && uv run python ai-news-deep.py --config ai-news-config.json

# Markdown zu MP3
cd audiobooks && uv run python md_to_mp3.py <input-dir> <output-dir>

# E-Book-Verarbeitung
cd audiobooks && uv run python ebooks_text_to_chunks.py <input-file> <output-dir>
cd audiobooks && uv run python ebooks_chunks_to_mp3.py <chunks-dir>

# Zufallsbasierte Leser
cd readers && uv run python random_educator.py <pdf-dir> <text-dir> <num-pages>
cd readers && uv run python random_pdf_reader.py <directory> <num-pages>
cd readers && uv run python random_text_reader.py <text-dir> <num-pages>

# Bereinigung
cd readers && uv run python cleanup.py

# Taeglich (News + PDF-Loop)
uv run python daily-run.py
```

### Windows Batch-Dateien

```cmd
run-tools.bat                         # Master-Launcher mit Auswahl
run-daily.bat                         # Daily Run (News + PDF-Loop)

news\run-ai-news.bat                  # AI News
news\run-ai-news-deep.bat             # AI News Deep

audiobooks\run-md-to-mp3.bat          # Markdown zu MP3
audiobooks\run-ebooks-text-to-chunks.bat
audiobooks\run-ebooks-chunks-to-mp3.bat

readers\run-random-educator.bat       # Random Educator
readers\run-random-pdf-reader.bat     # Random PDF Reader
readers\run-random-text-reader.bat    # Random Text Reader
readers\run-cleanup.bat               # Cleanup
```

### Konfiguration und Status (news)

- Config: `news/ai-news-config.json` (siehe `news/ai-news-config.example.json`)
- State: `news/.ai-news-status/` (Diff-Tracking pro Quelle)
- HTML-Report: `news/<output_prefix>_<timestamp>.html`

## Konventionen

- **Shebang**: Jede Python-Datei beginnt mit `#!/usr/bin/env python3`
- **if __name__ Guard**: Ausfuehrbarer Code in `if __name__ == "__main__":` kapseln
- **Logging**: Zeitgestempelte Ausgaben mit eigener `log()`-Funktion oder `print()`
- **Namensgebung**: Englische, aussagekraeftige Namen fuer Variablen und Funktionen
- **Einrueckung**: 4 Leerzeichen
- **Fehlerbehandlung**: try-except-Bloecke fuer robuste Ausfuehrung
- **Dokumentation**: Docstrings fuer Funktionen und Klassen
