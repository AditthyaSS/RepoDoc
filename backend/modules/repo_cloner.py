"""Repository cloning functionality."""

import subprocess
from typing import Optional


class RepoCloner:
    """Clones Git repositories locally."""
    
    @staticmethod
    def clone(repo_url: str, target_path: str, depth: Optional[int] = None) -> bool:
        """
        Clone a Git repository to the specified path.
        
        Args:
            repo_url: URL of the repository to clone
            target_path: Local path where the repository should be cloned
            depth: Optional depth for shallow clone
            
        Returns:
            True if cloning was successful, False otherwise
            
        Raises:
            subprocess.CalledProcessError: If git clone fails
        """
        cmd = ["git", "clone"]
        
        if depth:
            cmd.extend(["--depth", str(depth)])
        
        cmd.extend([repo_url, target_path])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=300  # 5 minute timeout
            )
            return True
        except subprocess.CalledProcessError as e:
            raise Exception(f"Git clone failed: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise Exception("Git clone timed out after 5 minutes")
        except FileNotFoundError:
            raise Exception("Git is not installed or not in PATH")
