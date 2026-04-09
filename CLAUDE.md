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

```
Ai-Tools/
  *.py              # Hauptskripte (ai-news, md_to_mp3, random_*, daily-run, cleanup)
  Lib/              # Wiederverwendbare Module (pdf_audio_tools, text_split)
  Ai-Documents/     # Projektdokumentation (coding-style, structure)
  Anforderungen/    # Anforderungsdokumente
  run-*.bat         # Windows-Startskripte
  run-tools.bat     # Master-Launcher fuer alle Tools
```

## Befehle

### Setup

```bash
uv sync
```

### Scripts ausfuehren

```bash
# Nachrichtenanalyse
uv run python ai-news.py --config ai-news-config.json
uv run python ai-news-deep.py --config ai-news-config.json

# Markdown zu MP3
uv run python md_to_mp3.py <input-dir> <output-dir>

# Zufallsbasierte Leser
uv run python random_educator.py <pdf-dir> <text-dir> <num-pages>
uv run python random_pdf_reader.py <directory> <num-pages>
uv run python random_text_reader.py <text-dir> <num-pages>

# E-Book-Verarbeitung
uv run python ebooks_text_to_chunks.py <input-file> <output-dir>
uv run python ebooks_chunks_to_mp3.py <chunks-dir>

# Taeglich
uv run python daily-run.py

# Bereinigung
uv run python cleanup.py
```

### Windows Batch-Dateien

```cmd
run-tools.bat              # Master-Launcher mit Auswahl
run-ai-news.bat            # AI News
run-ai-news-deep.bat       # AI News Deep
run-md-to-mp3.bat          # Markdown zu MP3
run-random-educator.bat    # Random Educator
run-random-pdf-reader.bat  # Random PDF Reader
run-random-text-reader.bat # Random Text Reader
run-daily.bat              # Daily Run
run-cleanup.bat            # Cleanup
```

## Konventionen

- **Shebang**: Jede Python-Datei beginnt mit `#!/usr/bin/env python3`
- **if __name__ Guard**: Ausfuehrbarer Code in `if __name__ == "__main__":` kapseln
- **Logging**: Zeitgestempelte Ausgaben mit eigener `log()`-Funktion oder `print()`
- **Namensgebung**: Englische, aussagekraeftige Namen fuer Variablen und Funktionen
- **Einrueckung**: 4 Leerzeichen
- **Fehlerbehandlung**: try-except-Bloecke fuer robuste Ausfuehrung
- **Dokumentation**: Docstrings fuer Funktionen und Klassen
