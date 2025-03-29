#!/usr/bin/env python3
"""
MdBuch2MP3 - Convert markdown files to MP3 using OpenAI's text-to-speech API

Usage:
    python md_to_mp3.py input_path output_path [--voice VOICE] [--model MODEL]

Example:
    python md_to_mp3.py C:\Books\MyBook C:\Output --voice alloy --model tts-1
"""

import argparse
import asyncio
import os
import tempfile
from pathlib import Path
from typing import List, Optional

import openai
from pydub import AudioSegment

# Maximum text length that can be processed at once by the OpenAI TTS API
MAX_CHUNK_SIZE = 4000  # Characters


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Convert markdown files to MP3 using OpenAI TTS")
    parser.add_argument("input_path", help="Directory containing markdown files")
    parser.add_argument("output_path", help="Directory for output files")
    parser.add_argument("--voice", default="alloy", help="OpenAI TTS voice (default: alloy)")
    parser.add_argument("--model", default="tts-1", help="OpenAI TTS model (default: tts-1)")
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


async def text_to_speech(client: openai.AsyncOpenAI, text: str, voice: str, model: str, output_file: str):
    """Convert text to speech using OpenAI API and save to file."""
    try:
        async with client.audio.speech.with_streaming_response.create(
            model=model,
            voice=voice,
            input=text,
        ) as response:
            # Save the audio to a file
            with open(output_file, "wb") as f:
                async for chunk in response.iter_bytes():
                    f.write(chunk)
            print(f"Generated: {output_file}")
    except Exception as e:
        print(f"Error generating speech for chunk: {e}")
        raise


async def process_chunks(chunks: List[str], voice: str, model: str, temp_dir: str, client: openai.AsyncOpenAI):
    """Process all text chunks and convert them to audio files."""
    tasks = []
    output_files = []
    
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
            
        output_file = os.path.join(temp_dir, f"chunk_{i:04d}.mp3")
        output_files.append(output_file)
        
        task = text_to_speech(client, chunk, voice, model, output_file)
        tasks.append(task)
    
    # Process chunks in parallel with a limit (to avoid overwhelming the API)
    semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent API calls
    
    async def process_with_semaphore(task):
        async with semaphore:
            await task
    
    await asyncio.gather(*(process_with_semaphore(task) for task in tasks))
    
    return output_files


def combine_audio_files(audio_files: List[str], output_file: str):
    """Combine multiple MP3 files into a single file."""
    if not audio_files:
        raise ValueError("No audio files to combine")
    
    # Start with the first audio file
    combined = AudioSegment.from_mp3(audio_files[0])
    
    # Add the rest of the audio files
    for audio_file in audio_files[1:]:
        audio = AudioSegment.from_mp3(audio_file)
        combined += audio
    
    # Export the combined audio
    combined.export(output_file, format="mp3")
    print(f"Combined audio saved to: {output_file}")


async def main():
    """Main function."""
    args = parse_arguments()
    
    # Set up API key
    if args.api_key:
        openai.api_key = args.api_key
    elif not os.environ.get("OPENAI_API_KEY"):
        api_key = input("Please enter your OpenAI API key: ")
        os.environ["OPENAI_API_KEY"] = api_key
    
    # Initialize the OpenAI client
    client = openai.AsyncOpenAI()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_path, exist_ok=True)
    
    # Get input directory name for the final filename
    input_dir_name = os.path.basename(os.path.normpath(args.input_path))
    final_output_file = os.path.join(args.output_path, f"{input_dir_name}.mp3")
    
    # Collect and process markdown files
    md_files = collect_markdown_files(args.input_path)
    if not md_files:
        print(f"No markdown files found in {args.input_path}")
        return
    
    print(f"Found {len(md_files)} markdown files")
    combined_text = concatenate_markdown_files(md_files)
    
    # Save combined text for reference
    text_output_file = os.path.join(args.output_path, f"{input_dir_name}.txt")
    with open(text_output_file, "w", encoding="utf-8") as f:
        f.write(combined_text)
    print(f"Combined text saved to: {text_output_file}")
    
    # Split text into chunks
    chunks = split_text_into_chunks(combined_text)
    print(f"Split text into {len(chunks)} chunks")
    
    # Create a temporary directory for the audio chunks
    with tempfile.TemporaryDirectory() as temp_dir:
        # Process chunks and get output files
        print("Converting text chunks to audio...")
        audio_files = await process_chunks(chunks, args.voice, args.model, temp_dir, client)
        
        # Combine audio files
        print("Combining audio files...")
        combine_audio_files(audio_files, final_output_file)
    
    print(f"Conversion complete! Final output saved to: {final_output_file}")


if __name__ == "__main__":
    asyncio.run(main())
