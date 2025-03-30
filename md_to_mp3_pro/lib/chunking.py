#!/usr/bin/env python3
"""
chunking.py - Module for splitting text content into processable chunks
"""

from typing import List, Dict
import re

# Maximum text length that can be processed at once by the OpenAI TTS API
MAX_CHUNK_SIZE = 4000  # Characters

def split_text_into_chunks(text: str) -> List[str]:
    """
    Split text into chunks that can be processed by the API.
    
    Args:
        text (str): The text to split
        
    Returns:
        List[str]: A list of text chunks
    """
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

def split_md_file_into_paragraphs(content: str) -> List[str]:
    """
    Split markdown content into paragraphs.
    
    Args:
        content (str): The markdown content to split
        
    Returns:
        List[str]: A list of paragraphs
    """
    # Split by double newlines (typical paragraph separator in markdown)
    paragraphs = re.split(r'\n\s*\n', content)
    return [p.strip() for p in paragraphs if p.strip()]
