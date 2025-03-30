#!/usr/bin/env python3
"""
tts.py - Module for text-to-speech conversion using OpenAI API
"""

import asyncio
import os
import random
from typing import List, Dict, Tuple
from openai import AsyncOpenAI

# Available voices in the OpenAI TTS API
VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer", "coral"]

# Instructions for different voice types
VOICE_INSTRUCTIONS = [
    # Energetic Instructor
    """Voice Affect: Energetic, enthusiastic, and motivational; project confidence and passion.
Tone: Inspirational and encouraging—express genuine excitement about the material and belief in the listener's ability to learn.
Pacing: Dynamic and engaging; vary speed to emphasize key points, with strategic pauses before important concepts.
Emotion: Genuine enthusiasm and positivity; speak with warmth and occasional excitement spikes when introducing breakthrough concepts.
Pronunciation: Clear and precise, with slight emphasis on technical terms to aid memorization.
Pauses: Strategic pauses after introducing complex ideas, creating moments for mental processing.""",
    
    # Academic Professor
    """Voice Affect: Calm, methodical, and analytical; project expertise and thoughtfulness.
Tone: Authoritative yet accessible—communicate complex ideas with clarity and precision.
Pacing: Steady and deliberate; take time with difficult concepts, ensuring thorough explanation.
Emotion: Measured intellectual curiosity; convey fascination with the subject matter in a controlled manner.
Pronunciation: Articulate and precise, with careful enunciation of technical terminology.
Pauses: Thoughtful pauses after explaining difficult concepts, allowing time for reflection.""",
    
    # Friendly Mentor
    """Voice Affect: Warm, conversational, and relatable; project friendliness and accessibility.
Tone: Collaborative and supportive—speak as if having a one-on-one conversation with a friend.
Pacing: Natural and comfortable; match the rhythm of everyday speech with occasional slowing for key insights.
Emotion: Genuine interest and care; speak with warmth and occasional humor to maintain engagement.
Pronunciation: Clear but casual, making technical concepts sound approachable and digestible.
Pauses: Natural conversational pauses, creating a rhythm that feels like dialogue rather than lecture.""",
    
    # Practical Coach
    """Voice Affect: Direct, practical, and efficient; project competence and experience.
Tone: No-nonsense but helpful—focus on delivering actionable knowledge without fluff.
Pacing: Brisk but clear; move efficiently through material while ensuring comprehension.
Emotion: Controlled enthusiasm for practical applications; emphasize utility and real-world relevance.
Pronunciation: Clear and straightforward, with emphasis on key action items and practical techniques.
Pauses: Brief, purposeful pauses before transitioning to new topics or summarizing important points.""",
    
    # Storyteller
    """Voice Affect: Storytelling, engaging, and vivid; project creativity and perspective.
Tone: Narrative and contextual—connect concepts to broader themes and real-world scenarios.
Pacing: Varied and dynamic; slow down for complex ideas, speed up for examples and illustrations.
Emotion: Rich emotional range; convey wonder, curiosity, and occasional drama to highlight importance.
Pronunciation: Expressive and colorful, with tonal variation to bring concepts to life.
Pauses: Dramatic pauses before key revelations or connections, creating narrative tension and resolution.""",
    
    # Mysterious Narrator
    """Voice Affect: Deep, intriguing, and slightly mysterious; project wisdom and ancient knowledge.
Tone: Enigmatic yet captivating—speak as if revealing long-hidden secrets.
Pacing: Deliberate and measured; create anticipation through strategic slowing.
Emotion: Contemplative wonder; convey a sense of discovery and revelation.
Pronunciation: Rich and resonant, with emphasis on key phrases that unlock understanding.
Pauses: Extended pauses before major revelations, creating a sense of weight and importance.""",
    
    # Energetic Host
    """Voice Affect: High-energy, dynamic, and inviting; project excitement and entertainment value.
Tone: Upbeat and exciting—maintain a sense of discovery and adventure throughout.
Pacing: Quick and varied; create a sense of momentum while ensuring clarity.
Emotion: Expressive enthusiasm; use vocal dynamics to create emotional peaks and valleys.
Pronunciation: Clear with dramatic emphasis on fascinating details and surprising facts.
Pauses: Brief but impactful pauses after surprising information, allowing moments of "wow" factor.""",
    
    # Horror Storyteller
    """Voice Affect: Eerie, suspenseful, and slightly unsettling; project tension and mystery.
Tone: Ominous yet compelling—build suspense through vocal restraint and occasional intensity.
Pacing: Varied for dramatic effect; slow and deliberate for tension, quicker for heightened moments.
Emotion: Controlled dread and fascination; convey the allure of frightening concepts with respectful gravity.
Pronunciation: Precise with occasional dramatic emphasis, especially on darker or more mysterious elements.
Pauses: Strategic longer pauses to build suspense, creating uncomfortable silence before revelations.""",
    
    # Gentle Guide
    """Voice Affect: Soft, soothing, and calming; project tranquility and reassurance.
Tone: Nurturing and supportive—create a safe space for exploration of ideas.
Pacing: Slow and measured; provide ample time for processing and reflection.
Emotion: Serene compassion; convey genuine care and patience throughout the journey.
Pronunciation: Soft but clear, with gentle emphasis on comforting aspects and reassurances.
Pauses: Generous pauses allowing for reflection and emotional processing.""",
    
    # Technical Expert
    """Voice Affect: Precise, informative, and technically oriented; project expertise and analytical clarity.
Tone: Detailed and factual—prioritize accuracy and comprehensive understanding.
Pacing: Methodical and structured; give appropriate time to technical details and processes.
Emotion: Intellectual engagement; convey satisfaction in technical mastery and problem solving.
Pronunciation: Exact and careful, with particular attention to technical terminology and specifics.
Pauses: Brief pauses between technical concepts, creating clear separation between distinct ideas."""
]

