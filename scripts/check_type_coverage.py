#!/usr/bin/env python3
"""Check type annotation coverage in the project."""
import ast
import sys
from pathlib import Path
from typing import Set, Tuple

def check_type_annotations(file_path: Path) -> Tuple[int, int, Set[str]]:
    """
    Check type annotations in a Python file.
    Returns (annotated_count, total_count, missing_annotations)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())

    annotated = 0
    total = 0
    missing = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            total += 1
            if node.returns is None:
                missing.add(f"{file_path}:{node.lineno} - {node.name}: missing return type")
            else:
                annotated += 1
            
            for arg in node.args.args:
                total += 1
                if arg.annotation is None:
                    missing.add(f"{file_path}:{arg.lineno} - {node.name}.{arg.arg}: missing parameter type")
                else:
                    annotated += 1

    return annotated, total, missing

def main() -> None:
    """Main function to check type coverage."""
    src_path = Path("src/note_gen")
    total_annotated = 0
    total_count = 0
    all_missing: Set[str] = set()

    for file_path in src_path.rglob("*.py"):
        if file_path.name.startswith("__"):
            continue
        annotated, total, missing = check_type_annotations(file_path)
        total_annotated += annotated
        total_count += total
        all_missing.update(missing)

    coverage = (total_annotated / total_count * 100) if total_count > 0 else 0
    print(f"\nType annotation coverage: {coverage:.2f}%")
    print(f"Total annotations: {total_annotated}/{total_count}")
    
    if all_missing:
        print("\nMissing type annotations:")
        for item in sorted(all_missing):
            print(f"  {item}")
        sys.exit(1)
    
    if coverage < 90:
        print("\nType coverage is below 90%")
        sys.exit(1)

if __name__ == "__main__":
    main()