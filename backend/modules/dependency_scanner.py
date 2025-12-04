import os
from pathlib import Path
from typing import List, Dict, Optional
import re


class DependencyScanner:

    SUPPORTED_FILES = {
        "requirements.txt": "python",
        "package.json": "javascript",
        "Pipfile": "python",
        "pyproject.toml": "python"
    }

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)

    def find_dependency_files(self) -> List[Dict[str, str]]:
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
        dependencies = []

        try:
            with open(file_path, "r") as f:
                for line in f:
                    line = line.strip()

                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("-e") or line.startswith("http"):
                        continue

                    parsed = self._parse_line(line)
                    if parsed:
                        dependencies.append(parsed)

        except Exception as e:
            raise Exception(f"Failed to parse requirements.txt: {str(e)}")

        return dependencies

    def _parse_line(self, line: str):
        line = line.split("#")[0].strip()

        patterns = [
            r"^([a-zA-Z0-9\-_\.]+)==(.+)$",
            r"^([a-zA-Z0-9\-_\.]+)>=(.+)$",
            r"^([a-zA-Z0-9\-_\.]+)~=(.+)$",
            r"^([a-zA-Z0-9\-_\.]+)$",
        ]

        for p in patterns:
            match = re.match(p, line)
            if match:
                name = match.group(1)
                version = match.group(2) if match.lastindex and match.lastindex > 1 else None
                return {"name": name, "version": version}

        return None

    def scan(self) -> Dict:
        result = {
            "files_found": [],
            "dependencies": []
        }

        files = self.find_dependency_files()
        result["files_found"] = files

        for file in files:
            if file["filename"] == "requirements.txt":
                result["dependencies"].extend(
                    self.parse_requirements_txt(file["path"])
                )

        return result
