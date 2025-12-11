from typing import Set

# Default directories and files to ignore during scans
IGNORED_NAMES: Set[str] = {'.venv', 'venv', '__pycache__'}

def is_ignored(name: str) -> bool:
    """
    Check if a file or directory name should be ignored.
    
    Args:
        name: The name of the file or directory (not the full path).
        
    Returns:
        True if the name starts with '.' or is in the ignored list.
    """
    return name.startswith('.') or name in IGNORED_NAMES
