#!/usr/bin/env python3
"""
MdBuch2MP3 - Convert markdown files to MP3 using OpenAI's text-to-speech API

Usage:
    python md_to_mp3.py input_path output_path [--model MODEL]

Example:
    python md_to_mp3.py C:\Books\MyBook C:\Output --model gpt-4o-mini-tts
"""

import argparse
import asyncio
import os
import random
import sys
from pathlib import Path
from typing import List, Dict, Tuple

from openai import AsyncOpenAI
from pydub import AudioSegment

# Maximum text length that can be processed at once by the OpenAI TTS API
MAX_CHUNK_SIZE = 4000  # Characters

# Available voices in the OpenAI TTS API
VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer", "coral"]

# Instructions for different trainer types
TRAINER_INSTRUCTIONS = [
    """Voice Affect: Energetic, enthusiastic, and motivational; project confidence and passion.
Tone: Inspirational and encouraging—express genuine excitement about the material and belief in the listener's ability to learn.
Pacing: Dynamic and engaging; vary speed to emphasize key points, with strategic pauses before important concepts.
Emotion: Genuine enthusiasm and positivity; speak with warmth and occasional excitement spikes when introducing breakthrough concepts.
Pronunciation: Clear and precise, with slight emphasis on technical terms to aid memorization.
Pauses: Strategic pauses after introducing complex ideas, creating moments for mental processing.""",
    
    """Voice Affect: Calm, methodical, and analytical; project expertise and thoughtfulness.
Tone: Authoritative yet accessible—communicate complex ideas with clarity and precision.
Pacing: Steady and deliberate; take time with difficult concepts, ensuring thorough explanation.
Emotion: Measured intellectual curiosity; convey fascination with the subject matter in a controlled manner.
Pronunciation: Articulate and precise, with careful enunciation of technical terminology.
Pauses: Thoughtful pauses after explaining difficult concepts, allowing time for reflection.""",
    
    """Voice Affect: Warm, conversational, and relatable; project friendliness and accessibility.
Tone: Collaborative and supportive—speak as if having a one-on-one conversation with a friend.
Pacing: Natural and comfortable; match the rhythm of everyday speech with occasional slowing for key insights.
Emotion: Genuine interest and care; speak with warmth and occasional humor to maintain engagement.
Pronunciation: Clear but casual, making technical concepts sound approachable and digestible.
Pauses: Natural conversational pauses, creating a rhythm that feels like dialogue rather than lecture.""",
    
    """Voice Affect: Direct, practical, and efficient; project competence and experience.
Tone: No-nonsense but helpful—focus on delivering actionable knowledge without fluff.
Pacing: Brisk but clear; move efficiently through material while ensuring comprehension.
Emotion: Controlled enthusiasm for practical applications; emphasize utility and real-world relevance.
Pronunciation: Clear and straightforward, with emphasis on key action items and practical techniques.
Pauses: Brief, purposeful pauses before transitioning to new topics or summarizing important points.""",
    
    """Voice Affect: Storytelling, engaging, and vivid; project creativity and perspective.
Tone: Narrative and contextual—connect concepts to broader themes and real-world scenarios.
Pacing: Varied and dynamic; slow down for complex ideas, speed up for examples and illustrations.
Emotion: Rich emotional range; convey wonder, curiosity, and occasional drama to highlight importance.
Pronunciation: Expressive and colorful, with tonal variation to bring concepts to life.
Pauses: Dramatic pauses before key revelations or connections, creating narrative tension and resolution."""
]


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Convert markdown files to MP3 using OpenAI TTS")
    parser.add_argument("input_path", help="Directory containing markdown files")
    parser.add_argument("output_path", help="Directory for output files")
    parser.add_argument("--model", default="gpt-4o-mini-tts", help="OpenAI TTS model (default: gpt-4o-mini-tts)")
    parser.add_argument("--api-key", help="OpenAI API key (optional, defaults to env var)")
    return parser.parse_args()


def collect_markdown_files(directory: str) -> List[Path]:
    """Collect all markdown files from the directory and sort them by name."""
    md_files = list(Path(directory).glob("*.md"))
    md_files.sort(key=lambda x: x.stem.lower())
    return md_files


def concatenate_markdown_files(md_files: List[Path]) -> str:
    """Concatenate markdown files with filenames as headings."""
    combined_text = ""
    
    for md_file in md_files:
        heading = f"# {md_file.stem}\n\n"
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        combined_text += heading + content + "\n\n"
    
    return combined_text


def split_text_into_chunks(text: str) -> List[str]:
    """Split text into chunks that can be processed by the API."""
    chunks = []
    paragraphs = text.split("\n\n")
    
    current_chunk = ""
    for paragraph in paragraphs:
        # If adding this paragraph would exceed the chunk size, save current chunk and start a new one
        if len(current_chunk) + len(paragraph) + 2 > MAX_CHUNK_SIZE:  # +2 for \n\n
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n\n"
        else:
            current_chunk += paragraph + "\n\n"
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


