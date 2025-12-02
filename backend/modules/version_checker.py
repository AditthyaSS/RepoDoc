"""Version checker for Python packages using PyPI API."""

import requests
from typing import Dict, Optional
from packaging import version as pkg_version


class VersionChecker:
    """Checks package versions against PyPI registry."""
    
    PYPI_API_URL = "https://pypi.org/pypi/{package}/json"
    
    def __init__(self, timeout: int = 10):
        """
        Initialize version checker.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
    
    def get_latest_version(self, package_name: str) -> Optional[str]:
        """
        Get the latest version of a package from PyPI.
        
        Args:
            package_name: Name of the package
            
        Returns:
            Latest version string, or None if not found
        """
        try:
            url = self.PYPI_API_URL.format(package=package_name)
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("info", {}).get("version")
            
            return None
        
        except Exception:
            return None
    
    def is_outdated(self, current_version: Optional[str], latest_version: Optional[str]) -> bool:
        """
        Check if current version is outdated compared to latest.
        
        Args:
            current_version: Current installed version
            latest_version: Latest available version
            
        Returns:
            True if outdated, False otherwise
        """
        if not current_version or not latest_version:
            return False
        
        try:
            current = pkg_version.parse(current_version)
            latest = pkg_version.parse(latest_version)
            return current < latest
        except Exception:
            return False
    
    def check_package(self, package_name: str, current_version: Optional[str]) -> Dict:
        """
        Check a single package and return its status.
        
        Args:
            package_name: Name of the package
            current_version: Current version (can be None)
            
        Returns:
            Dictionary with package status information
        """
        latest_version = self.get_latest_version(package_name)
        
        result = {
            "name": package_name,
            "current_version": current_version,
            "latest_version": latest_version,
            "is_outdated": False,
            "status": "unknown"
        }
        
        if latest_version is None:
            result["status"] = "not_found"
        elif current_version is None:
            result["status"] = "no_version_specified"
        elif self.is_outdated(current_version, latest_version):
            result["is_outdated"] = True
            result["status"] = "outdated"
        else:
            result["status"] = "up_to_date"
        
        return result
    
    def check_multiple_packages(self, packages: list) -> list:
        """
        Check multiple packages and return their statuses.
        
        Args:
            packages: List of dictionaries with 'name' and 'version' keys
            
        Returns:
            List of package status dictionaries
        """
        results = []
        
        for package in packages:
            package_name = package.get("name")
            current_version = package.get("version")
            
            if package_name:
                result = self.check_package(package_name, current_version)
                results.append(result)
        
        return results
