#!/usr/bin/env python3
import os
import random

from openai import OpenAI
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def chunk_to_speech(text):
    print("[DEBUG] Converting text to speech")
    try:
        voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        random_voice = random.choice(voices)
        print(f"[DEBUG] Selected voice: {random_voice}")
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice=random_voice,
            input=text
        )
        return response.content

    except Exception as e:
        print(f"[DEBUG] Error during text-to-speech conversion: {e}")

    return None
