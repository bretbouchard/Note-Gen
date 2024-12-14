"""Check for circular imports in the codebase."""
import ast
from pathlib import Path
from typing import Set, Dict, List, Optional, Union
import importlib.util
from types import ModuleType

def get_imports(file_path: Path) -> Set[str]:
    """Get all imports from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=str(file_path))

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.add(name.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports

def find_circular_imports(directory: Path) -> Dict[str, Set[str]]:
    """Find circular imports in Python files."""
    circular_imports: Dict[str, Set[str]] = {}
    visited_files: Set[str] = set()
    
    def check_file(file_path: Path, import_chain: List[str]) -> None:
        """Check a file for circular imports."""
        if str(file_path) in visited_files:
            return
        
        visited_files.add(str(file_path))
        imports = get_imports(file_path)
        
        for imp in imports:
            if imp in import_chain:
                start_idx = import_chain.index(imp)
                cycle = import_chain[start_idx:] + [imp]
                circular_imports[imp] = set(cycle)
            else:
                imp_path = find_module_path(directory, imp)
                if imp_path:
                    check_file(imp_path, import_chain + [imp])

    for file_path in directory.rglob('*.py'):
        if file_path.is_file() and not any(p.name.startswith('.') for p in file_path.parents):
            check_file(file_path, [])

    return circular_imports

def find_module_path(base_dir: Path, module_name: str) -> Optional[Path]:
    """Find the path to a module."""
    parts = module_name.split('.')
    current_dir = base_dir
    
    for part in parts[:-1]:
        current_dir = current_dir / part
        if not current_dir.is_dir():
            return None
    
    module_file = current_dir / f"{parts[-1]}.py"
    if module_file.is_file():
        return module_file
    
    return None

def import_module(module_path: Union[str, Path]) -> Optional[ModuleType]:
    """Import a module from a file path."""
    try:
        spec = importlib.util.spec_from_file_location(
            module_path.stem if isinstance(module_path, Path) else Path(module_path).stem,
            str(module_path)
        )
        if spec is None or spec.loader is None:
            return None
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Error importing module {module_path}: {str(e)}")
        return None

def main() -> None:
    """Main function to check for circular imports."""
    base_dir = Path(__file__).parent.parent
    circular_imports = find_circular_imports(base_dir)
    
    if circular_imports:
        print("Found circular imports:")
        for module, cycle in circular_imports.items():
            print(f"{module}: {' -> '.join(cycle)}")
    else:
        print("No circular imports found.")

if __name__ == '__main__':
    main()
