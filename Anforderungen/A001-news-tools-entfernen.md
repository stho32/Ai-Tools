# A001 — News-Tools aus Repository entfernen

## Quelle

- GitHub Issue: [stho32/Ai-Tools#2 "Aufräumen und nachoptimieren"](https://github.com/stho32/Ai-Tools/issues/2)
- Klaerung im Dialog: Die News-Funktionalitaet wird nicht mehr in diesem Repo weiterentwickelt. Es gibt ein separates Repository ("News2"), das den News-Bereich uebernommen hat und inhaltlich weiter ist.

## Motivation

Die News-Tools (`ai-news.py`, `ai-news-deep.py`) sind in diesem Repository nicht mehr gepflegt. Ihre Weiterentwicklung findet im Nachfolge-Repo "News2" statt. Der tote Code erhoeht die Wartungslast, macht die Abhaengigkeiten (`requests`, `beautifulsoup4`) unnoetig schwer und verwirrt neue Entwickler ueber den Zweck des Projekts.

Die uebrigen Tools (`md_to_mp3`, `random_educator`, `random_pdf_reader`, `random_text_reader`, `ebooks_text_to_chunks`, `ebooks_chunks_to_mp3`, `daily-run`, `cleanup`) bleiben erhalten und aktiv.

## Umfang

### Zu entfernende Dateien

- `ai-news.py`
- `ai-news-deep.py`
- `ai-news-config.example.json`
- `run-ai-news.bat`
- `run-ai-news-deep.bat`
- `run.bat` (ruft ausschliesslich `ai-news.py` auf)

### Anzupassende Dateien

- `pyproject.toml` — `[project.scripts]`-Eintraege `ai-news` und `ai-news-deep` entfernen. Dependencies `beautifulsoup4` und `requests` entfernen (werden nur von News-Tools und News-Funktionen in `Lib/pdf_audio_tools.py` genutzt — siehe unten). **Zusaetzlich (Scope-Zuwachs, mit Benutzer abgestimmt):** `[project.scripts]` und `[build-system]` komplett entfernen und durch `[tool.uv] package = false` ersetzen. Begruendung: Setuptools erkannte `Lib/` und `Anforderungen/` als konkurrierende Top-Level-Packages (vorbestehender Bug, nur durch warmen Build-Cache verdeckt). Die Scripts wurden ohnehin nie ueber die `[project.scripts]`-Entrypoints aufgerufen, sondern immer via `.bat`-Wrapper oder `uv run python <script>.py` — der Entrypoint-Shim-Mechanismus ist fuer dieses Projekt unnoetig. Zudem war der Eintrag `daily-run = "daily-run:main"` ohnehin PEP-621-invalid (Bindestrich im Modulnamen).
- `daily-run.py` — Aufruf von `ai-news.py` (Zeilen 23-29) entfernen. Das Skript startet kuenftig direkt mit der `random_pdf_reader`-Schleife.
- `run-tools.bat` — Menue-Eintraege "1. ai-news" und "2. ai-news-deep" sowie die zugehoerigen `if`-Zweige entfernen. Nummerierung der verbleibenden Eintraege anpassen.
- `Lib/pdf_audio_tools.py` — News-spezifische Funktionen und deren Imports entfernen:
  - Funktionen: `get_website_content`, `clean_html`, `get_content_diff`, `load_previous_content`, `save_current_content`, `get_state_directory`, `get_state_filename`, `hash_content`, `get_gpt4_analysis`
  - Imports: `requests`, `BeautifulSoup` (aus `bs4`), `hashlib`
  - `load_config`: News-spezifische Default-Keys (`categories`, `news_sources`, `output_prefix`) und den Fallback auf `ai-news-config.example.json` entfernen. Die Funktion bleibt erhalten, damit `call_gpt` weiterhin `model_config` aus einer optionalen Konfigurationsdatei lesen kann — das ist nicht news-spezifisch.
- `README.md` — Alle News-Erwaehnungen (Zeilen 40-41, 73, 82 sowie ggf. umgebende Absaetze) entfernen.
- `MIGRATION.md` — News-Beispiele (Zeilen 33, 38, 40, 42) durch ein anderes Tool-Beispiel (z.B. `md_to_mp3.py` oder `random_pdf_reader.py`) ersetzen oder die betroffenen Abschnitte entfernen.
- `CLAUDE.md` — Projektbeschreibung, Projektstruktur-Kommentar und Script-/Batch-Tabellen um die News-Eintraege bereinigen.
- `Ai-Documents/structure.md` — Abschnitte ueber `ai-news.py`, `ai-news-deep.py` und `ai-news-config.example.json` entfernen.
- `.gitignore` — Eintraege `ai-news-config.json` und `.ai-news-status/` entfernen (werden nicht mehr benoetigt).

### Nicht betroffen

- Alle Tools ausser News bleiben unveraendert funktional.
- `Lib/text_split.py` bleibt unveraendert.
- `call_gpt` und `load_config` in `Lib/pdf_audio_tools.py` bleiben erhalten (werden von `random_*`-Tools genutzt).

## Akzeptanzkriterien

1. Nach der Aenderung existieren die oben gelisteten Dateien nicht mehr im Repository.
2. `uv sync` laeuft ohne Fehler durch.
3. `grep -r "ai-news" .` findet keine Treffer mehr (ausgenommen git-Metadaten und `Anforderungen/A001-*.md`).
4. `grep -r "ai_news" .` findet keine Treffer.
5. Alle verbleibenden Python-Skripte lassen sich ohne ImportError starten (mindestens `--help`-Aufruf bzw. Import-Smoke-Test):
   - `uv run python md_to_mp3.py --help`
   - `uv run python random_educator.py --help` (bzw. Import-Check falls kein `--help`)
   - `uv run python random_pdf_reader.py --help`
   - `uv run python random_text_reader.py --help`
   - `uv run python ebooks_text_to_chunks.py --help`
   - `uv run python ebooks_chunks_to_mp3.py --help`
   - `uv run python cleanup.py` (reines Import-Check)
   - `uv run python daily-run.py` (Import-Check — voller Lauf nicht sinnvoll)
6. `run-tools.bat` ohne Argumente zeigt eine konsistente Tool-Liste ohne News-Eintraege.
7. `pyproject.toml` enthaelt keine `ai-news`- oder `ai-news-deep`-Scripts mehr und keine `beautifulsoup4`/`requests`-Dependencies.
8. Die Dokumentation (`README.md`, `CLAUDE.md`, `MIGRATION.md`, `Ai-Documents/structure.md`) erwaehnt keine News-Tools mehr.

## Nicht-Ziele

- Es werden keine weiteren Refactorings an den verbleibenden Tools durchgefuehrt.
- Die Dependencies `anthropic` und `openai` bleiben erhalten (werden von `call_gpt` genutzt).
- Die git-Historie wird nicht umgeschrieben — die News-Tools bleiben ueber frueheren Commits auffindbar.
- Es findet keine Migration der Funktionalitaet ins News2-Repo statt (das Repo existiert bereits eigenstaendig).

## Tests/Verifikation

Da das Repository keine automatisierten Tests hat, erfolgt die Verifikation manuell:

- Strukturelle Pruefung via `grep` (Kriterien 3, 4).
- Import-Smoke-Tests fuer alle verbleibenden Skripte (Kriterium 5).
- `uv sync`-Durchlauf (Kriterium 2).
- Sichtpruefung des `run-tools.bat`-Menues (Kriterium 6).
- Sichtpruefung der `pyproject.toml` (Kriterium 7).
- Sichtpruefung der Dokumentation (Kriterium 8).

Ein richtiger End-to-End-Test der verbleibenden Tools (Audio-Ausgabe, PDF-Auswahl) ist durch den Benutzer vorgesehen (Phase 6 des Workflows).
