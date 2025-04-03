#!/usr/bin/env python3
import os
import re

def update_imports(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace imports from src.note_gen to note_gen
    updated_content = re.sub(r'from src\.note_gen\.', 'from note_gen.', content)
    updated_content = re.sub(r'import src\.note_gen\.', 'import note_gen.', updated_content)
    
    if content != updated_content:
        with open(file_path, 'w') as f:
            f.write(updated_content)
        print(f"Updated imports in {file_path}")
    else:
        print(f"No changes needed in {file_path}")

def main():
    core_dir = "src/note_gen/core"
    for root, _, files in os.walk(core_dir):
        for file in files:
            if file.endswith(".py") or file.endswith(".pyi"):
                file_path = os.path.join(root, file)
                update_imports(file_path)

if __name__ == "__main__":
    main()
