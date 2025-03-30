- Ich hätte gerne ein Python Script.

- Das Skript möge das neue text-to-speech von OpenAI nutzen:
https://platform.openai.com/docs/guides/text-to-speech
- Die Umgebungsvariable, aus der du den OPENAI-Key bekommst heisst "OPENAI_API_KEY"

```python
import asyncio

from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer

openai = AsyncOpenAI()

input = """Thank you for contacting us. I completely understand your frustration with the canceled flight, and I'm here to help you get rebooked quickly.\n\nI just need a few details from your original reservation, like your booking confirmation number or passenger info. Once I have those, I'll find the next available flight and make sure you reach your destination smoothly."""

instructions = """Voice Affect: Calm, composed, and reassuring; project quiet authority and confidence.\n\nTone: Sincere, empathetic, and gently authoritative—express genuine apology while conveying competence.\n\nPacing: Steady and moderate; unhurried enough to communicate care, yet efficient enough to demonstrate professionalism.\n\nEmotion: Genuine empathy and understanding; speak with warmth, especially during apologies (\"I'm very sorry for any disruption...\").\n\nPronunciation: Clear and precise, emphasizing key reassurances (\"smoothly,\" \"quickly,\" \"promptly\") to reinforce confidence.\n\nPauses: Brief pauses after offering assistance or requesting details, highlighting willingness to listen and support."""

async def main() -> None:

    async with openai.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=input,
        instructions=instructions,
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)

if __name__ == "__main__":
    asyncio.run(main())
```
- nutze diese neue gerade beschriebene Schnittstelle
- erstelle als Instructions 10 unterschiedliche Stimmen-Instructions
- die Voice soll bitte auch zufällig gewählt werden in jedem Paragraphen
- Die Stimmen-Instructions können ein buntes Spektrum abgeben, d.h. von frisch und energetisch bis zu Gruselgeschichte.
- Achtung: Bitte baue einen Fallback-Mechanismus ein. Er soll versuchen gpt-4o-mini-tts zu verwenden. Wenn das nicht klappt darf er auf ältere Modelle zurückfallen.

Struktur:
- Erstelle einen Ordner für das neue Skript
- Darin enthalten:
    md_to_mp3_pro.py    - das Hauptskript
    md_to_mp3_pro_README.md - die Nutzungsdokumentation 
    ./lib/              - Unterverzeichnis für Tool-Bibliotheken
        chunking.py
        tts.py
        ...

Die Anwendung soll so ähnlich wie md_to_mp3.py funktionieren.

- Ich starte das Skript und gebe hierbei einen Quell-Pfad an, in dem sich eine Menge von MD-Dateien befinden.
- Ich gebe einen weiteren Pfad, einen Arbeitspfad an. Hier können temporäre Dateien abgelegt werden. Die temporären Dateien bleiben bestehen. 
- Das Tool erstellt für jede md-Datei, die sie im Quell-Pfad einen Hash. Im Arbeitspfad legt es sich ein Gedächtnis an, in dem zu jeder md-Datei der letzte Hash steht (oder keiner, falls die Datei neu ist).
- Immer wenn sich gemerkter Hash und neuer Hash unterscheiden, wird der text-to-speech-Vorgang ausgeführt, der noch folgt.
- Jede *Bezeichnung*.md-Datei wird durch den Vorgang eine *Bezeichnung*.mp3-Datei erhalten.  
- Text-To-Speech-Vorgang für eine md-Datei:
    - Die *Bezeichnung*.md-Datei wird in Paragraphen aufgeteilt und in Abschnitten verarbeitet, die durch die TTS-API verarbeitet werden können 
    - Die Abschnitte werden in MP3s konvertiert unter Nutzung der TTS-API
    - Die Abschnitt-Dateien werden zusammengeführt und als *Bezeichnung*.mp3 gespeichert
    - Die Abschnitts-mp3 ersetzt eine ggf. bestehende Abschnitts-mp3 die schon neben der md-Datei liegt. Wenn es da noch keine gibt, dann ist sie neu, das ist ok. 

Ziel ist es, neben jeder md-Datei eine mp3-Fassung des md-Inhaltes zu haben. Ich werde die md-Dateien folgend immer mal hier oder mal da bearbeiten und das md_to_mp3_pro.py-Tool erneut ausführen. Hierbei wird das Tool alle Änderungen an md-Dateien erkennen und für die geänderten und neuen md-Dateien neue mp3s erzeugen.

- Für die temporären Audio-Dateien die du erstellst und ggf. Text Chunks FALLS du sie in Dateien speicherst, nutze gerne den Arbeitspfad als temporären Speicherort

- Stelle sicher, dass ich während des Vorgangs Fortschrittsmeldungen erhalte

Zum Testen kannst du folgende Angaben verwenden:
- Eingabeverzeichnis mit md-Dateien : C:\Projekte\Seminar-Prozess\Seminar-Prozess
- Arbeitspfad : C:\Projekte\Seminar-Prozess-Arbeitspfad

- Das Programm soll so konstruiert sein, dass es, wenn es im Lauf abstürzt oder unterbrochen wird, es im nächsten Lauf seine Arbeit wieder aufnimmt