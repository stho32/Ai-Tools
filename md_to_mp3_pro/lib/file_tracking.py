#!/usr/bin/env python3
"""
file_tracking.py - Module for tracking file changes using hashes
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple


def get_file_hash(file_path: str) -> str:
    """
    Calculate the SHA-256 hash of a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: Hexadecimal hash string
    """
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        return file_hash
    except Exception as e:
        print(f"Error calculating hash for {file_path}: {e}")
        return ""


def load_hash_memory(work_dir: str) -> Dict[str, Dict[str, str]]:
    """
    Load the hash memory from the work directory.
    
    Args:
        work_dir (str): Work directory path
        
    Returns:
        Dict[str, Dict[str, str]]: Dictionary mapping file paths to their metadata (hash and status)
    """
    memory_file = os.path.join(work_dir, "file_hashes.json")
    
    if os.path.exists(memory_file):
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading hash memory: {e}")
            return {}
    else:
        return {}


def save_hash_memory(work_dir: str, hash_memory: Dict[str, Dict[str, str]]) -> None:
    """
    Save the hash memory to the work directory.
    
    Args:
        work_dir (str): Work directory path
        hash_memory (Dict[str, Dict[str, str]]): Dictionary mapping file paths to their metadata
    """
    os.makedirs(work_dir, exist_ok=True)
    memory_file = os.path.join(work_dir, "file_hashes.json")
    
    try:
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(hash_memory, f, indent=2)
        print(f"Hash memory saved to: {memory_file}")
    except Exception as e:
        print(f"Error saving hash memory: {e}")


def collect_markdown_files(directory: str) -> List[Path]:
    """
    Collect all markdown files from the directory.
    
    Args:
        directory (str): Directory to search for markdown files
        
    Returns:
        List[Path]: List of paths to markdown files
    """
    try:
        md_files = list(Path(directory).glob("**/*.md"))
        md_files.sort(key=lambda x: x.stem.lower())
        return md_files
    except Exception as e:
        print(f"Error collecting markdown files: {e}")
        return []


def identify_changed_files(input_dir: str, work_dir: str) -> Tuple[List[Path], Dict[str, Dict[str, str]]]:
    """
    Identify which markdown files have changed or are new, or were previously interrupted during processing.
    
    Args:
        input_dir (str): Input directory containing markdown files
        work_dir (str): Work directory for storing hash memory
        
    Returns:
        Tuple[List[Path], Dict[str, Dict[str, str]]]: List of files to process and updated hash memory
    """
    print(f"Scanning for markdown files in {input_dir}...")
    md_files = collect_markdown_files(input_dir)
    print(f"Found {len(md_files)} markdown files")
    
    # Load existing hash memory
    hash_memory = load_hash_memory(work_dir)
    
    # Convert old format if necessary (backward compatibility)
    if hash_memory and all(isinstance(v, str) for v in hash_memory.values()):
        print("Converting hash memory to new format...")
        new_hash_memory = {}
        for file_path, file_hash in hash_memory.items():
            new_hash_memory[file_path] = {
                "hash": file_hash,
                "status": "completed"
            }
        hash_memory = new_hash_memory
    
    # Identify files to process (changed, new, or previously interrupted)
    files_to_process = []
    for md_file in md_files:
        file_path_str = str(md_file)
        current_hash = get_file_hash(file_path_str)
        
        if not current_hash:
            print(f"Warning: Could not calculate hash for {file_path_str}")
            continue
        
        # Check if file is new, changed, or was previously interrupted
        if file_path_str not in hash_memory:
            # New file
            files_to_process.append(md_file)
            hash_memory[file_path_str] = {
                "hash": current_hash,
                "status": "pending"
            }
            print(f"New file: {md_file.name}")
        elif hash_memory[file_path_str]["hash"] != current_hash:
            # Changed file
            files_to_process.append(md_file)
            hash_memory[file_path_str] = {
                "hash": current_hash,
                "status": "pending"
            }
            print(f"File changed: {md_file.name}")
        elif hash_memory[file_path_str].get("status") != "completed":
            # Previously interrupted file
            files_to_process.append(md_file)
            hash_memory[file_path_str]["status"] = "pending"
            print(f"Resuming interrupted file: {md_file.name}")
    
    # Save updated hash memory
    save_hash_memory(work_dir, hash_memory)
    
    print(f"Identified {len(files_to_process)} files to process")
    return files_to_process, hash_memory


def update_file_status(work_dir: str, file_path: str, status: str) -> None:
    """
    Update the processing status of a file in the hash memory.
    
    Args:
        work_dir (str): Work directory path
        file_path (str): Path to the file
        status (str): New status ('pending', 'processing', 'completed', 'failed')
    """
    hash_memory = load_hash_memory(work_dir)
    
    if file_path in hash_memory:
        hash_memory[file_path]["status"] = status
        save_hash_memory(work_dir, hash_memory)
        print(f"Updated status for {os.path.basename(file_path)}: {status}")
