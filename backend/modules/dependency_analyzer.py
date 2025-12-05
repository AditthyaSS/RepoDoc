import time
import json
from urllib import request, parse
from packaging import version as pkg_version
from typing import Dict, List, Optional
from pathlib import Path

from .dependency_scanner import DependencyScanner


def fetch_json(url, timeout=5):
    try:
        req = request.Request(url, headers={"User-Agent": "RepoDoctor"})
        with request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except:
        return None


def clean_version(v):
    if not v:
        return None
    v = v.replace("^", "").replace("~", "").replace(">=", "").replace("<=", "").replace("*", "")
    v = v.replace(">", "").replace("<", "").strip()
    if " " in v:
        v = v.split()[0]
    if v.startswith("v"):
        v = v[1:]
    return v


def compare(cur, lat):
    if not cur or not lat:
        return None
    cur_v = pkg_version.parse(cur)
    lat_v = pkg_version.parse(lat)
    if cur_v == lat_v:
        return "up-to-date"
    if lat_v.release[0] > cur_v.release[0]:
        return "major"
    if lat_v.release[1] > cur_v.release[1]:
        return "minor"
    if lat_v.release[2] > cur_v.release[2]:
        return "patch"
    return "unknown"


class DependencyAnalyzer:
    def __init__(self, timeout_seconds=30):
        self.timeout_seconds = timeout_seconds

    def _npm_latest(self, pkg):
        data = fetch_json(f"https://registry.npmjs.org/{parse.quote(pkg)}")
        if not data:
            return None
        if "dist-tags" in data and "latest" in data["dist-tags"]:
            return clean_version(data["dist-tags"]["latest"])
        versions = list(data.get("versions", {}).keys())
        versions.sort(key=lambda x: pkg_version.parse(clean_version(x)))
        return clean_version(versions[-1]) if versions else None

    def _pypi_latest(self, pkg):
        data = fetch_json(f"https://pypi.org/pypi/{parse.quote(pkg)}/json")
        if not data:
            return None
        return clean_version(data.get("info", {}).get("version"))

    def _composer_latest(self, pkg):
        data = fetch_json(f"https://repo.packagist.org/p2/{pkg}.json")
        if not data:
            return None
        try:
            versions = data["packages"][pkg]
            return clean_version(versions[0]["version"])
        except:
            return None

    def analyze(self, repo_path: str):
        scanner = DependencyScanner(repo_path)
        scan = scanner.scan()

        deps = scan["dependencies"]
        files_found = scan["files_found"]

        all_packages = {}
        for d in deps:
            name = d["name"]
            eco = d["ecosystem"]
            cur = clean_version(d["version"])
            key = f"{eco}:{name}"
            all_packages[key] = {
                "name": name,
                "ecosystem": eco,
                "current_version": cur,
                "latest_version": None,
                "severity": None
            }

        outdated = []
        start = time.time()

        for meta in all_packages.values():
            if time.time() - start > self.timeout_seconds:
                partial = True
                break

            eco = meta["ecosystem"]
            name = meta["name"]

            if eco == "npm":
                latest = self._npm_latest(name)
            elif eco == "pypi":
                latest = self._pypi_latest(name)
            elif eco == "composer":
                latest = self._composer_latest(name)
            else:
                latest = None

            meta["latest_version"] = latest
            meta["severity"] = compare(meta["current_version"], latest)

            if meta["severity"] not in (None, "up-to-date"):
                outdated.append(meta)
        else:
            partial = False

        total = len(all_packages)
        outdated_count = len(outdated)

        # HEALTH SCORE
        score = 100
        for d in outdated:
            if d["severity"] == "major": score -= 8
            if d["severity"] == "minor": score -= 3
            if d["severity"] == "patch": score -= 1

        score -= outdated_count
        score = max(0, min(100, score))

        return {
            "summary": {
                "total_packages": total,
                "outdated_count": outdated_count
            },
            "health_score": score,
            "outdated_packages": outdated,
            "partial": partial
        }
