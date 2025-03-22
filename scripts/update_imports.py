#!/usr/bin/env python3

import re
from pathlib import Path
from typing import List

def find_python_files(root_dir: str) -> List[Path]:
    """Find all Python files in the project."""
    return list(Path(root_dir).rglob("*.py"))

def update_imports(file_path: Path) -> None:
    """Update imports to use new centralized modules."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update patterns
    patterns = {
        r'from .*?models\.enums import': 'from src.note_gen.core.enums import',
        r'from .*?models\.constants import': 'from src.note_gen.core.constants import',
        r'from .*?models\.core\.enums import': 'from src.note_gen.core.enums import',
        r'from .*?models\.core\.constants import': 'from src.note_gen.core.constants import',
    }

    for old_pattern, new_import in patterns.items():
        content = re.sub(old_pattern, new_import, content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main() -> None:
    """Main function to update imports."""
    project_root = "src/note_gen"
    python_files = find_python_files(project_root)
    
    for file_path in python_files:
        try:
            update_imports(file_path)
            print(f"Updated imports in {file_path}")
        except Exception as e:
            print(f"Error updating {file_path}: {e}")

if __name__ == "__main__":
    main()
