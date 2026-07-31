from __future__ import annotations

import csv
import hashlib
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    ROOT / "AGENTS.md",
    ROOT / "ARCHITECTURE.md",
    ROOT / "README.md",
    ROOT / "docs" / "design-docs" / "index.md",
    ROOT / "docs" / "exec-plans" / "active",
    ROOT / "docs" / "exec-plans" / "completed",
    ROOT / "docs" / "product-specs" / "Wang2026_fit_contract.md",
    ROOT / "docs" / "reviews",
    ROOT / "docs" / "research-results",
    ROOT / "docs" / "run-evidence" / "index.md",
]
ALLOWED_SUFFIXES = {".md", ".py", ".mjs", ".csv", ".png", ".in", ".c", ".sh", ".json", ".txt"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED:
        if not path.exists():
            errors.append(f"missing: {path}")

    for path in ROOT.rglob("*"):
        if path.is_file() and path.name != ".gitkeep" and path.suffix.lower() not in ALLOWED_SUFFIXES:
            errors.append(f"forbidden suffix: {path}")

    manifest = ROOT / "docs" / "generated" / "post_cutoff_md_manifest.csv"
    if manifest.exists():
        with manifest.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            mirror = ROOT / row["mirror_path"]
            if not mirror.is_file():
                errors.append(f"manifest mirror missing: {mirror}")
            elif sha256(mirror) != row["sha256"].upper():
                errors.append(f"manifest sha mismatch: {mirror}")

    agent_lines = (ROOT / "AGENTS.md").read_text(encoding="utf-8").splitlines()
    if len(agent_lines) > 120:
        errors.append(f"AGENTS.md too long: {len(agent_lines)} lines")

    if errors:
        print("HARNESS_CHECK=FAIL")
        for item in errors:
            print(item)
        return 1

    print("HARNESS_CHECK=PASS")
    print(f"ROOT={ROOT}")
    print(f"AGENTS_LINES={len(agent_lines)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
