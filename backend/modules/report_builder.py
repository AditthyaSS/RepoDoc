"""Report builder for dependency analysis results."""

from typing import Dict, List
from datetime import datetime


class ReportBuilder:
    """Builds structured reports from dependency analysis data."""
    
    @staticmethod
    def build_report(scan_results: Dict, version_check_results: List[Dict]) -> Dict:
        """
        Build a comprehensive analysis report.
        
        Args:
            scan_results: Results from DependencyScanner
            version_check_results: Results from VersionChecker
            
        Returns:
            Structured report dictionary
        """
        total_packages = len(version_check_results)
        outdated_packages = [pkg for pkg in version_check_results if pkg.get("is_outdated")]
        up_to_date_packages = [pkg for pkg in version_check_results if pkg.get("status") == "up_to_date"]
        not_found_packages = [pkg for pkg in version_check_results if pkg.get("status") == "not_found"]
        no_version_packages = [pkg for pkg in version_check_results if pkg.get("status") == "no_version_specified"]
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_packages": total_packages,
                "outdated_count": len(outdated_packages),
                "up_to_date_count": len(up_to_date_packages),
                "not_found_count": len(not_found_packages),
                "no_version_count": len(no_version_packages)
            },
            "files_analyzed": scan_results.get("files_found", []),
            "packages": version_check_results,
            "outdated_packages": outdated_packages,
            "health_score": ReportBuilder._calculate_health_score(
                total_packages,
                len(outdated_packages),
                len(not_found_packages)
            )
        }
        
        return report
    
    @staticmethod
    def _calculate_health_score(total: int, outdated: int, not_found: int) -> float:
        """
        Calculate a health score (0-100) based on dependency status.
        
        Args:
            total: Total number of packages
            outdated: Number of outdated packages
            not_found: Number of packages not found
            
        Returns:
            Health score as a float between 0 and 100
        """
        if total == 0:
            return 100.0
        
        # Penalize outdated and not found packages
        penalty = (outdated * 1.0 + not_found * 0.5) / total
        score = max(0.0, 100.0 - (penalty * 100.0))
        
        return round(score, 2)
    
    @staticmethod
    def build_summary(report: Dict) -> str:
        """
        Build a human-readable summary from the report.
        
        Args:
            report: Analysis report dictionary
            
        Returns:
            Summary string
        """
        summary = report.get("summary", {})
        total = summary.get("total_packages", 0)
        outdated = summary.get("outdated_count", 0)
        health_score = report.get("health_score", 0)
        
        if total == 0:
            return "No dependencies found."
        
        if outdated == 0:
            return f"All {total} dependencies are up to date! Health score: {health_score}/100"
        
        return f"Found {outdated} outdated package(s) out of {total} total. Health score: {health_score}/100"