async def text_to_speech(client: AsyncOpenAI, text: str, output_file: str, model: str):
    """Convert text to speech using OpenAI API and save to file."""
    # Randomly select a voice and an instruction
    voice = random.choice(VOICES)
    instruction = random.choice(TRAINER_INSTRUCTIONS)
    
    try:
        print(f"Processing chunk with voice '{voice}'...")
        try:
            # First attempt with the requested model
            async with client.audio.speech.with_streaming_response.create(
                model=model,
                voice=voice,
                input=text,
                instructions=instruction,
                response_format="mp3",
            ) as response:
                # Save the audio to a file
                with open(output_file, "wb") as f:
                    async for chunk in response.iter_bytes():
                        f.write(chunk)
                print(f"Generated: {output_file}")
        except Exception as model_error:
            if "model_not_found" in str(model_error) or "does not have access to model" in str(model_error):
                # Fallback to tts-1 if the requested model is not available
                fallback_model = "tts-1"
                print(f"Model {model} not available. Falling back to {fallback_model}...")
                
                async with client.audio.speech.with_streaming_response.create(
                    model=fallback_model,
                    voice=voice,
                    input=text,
                    instructions=instruction,
                    response_format="mp3",
                ) as response:
                    # Save the audio to a file
                    with open(output_file, "wb") as f:
                        async for chunk in response.iter_bytes():
                            f.write(chunk)
                    print(f"Generated: {output_file} using fallback model")
            else:
                # If it's a different error, re-raise it
                raise model_error
    except Exception as e:
        print(f"Error generating speech for chunk: {e}")
        raise


async def process_chunks(chunks: List[str], model: str, output_dir: str, client: AsyncOpenAI):
    """Process all text chunks and convert them to audio files."""
    tasks = []
    output_files = []
    
    # Create a temporary directory inside the output directory
    temp_dir = os.path.join(output_dir, "temp_audio")
    os.makedirs(temp_dir, exist_ok=True)
    print(f"Created temporary directory for audio chunks: {temp_dir}")
    
    total_chunks = len(chunks)
    
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
            
        output_file = os.path.join(temp_dir, f"chunk_{i:04d}.mp3")
        output_files.append(output_file)
        
        print(f"Scheduling chunk {i+1}/{total_chunks} for processing...")
        task = text_to_speech(client, chunk, output_file, model)
        tasks.append(task)
    
    # Process chunks in parallel with a limit (to avoid overwhelming the API)
    semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent API calls
    
    async def process_with_semaphore(task_idx, task):
        async with semaphore:
            print(f"Starting processing of chunk {task_idx+1}/{total_chunks}...")
            await task
            print(f"Completed chunk {task_idx+1}/{total_chunks}")
    
    print(f"Processing {len(tasks)} chunks in parallel (max 5 concurrent)...")
    await asyncio.gather(*(process_with_semaphore(i, task) for i, task in enumerate(tasks)))
    print("All chunks processed successfully!")
    
    return output_files


def combine_audio_files(audio_files: List[str], output_file: str):
    """Combine multiple MP3 files into a single file."""
    if not audio_files:
        raise ValueError("No audio files to combine")
    
    print(f"Combining {len(audio_files)} audio files...")
    
    # Start with the first audio file
    combined = AudioSegment.from_mp3(audio_files[0])
    print(f"Added first audio segment ({os.path.basename(audio_files[0])})")
    
    # Add the rest of the audio files
    for i, audio_file in enumerate(audio_files[1:], 1):
        print(f"Adding audio segment {i+1}/{len(audio_files)} ({os.path.basename(audio_file)})")
        audio = AudioSegment.from_mp3(audio_file)
        combined += audio
    
    # Export the combined audio
    print(f"Exporting combined audio to {output_file}...")
    combined.export(output_file, format="mp3")
    print(f"Combined audio saved to: {output_file}")


async def main():
    """Main function."""
    try:
        args = parse_arguments()
        
        # Check if paths exist
        if not os.path.isdir(args.input_path):
            print(f"Error: Input directory '{args.input_path}' does not exist.")
            return 1
        
        # Set up API key
        if args.api_key:
            os.environ["OPENAI_API_KEY"] = args.api_key
        
        if not os.environ.get("OPENAI_API_KEY"):
            api_key = input("Please enter your OpenAI API key: ")
            os.environ["OPENAI_API_KEY"] = api_key
        
        # Initialize the OpenAI client
        client = AsyncOpenAI()
        print("Initialized OpenAI client")
        
        # Create output directory if it doesn't exist
        os.makedirs(args.output_path, exist_ok=True)
        print(f"Ensured output directory exists: {args.output_path}")
        
        # Get input directory name for the final filename
        input_dir_name = os.path.basename(os.path.normpath(args.input_path))
        final_output_file = os.path.join(args.output_path, f"{input_dir_name}.mp3")
        print(f"Final output will be saved as: {final_output_file}")
        
        # Collect and process markdown files
        print(f"Collecting markdown files from {args.input_path}...")
        md_files = collect_markdown_files(args.input_path)
        if not md_files:
            print(f"No markdown files found in {args.input_path}")
            return 1
        
        print(f"Found {len(md_files)} markdown files")
        print("Concatenating markdown files...")
        combined_text = concatenate_markdown_files(md_files)
        
        # Save combined text for reference
        text_output_file = os.path.join(args.output_path, f"{input_dir_name}.txt")
        print(f"Saving combined text to {text_output_file}...")
        with open(text_output_file, "w", encoding="utf-8") as f:
            f.write(combined_text)
        print(f"Combined text saved to: {text_output_file}")
        
        # Split text into chunks
        print("Splitting text into chunks...")
        chunks = split_text_into_chunks(combined_text)
        print(f"Split text into {len(chunks)} chunks")
        
        # Process chunks in the output directory
        print("Starting text-to-speech conversion...")
        audio_files = await process_chunks(chunks, args.model, args.output_path, client)
        
        # Combine audio files
        print("Combining audio files...")
        combine_audio_files(audio_files, final_output_file)
        
        # Cleanup temporary files
        temp_dir = os.path.join(args.output_path, "temp_audio")
        print(f"Conversion complete! Final output saved to: {final_output_file}")
        print(f"Temporary audio files are in: {temp_dir}")
        
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
