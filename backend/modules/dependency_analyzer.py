# backend/modules/dependency_analyzer.py
import os
import json
import time
from pathlib import Path
import subprocess
from packaging import version as pkg_version
from typing import Dict, List

class DependencyAnalyzer:
    def __init__(self):
        # folders we won't descend into
        self.ignored_dirs = {
            "node_modules", "dist", "build", "coverage", "public",
            ".github", "docs", "examples", "test", "tests", "benchmark"
        }
        self.priority_dirs = {"", "packages", "app", "src", "services", "modules"}
        self.max_files_per_dir = 5000
        self.timeout_seconds = 30

    def analyze(self, repo_path: str) -> Dict:
        start_time = time.time()
        repo_path = Path(repo_path)

        package_files = []
        # find package.json files in priority folders
        for folder in self.priority_dirs:
            folder_path = repo_path / folder
            if folder_path.exists():
                for root, dirs, files in os.walk(folder_path):
                    dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
                    if len(files) > self.max_files_per_dir:
                        continue
                    if time.time() - start_time > self.timeout_seconds:
                        break
                    if "package.json" in files:
                        package_files.append(Path(root) / "package.json")

        all_packages: Dict[str, str] = {}

        for pkg_file in package_files:
            if time.time() - start_time > self.timeout_seconds:
                break
            try:
                with open(pkg_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                deps = data.get("dependencies", {}) or {}
                dev_deps = data.get("devDependencies", {}) or {}
                for pkg, ver in {**deps, **dev_deps}.items():
                    # store first seen version string (may include ^~)
                    all_packages[pkg] = str(ver)
            except Exception:
                # skip unreadable or malformed package.json
                continue

        total_packages = int(len(all_packages))  # force int

        outdated_count = 0
        outdated_packages: List[Dict[str, str]] = []

        # quick check for each package using npm view (if npm is present)
        for pkg, ver in all_packages.items():
            # stop if timeout reached
            if time.time() - start_time > self.timeout_seconds:
                break
            try:
                # normalize the installed version string (strip ^~)
                installed = str(ver).lstrip("^~")
                # call npm to get latest (timeout small to avoid blocking)
                result = subprocess.run(
                    ["npm", "view", pkg, "version"],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                latest = result.stdout.strip()
                if latest:
                    try:
                        if pkg_version.parse(latest) > pkg_version.parse(installed):
                            outdated_count += 1
                            outdated_packages.append({
                                "name": pkg,
                                "current_version": installed,
                                "latest_version": latest
                            })
                    except Exception:
                        # version parsing failed; skip comparison
                        pass
            except Exception:
                # npm not available or network blocked — skip deep check
                continue

        # Score: ensure integer and within 0..100
        health_score = max(0, min(100, 100 - (outdated_count * 2)))
        # If repo was big and we stopped early, mark partial_analysis True
        partial_analysis = bool(time.time() - start_time > self.timeout_seconds)

        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            # keys expected by frontend
            "total_packages": total_packages,
            "outdated_count": int(outdated_count),
            "health_score": int(health_score),
            "partial_analysis": partial_analysis,
            # include list (may be empty) so frontend can iterate safely
            "outdated_packages": outdated_packages
        }
