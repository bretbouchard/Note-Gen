#!/usr/bin/env python3

import os
import re

def update_imports(root_dir: str) -> None:
    """Update imports from src.note_gen to note_gen."""
    pattern = r'from src\.note_gen\.'
    replacement = 'from note_gen.'
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(filepath, 'r', encoding='latin-1') as f:
                            content = f.read()
                    except Exception as e:
                        print(f"Error reading {filepath}: {e}")
                        continue
                
                # Skip if no matches
                if not re.search(pattern, content):
                    continue
                
                # Replace imports
                new_content = re.sub(pattern, replacement, content)
                
                # Write back if changed
                if new_content != content:
                    print(f"Updating imports in {filepath}")
                    try:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                    except Exception as e:
                        print(f"Error writing {filepath}: {e}")

if __name__ == '__main__':
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    update_imports(root_dir)
