#!/usr/bin/env python3
"""
Standardize imports across the codebase.
This script converts all imports from 'src.note_gen.*' to 'note_gen.*'
to ensure consistent import paths.
"""

import os
import re
import sys
from pathlib import Path
from typing import Tuple, Dict, List, Optional, Union, Any

def standardize_imports(filepath: str) -> bool:
    """
    Convert imports from 'src.note_gen.*' to 'note_gen.*' in a file.
    
    Args:
        filepath: Path to the file to process
    
    Returns:
        bool: True if file was modified, False otherwise
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace 'from src.note_gen.' with 'from note_gen.'
        modified_content = re.sub(
            r'from src\.note_gen\.', 
            'from note_gen.', 
            content
        )
        
        # Replace 'import src.note_gen.' with 'import note_gen.'
        modified_content = re.sub(
            r'import src\.note_gen\.', 
            'import note_gen.', 
            modified_content
        )
        
        # Replace direct 'import src.note_gen'
        modified_content = re.sub(
            r'import src\.note_gen$',
            'import note_gen',
            modified_content,
            flags=re.MULTILINE
        )
        
        # Add more specific fixes for app module
        modified_content = re.sub(
            r'from src\.note_gen\.app',
            'from note_gen.app',
            modified_content
        )
        
        modified_content = re.sub(
            r'import src\.note_gen\.app',
            'import note_gen.app',
            modified_content
        )
        
        if content != modified_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            return True
        
        return False
    except UnicodeDecodeError:
        print(f"Skipping file due to encoding issues: {filepath}")
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def process_directory(directory: str) -> Tuple[int, int]:
    """
    Process all Python files in directory and its subdirectories.
    
    Args:
        directory: Directory path to process
    
    Returns:
        tuple: (total files processed, number of files modified)
    """
    total_files = 0
    modified_files = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') or file.endswith('.pyi'):
                filepath = os.path.join(root, file)
                total_files += 1
                
                if standardize_imports(filepath):
                    modified_files += 1
                    print(f"Modified: {filepath}")
    
    return total_files, modified_files

def main() -> None:
    """Main function."""
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = '.'
    
    print(f"Standardizing imports in {directory}...")
    total, modified = process_directory(directory)
    
    print(f"Processed {total} files, modified {modified} files.")

if __name__ == "__main__":
    main()
