# Projektstruktur

Dieses Projekt ist ein Python-Projekt zur Verarbeitung, Analyse und Konvertierung von Text-, Nachrichten- und Audioinhalten. Die Tools sind nach Themenbereich in eigene Oberverzeichnisse aufgeteilt.

## Hauptverzeichnis

- **.git/**: Git-Versionskontrolle für das Projekt.
- **.gitignore**: Definiert Dateien/Ordner, die von Git ignoriert werden.
- **Ai-Documents/**: Enthält Projektdokumentation.
    - **coding-style.md**: Richtlinien zum Programmierstil.
    - **structure.md**: Beschreibung der Projektstruktur.
- **Anforderungen/**: Anforderungsdokumente.
- **README.md**: Einstiegspunkt mit Hinweisen zur Nutzung.
- **CLAUDE.md**: Projekt-Instruktionen für Claude Code.
- **requirements.txt / pyproject.toml**: Python-Abhängigkeiten (uv).
- **daily-run.py**: Orchestrator-Skript (News-Scrape + PDF-Reader-Loop).
- **run.bat / run-daily.bat / run-tools.bat / setup.bat**: Windows-Launcher.

## Themenbereiche

### `news/` - Nachrichtenanalyse

- **ai-news.py**: Scrape-Skript für Nachrichtenquellen mit HTML-Report und KI-Analyse.
    - **Funktionen:**
        - `main()`: Einstiegspunkt, lädt Konfiguration, verarbeitet Quellen, generiert HTML-Report.
        - `process_source(source)`: Verarbeitet eine Nachrichtenquelle.
        - `generate_html_report(results, timestamp)`: Erstellt HTML-Report.
- **ai-news-deep.py**: Deep-Crawler, analysiert Unterseiten je Domain.
    - **Funktionen:**
        - `main()`: Hauptfunktion, verarbeitet Quellen, erstellt HTML-Report.
        - `process_source_deep(source, max_pages)`: Durchsucht und analysiert Unterseiten.
        - `generate_html_report(results, timestamp)`: Erstellt HTML-Report für Deep Crawl.
- **ai-news-config.example.json**: Beispiel-Konfigurationsdatei mit Quellen und Kategorien.
- **run-ai-news.bat / run-ai-news-deep.bat**: Windows-Launcher.
- **lib/news_utils.py**: HTTP-Fetch, HTML-Clean, Diff, LLM-Call (OpenAI/Anthropic).
    - **Funktionen:**
        - `get_website_content(url)`, `clean_html(html_content)`
        - `get_content_diff(previous, current)`, `load_previous_content(url)`, `save_current_content(url, content)`
        - `call_gpt(system_message, user_message)`, `get_gpt4_analysis(content, url, keywords, category)`
        - `load_config(config_path=None)`

### `audiobooks/` - Markdown / eBook zu MP3

- **md_to_mp3.py**: Konvertiert Markdown-Dateien in MP3 (OpenAI TTS, asyncio).
- **ebooks_text_to_chunks.py**: Zerlegt eBooks in Text-Chunks.
- **ebooks_chunks_to_mp3.py**: Wandelt Text-Chunks in MP3-Dateien um.
- **README.md / REQUIREMENTS.md / REQUIREMENTS_pro.md**: Doku zu den Audiobook-Tools.
- **run-md-to-mp3.bat / run-md-to-mp3-pro.bat / run-ebooks-\*.bat**: Windows-Launcher.
- **lib/text_split.py**: Zerlegt Texte in Chunks nach Zeichen/Wörtern/Sätzen.
- **lib/audio_tools.py**: `chunk_to_speech(text)` via OpenAI TTS.

### `readers/` - Zufällige PDF/Text-Reader mit TTS

- **random_pdf_reader.py**: Liest zufällige Seiten eines zufälligen PDFs vor.
- **random_educator.py**: Wählt zufällig PDF oder Textdatei, bereitet Inhalt per GPT auf und gibt ihn als Audio aus.
- **random_text_reader.py**: Liest zufällige Seiten einer Textdatei vor.
- **cleanup.py**: Entfernt `.txt`- und `.mp3`-Dateien im aktuellen Verzeichnis.
- **run-random-\*.bat / run-cleanup.bat**: Windows-Launcher.
- **lib/pdf_audio_tools.py**: PDF-Extraktion, `call_gpt`, `text_to_speech`, `play_audio`.

---

**Hinweis:**
- Trennung nach Themenbereich (News, Audiobooks, Readers) in je eigenem Oberverzeichnis.
- Jeder Bereich hat sein eigenes `lib/`-Unterverzeichnis.
- Daily-Orchestrator und Master-Launcher liegen weiterhin im Wurzelverzeichnis.
