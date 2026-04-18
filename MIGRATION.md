# Migration zu uv

Diese Anleitung hilft beim Übergang von der alten manuellen Python-Umgebung zur neuen uv-basierten Verwaltung.

## Was hat sich geändert?

1. **Dependency Management**: Statt `requirements.txt` verwenden wir jetzt `pyproject.toml`
2. **Virtual Environment**: uv verwaltet das Virtual Environment automatisch
3. **Ausführung**: Neue Batch-Skripte verwenden `uv run` statt direktes `python`

## Migration Steps

### 1. Setup der neuen Struktur

```cmd
# Führe das Setup-Skript aus
setup.bat
```

### 2. Alte Virtual Environments entfernen (optional)

Falls Sie vorher manuelle Virtual Environments verwendet haben:

```cmd
# Alte venv oder conda environments können gelöscht werden
# da uv diese automatisch verwaltet
```

### 3. Neue Ausführungsmethoden verwenden

**Alt:**
```cmd
python md_to_mp3.py "C:\Books\Input" "C:\Books\Output"
```

**Neu:**
```cmd
run-tools.bat md-to-mp3 "C:\Books\Input" "C:\Books\Output"
# oder
run-md-to-mp3.bat "C:\Books\Input" "C:\Books\Output"
# oder
uv run python md_to_mp3.py "C:\Books\Input" "C:\Books\Output"
```

## Vorteile der neuen Struktur

- ✅ **Automatisches Environment Management**: Keine manuellen venv-Operationen
- ✅ **Schnellere Installation**: uv ist deutlich schneller als pip
- ✅ **Einheitliche Toolchain**: Alle Tools verwenden dieselbe Verwaltung
- ✅ **Reproduzierbare Builds**: Lockfile sorgt für konsistente Abhängigkeiten
- ✅ **Einfachere Nutzung**: Ein Kommando für alle Tools

## Troubleshooting

### uv Command nicht gefunden
```cmd
pip install uv
```

### Dependencies nicht installiert
```cmd
uv sync
```

### Alte Python-Pfade in Skripten
Die neuen Batch-Skripte verwenden `uv run`, alte direkte Python-Aufrufe sollten ersetzt werden.

## Kompatibilität

Die Python-Skripte selbst sind unverändert geblieben. Nur die Art der Ausführung hat sich geändert.
