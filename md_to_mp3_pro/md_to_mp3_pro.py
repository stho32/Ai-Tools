#!/usr/bin/env python3
"""
md_to_mp3_pro.py - Convert markdown files to MP3 using OpenAI's text-to-speech API

This enhanced version:
- Tracks file changes using hashing
- Only processes modified or new files
- Uses an improved paragraph-by-paragraph TTS approach with varied voices
- Stores audio files alongside markdown files
- Supports a working directory for caching and temporary files
- Can resume processing after interruption or crash

Usage:
    python md_to_mp3_pro.py input_path work_path

Example:
    python md_to_mp3_pro.py C:\Books\MyBook C:\Output\WorkDir
"""

import argparse
import asyncio
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Tuple

from openai import AsyncOpenAI

# Import local modules
from lib.chunking import split_text_into_chunks, split_md_file_into_paragraphs
from lib.tts import process_chunks
from lib.audio import combine_audio_files
from lib.file_tracking import identify_changed_files, update_file_status


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Convert markdown files to MP3 using OpenAI TTS")
    parser.add_argument("input_path", help="Directory containing markdown files")
    parser.add_argument("work_path", help="Working directory for temporary files and hash memory")
    parser.add_argument("--api-key", help="OpenAI API key (optional, defaults to env var)")
    return parser.parse_args()


async def process_markdown_file(md_file: Path, work_dir: str, client: AsyncOpenAI) -> bool:
    """
    Process a single markdown file and convert it to MP3.
    
    Args:
        md_file (Path): Path to the markdown file
        work_dir (str): Working directory for temporary files
        client (AsyncOpenAI): OpenAI client
        
    Returns:
        bool: True if successful, False otherwise
    """
    file_path_str = str(md_file)
    
    try:
        # Mark file as being processed
        update_file_status(work_dir, file_path_str, "processing")
        
        file_name = md_file.stem
        output_file = md_file.with_suffix('.mp3')
        
        print(f"\n{'=' * 80}")
        print(f"Processing file: {md_file}")
        print(f"Output will be saved to: {output_file}")
        print(f"{'=' * 80}\n")
        
        # Read the markdown file
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Create a folder for this file's temporary chunks
        file_work_dir = os.path.join(work_dir, f"tmp_{file_name}")
        os.makedirs(file_work_dir, exist_ok=True)
        
        # Split content into chunks
        print("Splitting text into chunks...")
        chunks = split_text_into_chunks(content)
        print(f"Split text into {len(chunks)} chunks")
        
        # Process chunks
        print("Starting text-to-speech conversion...")
        start_time = time.time()
        audio_files = await process_chunks(chunks, file_work_dir, client)
        elapsed = time.time() - start_time
        print(f"Text-to-speech conversion completed in {elapsed:.2f} seconds")
        
        # Combine audio files
        print("Combining audio files...")
        success = combine_audio_files(audio_files, str(output_file))
        
        if success:
            print(f"Conversion successful: {output_file}")
            # Mark file as completed
            update_file_status(work_dir, file_path_str, "completed")
            return True
        else:
            print(f"Failed to create MP3 for {md_file}")
            # Mark file as failed
            update_file_status(work_dir, file_path_str, "failed")
            return False
    
    except Exception as e:
        print(f"Error processing file {md_file}: {e}")
        import traceback
        traceback.print_exc()
        # Mark file as failed
        update_file_status(work_dir, file_path_str, "failed")
        return False


async def main():
    """Main function."""
    try:
        args = parse_arguments()
        
        print(f"MD to MP3 Pro - Starting at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check if paths exist
        if not os.path.isdir(args.input_path):
            print(f"Error: Input directory '{args.input_path}' does not exist.")
            return 1
        
        # Create work directory if it doesn't exist
        os.makedirs(args.work_path, exist_ok=True)
        print(f"Using work directory: {args.work_path}")
        
        # Set up API key
        if args.api_key:
            os.environ["OPENAI_API_KEY"] = args.api_key
        
        if not os.environ.get("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY environment variable not set.")
            print("Please set the environment variable or provide --api-key argument.")
            return 1
        
        # Initialize the OpenAI client
        client = AsyncOpenAI()
        print("Initialized OpenAI client")
        
        # Identify files that need to be processed (changed, new, or previously interrupted)
        files_to_process, hash_memory = identify_changed_files(args.input_path, args.work_path)
        
        if not files_to_process:
            print("No new, modified, or interrupted files found. Nothing to do.")
            return 0
        
        # Process each file
        success_count = 0
        for i, md_file in enumerate(files_to_process, 1):
            print(f"\nProcessing file {i}/{len(files_to_process)}: {md_file.name}")
            success = await process_markdown_file(md_file, args.work_path, client)
            if success:
                success_count += 1
        
        # Print summary
        print(f"\n{'=' * 80}")
        print(f"Processing complete: {success_count}/{len(files_to_process)} files successful")
        print(f"Temporary files are in: {args.work_path}")
        print(f"Finished at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 80}")
        
        return 0
    
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
