import os
import json
import time
from pathlib import Path
import subprocess
from packaging import version as pkg_version


class DependencyAnalyzer:
    def __init__(self):
        # ⛔ Skip heavy & useless folders
        self.ignored_dirs = {
            "node_modules", "dist", "build", "coverage", "public",
            ".github", "docs", "examples", "test", "tests", "benchmark"
        }

        # ✅ Only scan these priority locations
        self.priority_dirs = {
            "", "packages", "app", "src", "services", "modules"
        }

        self.max_files_per_dir = 5000  # ✅ Skip huge folders
        self.timeout_seconds = 30      # ✅ 30-second max runtime

    def analyze(self, repo_path: str):
        start_time = time.time()
        repo_path = Path(repo_path)

        package_files = []

        # ✅ Look only in priority folders
        for folder in self.priority_dirs:
            folder_path = repo_path / folder
            if folder_path.exists():
                for root, dirs, files in os.walk(folder_path):

                    # ⛔ Skip ignored folders
                    dirs[:] = [d for d in dirs if d not in self.ignored_dirs]

                    # ✅ Skip huge folders
                    if len(files) > self.max_files_per_dir:
                        continue

                    # ✅ Stop if time is up
                    if time.time() - start_time > self.timeout_seconds:
                        break

                    # ✅ Collect package.json
                    if "package.json" in files:
                        package_files.append(Path(root) / "package.json")

        total_packages = 0
        outdated = 0
        all_packages = {}

        for pkg_file in package_files:
            if time.time() - start_time > self.timeout_seconds:
                break

            try:
                with open(pkg_file, "r") as f:
                    data = json.load(f)

                deps = data.get("dependencies", {})
                dev_deps = data.get("devDependencies", {})

                for pkg, ver in {**deps, **dev_deps}.items():
                    all_packages[pkg] = ver

            except:
                continue

        # ✅ Count packages
        total_packages = len(all_packages)

        # ✅ Check outdated packages (fast lookup)
        for pkg, ver in all_packages.items():
            try:
                result = subprocess.run(
                    ["npm", "view", pkg, "version"],
                    capture_output=True, text=True, timeout=3
                )
                latest = result.stdout.strip()

                if latest and pkg_version.parse(latest) > pkg_version.parse(ver.strip("^~")):
                    outdated += 1

            except:
                pass

        # ✅ Score
        health = max(10, 100 - outdated * 2)

        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_packages": total_packages,
                "outdated_count": outdated
            },
            "health_score": health,
            "partial": time.time() - start_time > self.timeout_seconds
        }
