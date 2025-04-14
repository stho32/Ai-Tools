# Projektstruktur

Dieses Projekt ist ein umfangreiches Python-Projekt zur Verarbeitung, Analyse und Konvertierung von Text- und Markdown-Dateien in Audioformate (z.B. MP3). Die Struktur ist wie folgt aufgebaut:

## Hauptverzeichnis

- **.git/**: Git-Versionskontrolle für das Projekt.
- **.gitignore**: Definiert Dateien/Ordner, die von Git ignoriert werden.
- **Ai-Documents/**: Enthält Projektdokumentation.
    - **coding-style.md**: Richtlinien zum Programmierstil.
    - **structure.md**: Beschreibung der Projektstruktur.
- **Lib/**: Eigene Python-Bibliotheken für wiederverwendbare Funktionen.
    - **pdf_audio_tools.py**: Tools für PDF- und Audioverarbeitung, inkl. KI-Integration (OpenAI, Anthropic).
        - **Funktionen:**
            - `clean_html(html_content)`: Bereinigt HTML-Inhalte und extrahiert Klartext.
            - `get_gpt4_analysis(content, url, keywords, category)`: Führt KI-Analyse durch.
            - `load_config(config_path=None)`: Lädt Konfiguration.
            - `extract_text_from_pdf(pdf_path, start_page, num_pages)`: Extrahiert Text aus PDF.
            - `text_to_speech(text)`: Wandelt Text in Sprache um (OpenAI TTS).
            - `get_content_diff(previous_content, current_content)`: Vergleicht Inhalte.
            - `play_audio(audio_contents, output_filename)`: Spielt generierte Audiodateien ab.
            - `call_gpt(system_message, user_message)`: Ruft GPT-Modelle auf (OpenAI/Anthropic).
            - `get_website_content(url)`: Holt Website-Inhalte.
            - `chunk_to_speech(text)`: Wandelt Text-Abschnitt in Sprache um.
            - `get_random_pdf(directory)`: Wählt zufällige PDF aus Verzeichnis.
            - u.v.m.
    - **text_split.py**: Funktionen zum Zerlegen von Texten in Chunks nach Zeichen oder Wörtern.
        - **Funktionen:**
            - `read_text_file(file_path)`: Liest Textdatei ein.
            - `split_by_characters(text, max_chars)`: Teilt Text in Zeichen-Chunks.
            - `split_by_words(text, max_chunk_size)`: Teilt Text in Wort-Chunks.
            - `split_by_sentences(text, max_chunk_size)`: Teilt Text in Satz-Chunks.
            - `test()`: Testfunktion für Chunking.
- **README.md**: Einstiegspunkt mit Hinweisen zur Nutzung der wichtigsten Skripte.
- **requirements.txt**: Listet alle Python-Abhängigkeiten für das Projekt.
- **run.bat**: Windows-Batchdatei zum Starten von Skripten.

## Hauptskripte

- **ai-news.py**: Skript zur Analyse und Verarbeitung von Nachrichtenquellen. Nutzt KI für Inhaltsanalyse und -vergleich.
    - **Funktionen:**
        - `main()`: Einstiegspunkt, lädt Konfiguration, verarbeitet Quellen, generiert HTML-Report.
        - `process_source(source)`: Verarbeitet eine Nachrichtenquelle.
        - `generate_html_report(results, timestamp)`: Erstellt HTML-Report.
        - `get_gpt4_analysis(...)`: Führt GPT-Analyse durch.
- **ai-news-deep.py**: Erweiterte Version zur tieferen Analyse von Webseiten, nutzt verschiedene KI-Modelle und Funktionen aus `Lib/`.
    - **Funktionen:**
        - `main()`: Hauptfunktion, verarbeitet Quellen, erstellt HTML-Report.
        - `process_source_deep(source, max_pages)`: Durchsucht und analysiert Unterseiten.
        - `generate_html_report(results, timestamp)`: Erstellt HTML-Report für Deep Crawl.
- **ai-news-config.example.json**: Beispiel für eine Konfigurationsdatei mit Quellen und Einstellungen.
- **cleanup.py**: Hilfsskript zur Bereinigung von temporären Dateien oder Verzeichnissen.
- **daily-run.py**: Automatisiertes Skript für tägliche Aufgaben.
    - **Funktionen:**
        - `log(message)`: Zeitgestempelte Logausgabe.

## E-Book & Markdown zu Audio

- **ebooks_chunks_to_mp3.py**: Wandelt Text-Chunks aus E-Books in MP3-Dateien um.
- **ebooks_text_to_chunks.py**: Zerlegt E-Books in Text-Chunks.
- **md_to_mp3.py**: Konvertiert Markdown-Dateien direkt in MP3.
    - **Funktionen:**
        - `main()`: Hauptfunktion für die Konvertierung.
        - `parse_arguments()`: Argumentparser für Kommandozeile.
- **md_to_mp3_README.md**: Anleitung zur Nutzung von md_to_mp3.
- **md_to_mp3_REQUIREMENTS.md**: Zusätzliche Abhängigkeiten für md_to_mp3.

## Erweiterte Markdown-Konvertierung

- **md_to_mp3_pro/**: Erweiterte Version für die Markdown-zu-MP3-Konvertierung.
    - **md_to_mp3_pro.py**: Hauptskript mit Features wie Hashing, Resume-Funktion, Voice-Varianten, u.v.m.
        - **Funktionen:**
            - `main()`: Hauptfunktion.
            - `process_markdown_file(md_file, work_dir, client)`: Verarbeitet einzelne Markdown-Dateien asynchron.
    - **md_to_mp3_pro_README.md**: Anleitung für die Pro-Version.
    - **lib/**: Unterordner mit Modulen für die Pro-Version:
        - **audio.py**: Audioprozessierung und TTS.
            - `get_audio_duration(file_path)`: Gibt Audiodauer zurück.
            - `combine_audio_files(audio_files, output_file)`: Kombiniert mehrere MP3s.
        - **chunking.py**: Aufteilung von Texten in Abschnitte.
            - `split_text_into_chunks(text)`: Teilt Text in API-verarbeitbare Chunks.
            - `split_md_file_into_paragraphs(content)`: Teilt Markdown in Absätze.
        - **file_tracking.py**: Überwachung/Hashing von Dateien.
            - `identify_changed_files(input_dir, work_dir)`: Findet geänderte/neue Dateien.
            - `collect_markdown_files(directory)`: Sammelt alle Markdown-Dateien.
            - `update_file_status(work_dir, file_path, status)`: Aktualisiert Status.
            - `get_file_hash(file_path)`: Erzeugt SHA256-Hash.
            - `load_hash_memory(work_dir)`, `save_hash_memory(work_dir, hash_memory)`: Lädt/Speichert Hash-Memory.
        - **tts.py**: Text-to-Speech-Funktionalität (OpenAI, verschiedene Stimmen und Modelle).
            - `text_to_speech(client, text, output_file, model)`: Wandelt Text asynchron in Sprache um.
            - `process_chunks(chunks, work_dir, client, max_concurrent)`: Verarbeitet mehrere Chunks parallel.
        - **__pycache__/**: Python-Cache für Kompilate.
- **md_to_mp3_pro_REQUIREMENTS.md**: Anforderungen für die Pro-Version.

## Weitere Skripte

- **random_educator.py**: Generiert zufällige Lerninhalte.
    - **Funktionen:**
        - `random_educator(pdf_dir, text_dir, num_pages)`: Wählt zufällig PDF/Text, verarbeitet und liest vor.
        - `prepare_content_with_gpt4(text, source_info)`: Bereitet Text mit GPT-4 auf.
- **random_pdf_reader.py**: Liest zufällig ausgewählte PDFs.
    - **Funktionen:**
        - `random_pdf_reader(directory, num_pages, loop)`: Wählt und liest PDF, TTS-Ausgabe.
- **random_text_reader.py**: Liest zufällig ausgewählte Textdateien.
    - **Funktionen:**
        - `random_text_reader(text_dir, num_pages)`: Wählt und liest Textdatei, TTS-Ausgabe.

---

**Hinweis:**
- Die Struktur ermöglicht eine klare Trennung von Kernfunktionen, Hilfsmodulen, Dokumentation und Konfigurationsdateien.
- Die Hauptskripte sind direkt im Wurzelverzeichnis für schnellen Zugriff.
- Erweiterte/Pro-Funktionen sind in eigenen Unterordnern gekapselt.
- Eigene Bibliotheken liegen konsolidiert im `Lib/`-Verzeichnis.
- Die wichtigsten Funktionen der zentralen Module und Skripte sind dokumentiert.