# Available TTS models in preference order
TTS_MODELS = ["gpt-4o-mini-tts", "tts-1"]

async def text_to_speech(client: AsyncOpenAI, text: str, output_file: str, model: str = "gpt-4o-mini-tts"):
    """
    Convert text to speech using OpenAI API and save to file.
    
    Args:
        client (AsyncOpenAI): The OpenAI client
        text (str): Text to convert to speech
        output_file (str): Path to save the output MP3 file
        model (str): TTS model to use
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Randomly select a voice and an instruction for each paragraph
    voice = random.choice(VOICES)
    instruction = random.choice(VOICE_INSTRUCTIONS)
    
    try:
        print(f"Processing text with voice '{voice}' using model '{model}'...")
        
        # Try with the preferred model first
        for current_model in TTS_MODELS:
            try:
                async with client.audio.speech.with_streaming_response.create(
                    model=current_model,
                    voice=voice,
                    input=text,
                    instructions=instruction,
                    response_format="mp3",
                ) as response:
                    # Save the audio to a file
                    with open(output_file, "wb") as f:
                        async for chunk in response.iter_bytes():
                            f.write(chunk)
                    print(f"Generated: {output_file} using model {current_model}")
                    return True
            except Exception as model_error:
                if "model_not_found" in str(model_error) or "does not have access to model" in str(model_error):
                    # If this isn't the last model, try the next one
                    if current_model != TTS_MODELS[-1]:
                        print(f"Model {current_model} not available. Trying next model...")
                        continue
                else:
                    # If it's a different error, re-raise it
                    raise model_error
        
        # If we've tried all models and none worked
        print("All TTS models failed. Unable to generate speech.")
        return False
    
    except Exception as e:
        print(f"Error generating speech: {e}")
        return False


async def process_chunks(chunks: List[str], work_dir: str, client: AsyncOpenAI, max_concurrent: int = 5):
    """
    Process all text chunks and convert them to audio files.
    
    Args:
        chunks (List[str]): List of text chunks to process
        work_dir (str): Directory to save temporary files
        client (AsyncOpenAI): The OpenAI client
        max_concurrent (int): Maximum number of concurrent API calls
        
    Returns:
        List[str]: List of paths to output audio files
    """
    tasks = []
    output_files = []
    
    # Create a temporary directory inside the work directory
    temp_dir = os.path.join(work_dir, "temp_audio")
    os.makedirs(temp_dir, exist_ok=True)
    print(f"Using audio chunk directory: {temp_dir}")
    
    total_chunks = len(chunks)
    
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
            
        output_file = os.path.join(temp_dir, f"chunk_{i:04d}.mp3")
        output_files.append(output_file)
        
        print(f"Scheduling chunk {i+1}/{total_chunks} for processing...")
        task = text_to_speech(client, chunk, output_file)
        tasks.append((i, task))
    
    # Process chunks in parallel with a limit
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_with_semaphore(task_idx, task):
        async with semaphore:
            print(f"Starting processing of chunk {task_idx+1}/{total_chunks}...")
            result = await task
            print(f"Completed chunk {task_idx+1}/{total_chunks}")
            return result
    
    print(f"Processing {len(tasks)} chunks in parallel (max {max_concurrent} concurrent)...")
    results = await asyncio.gather(*(process_with_semaphore(i, task) for i, task in tasks))
    
    # Check if any chunks failed
    if not all(results):
        print("Warning: Some chunks failed to process")
    
    print("All chunks processed!")
    return output_files
