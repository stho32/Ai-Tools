#!/usr/bin/env python3
"""
audio.py - Module for audio processing and manipulation
"""

import os
from typing import List
from pydub import AudioSegment


def combine_audio_files(audio_files: List[str], output_file: str) -> bool:
    """
    Combine multiple MP3 files into a single file.
    
    Args:
        audio_files (List[str]): List of paths to MP3 files to combine
        output_file (str): Path to save the combined MP3 file
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not audio_files:
        print("No audio files to combine")
        return False
    
    try:
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
        return True
    
    except Exception as e:
        print(f"Error combining audio files: {e}")
        return False


def get_audio_duration(file_path: str) -> float:
    """
    Get the duration of an audio file in seconds.
    
    Args:
        file_path (str): Path to the audio file
        
    Returns:
        float: Duration in seconds
    """
    try:
        audio = AudioSegment.from_mp3(file_path)
        return len(audio) / 1000.0  # Convert from milliseconds to seconds
    except Exception as e:
        print(f"Error getting audio duration: {e}")
        return 0.0
