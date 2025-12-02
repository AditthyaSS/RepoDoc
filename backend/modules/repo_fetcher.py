import subprocess
from modules.url_validator import URLValidator
from modules.storage_manager import StorageManager


class RepoFetcher:
    def __init__(self):
        self.validator = URLValidator()
        self.storage = StorageManager()

    def fetch(self, repo_url: str) -> str:
        # ✅ Validate & clean URL
        clean_url = self.validator.validate(repo_url)

        # ✅ Create temporary directory
        target_dir = self.storage.create_temp_directory()

        # ✅ SHALLOW CLONE (Balanced Optimization)
        result = subprocess.run(
            ["git", "clone", "--depth", "1", clean_url, target_dir],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"Git clone failed: {result.stderr}")

        return target_dir
