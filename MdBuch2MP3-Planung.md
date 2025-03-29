- Ich hätte gerne ein Python Script.

- Das Skript möge das neue text-to-speech von OpenAI nutzen:
https://platform.openai.com/docs/guides/text-to-speech

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

Ich möchte ein Skript haben, dass so ähnlich wie die ebook* Skripte funktioniert.

- Ich starte das Skript und gebe hierbei einen Pfad an, in dem sich eine Menge von MD-Dateien befinden.
- Des weiteren gebe ich einen Ausgabepfad an.
- Die Md-Dateien werden in einer Text-Datei zusammengefasst. Die Dateien werden entsprechend ihrer Reihenfolge im Dateisystem (sortiert nach Namen) zusammengefügt. Der Name der Datei ohne .md dient dabei als Überschrift, die immer zwischen den Inhalten eingefügt wird.
- Dann wird die Gesamtdatei in Abschnitte aufgeteilt, die durch die API verarbeitet werden können (es sollte sich vielleicht um Paragraphen oder Sätze handeln, die immer zusammen verarbeitet werden)
- Die Abschnitte werden in MP3s konvertiert
- Am Ende werden alle MP3s zusammengefasst. Die zusammengefasste MP3-Datei heißt wie der Md-Ordner, den ich angegeben habe. Also z.B. wenn C:\Projekte\Blabla\Pineapple der Pfad war, dann ist der Dateiname Pineapple.mp3 .
