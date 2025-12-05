import os
import json
from pathlib import Path
from typing import List, Dict, Optional


class DependencyScanner:
    SUPPORTED_FILES = {
        "package.json": "npm",
        "requirements.txt": "pypi",
        "composer.json": "composer"
    }

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)

    def scan(self) -> Dict:
        results = {"dependencies": [], "files_found": []}

        for filename, eco in self.SUPPORTED_FILES.items():
            file_path = self.repo_path / filename
            if file_path.exists():
                results["files_found"].append({
                    "filename": filename,
                    "path": str(file_path),
                    "ecosystem": eco
                })

                if filename == "package.json":
                    results["dependencies"].extend(self._parse_package_json(file_path))

                elif filename == "requirements.txt":
                    results["dependencies"].extend(self._parse_requirements(file_path))

                elif filename == "composer.json":
                    results["dependencies"].extend(self._parse_composer(file_path))

        return results

    def _parse_package_json(self, path: Path):
        deps = []
        try:
            data = json.loads(path.read_text())
            for section in ["dependencies", "devDependencies"]:
                for name, ver in data.get(section, {}).items():
                    deps.append({"name": name, "version": ver, "ecosystem": "npm"})
        except:
            pass
        return deps

    def _parse_requirements(self, path: Path):
        deps = []
        try:
            for line in path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "@" in line:
                    continue
                if "==" in line:
                    name, ver = line.split("==")
                    deps.append({"name": name, "version": ver, "ecosystem": "pypi"})
        except:
            pass
        return deps

    def _parse_composer(self, path: Path):
        deps = []
        try:
            data = json.loads(path.read_text())
            for section in ["require", "require-dev"]:
                for name, ver in data.get(section, {}).items():
                    deps.append({"name": name, "version": ver, "ecosystem": "composer"})
        except:
            pass
        return deps
