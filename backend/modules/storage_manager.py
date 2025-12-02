"""Storage management for cloned repositories."""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional


class StorageManager:
    """Manages temporary storage directories for cloned repositories."""
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize storage manager.
        
        Args:
            base_dir: Base directory for storage. If None, uses system temp directory.
        """
        self.base_dir = base_dir or tempfile.gettempdir()
        self.repos_dir = Path(self.base_dir) / "repo_fetcher_clones"
        self.repos_dir.mkdir(parents=True, exist_ok=True)
    
    def create_temp_directory(self) -> str:
        """
        Create a temporary directory for a repository.
        
        Returns:
            Absolute path to the created directory
        """
        temp_dir = tempfile.mkdtemp(dir=self.repos_dir)
        return temp_dir
    
    def cleanup_directory(self, path: str) -> bool:
        """
        Remove a directory and all its contents.
        
        Args:
            path: Path to the directory to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
            return True
        except Exception:
            return False
    
    def get_directory_size(self, path: str) -> int:
        """
        Calculate total size of a directory in bytes.
        
        Args:
            path: Path to the directory
            
        Returns:
            Total size in bytes
        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
