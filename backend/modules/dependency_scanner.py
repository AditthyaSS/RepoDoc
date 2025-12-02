"""Dependency file scanner for repositories."""

import os
from pathlib import Path
from typing import List, Dict, Optional
import re


class DependencyScanner:
    """Scans repositories for dependency files and extracts package information."""
    
    SUPPORTED_FILES = {
        "requirements.txt": "python",
        "package.json": "javascript",
        "Pipfile": "python",
        "pyproject.toml": "python"
    }
    
    def __init__(self, repo_path: str):
        """
        Initialize scanner with repository path.
        
        Args:
            repo_path: Path to the cloned repository
        """
        self.repo_path = Path(repo_path)
    
    def find_dependency_files(self) -> List[Dict[str, str]]:
        """
        Find all supported dependency files in the repository.
        
        Returns:
            List of dictionaries with file info (path, type)
        """
        found_files = []
        
        for filename, file_type in self.SUPPORTED_FILES.items():
            file_path = self.repo_path / filename
            if file_path.exists():
                found_files.append({
                    "filename": filename,
                    "path": str(file_path),
                    "type": file_type
                })
        
        return found_files
    
    def parse_requirements_txt(self, file_path: str) -> List[Dict[str, Optional[str]]]:
        """
        Parse a requirements.txt file and extract dependencies.
        
        Args:
            file_path: Path to requirements.txt
            
        Returns:
            List of dictionaries with package name and version
        """
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Skip editable installs and URLs
                    if line.startswith('-e') or line.startswith('http'):
                        continue
                    
                    # Parse package name and version
                    package_info = self._parse_requirement_line(line)
                    if package_info:
                        dependencies.append(package_info)
        
        except Exception as e:
            raise Exception(f"Failed to parse requirements.txt: {str(e)}")
        
        return dependencies
    
    def _parse_requirement_line(self, line: str) -> Optional[Dict[str, Optional[str]]]:
        """
        Parse a single requirement line.
        
        Args:
            line: Single line from requirements file
            
        Returns:
            Dictionary with package name and version, or None if invalid
        """
        # Remove inline comments
        line = line.split('#')[0].strip()
        
        if not line:
            return None
        
        # Match patterns like: package==1.0.0, package>=1.0.0, package~=1.0.0, etc.
        patterns = [
            r'^([a-zA-Z0-9\-_\.]+)==([0-9\.]+[a-zA-Z0-9\.]*)$',  # exact version
            r'^([a-zA-Z0-9\-_\.]+)>=([0-9\.]+[a-zA-Z0-9\.]*)$',  # minimum version
            r'^([a-zA-Z0-9\-_\.]+)~=([0-9\.]+[a-zA-Z0-9\.]*)$',  # compatible version
            r'^([a-zA-Z0-9\-_\.]+)$',  # no version specified
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                groups = match.groups()
                return {
                    "name": groups[0],
                    "version": groups[1] if len(groups) > 1 else None
                }
        
        return None
    
    def scan(self) -> Dict:
        """
        Scan repository and return all found dependencies.
        
        Returns:
            Dictionary with dependency files and their contents
        """
        result = {
            "files_found": [],
            "dependencies": []
        }
        
        dependency_files = self.find_dependency_files()
        result["files_found"] = dependency_files
        
        # Parse each found file
        for file_info in dependency_files:
            if file_info["filename"] == "requirements.txt":
                deps = self.parse_requirements_txt(file_info["path"])
                result["dependencies"].extend(deps)
        
        return result
