#!/usr/bin/env python3
import os
import re

def update_imports(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace imports from src.note_gen to note_gen
    updated_content = re.sub(r'from src\.note_gen\.', 'from note_gen.', content)
    updated_content = re.sub(r'import src\.note_gen\.', 'import note_gen.', updated_content)
    
    # Replace patch paths
    updated_content = re.sub(r'@patch\([\'"]src\.note_gen\.', r'@patch([\'"]note_gen.', updated_content)
    
    if content != updated_content:
        with open(file_path, 'w') as f:
            f.write(updated_content)
        print(f"Updated imports in {file_path}")
    else:
        print(f"No changes needed in {file_path}")

def main():
    test_dirs = ["tests/api", "tests/database"]
    for test_dir in test_dirs:
        for root, _, files in os.walk(test_dir):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    update_imports(file_path)

if __name__ == "__main__":
    main()
