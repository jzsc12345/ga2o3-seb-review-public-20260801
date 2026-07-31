from __future__ import annotations

import csv
import hashlib
from pathlib import Path, PurePosixPath
import shutil
import subprocess


WORKSPACE = Path(__file__).resolve().parents[2]
HARNESS = WORKSPACE / "harness"
COMMIT = "540379dab74fdda861f688204b4d45ec5f59a9d2"
MIRROR_ROOT = HARNESS / "docs" / "imported" / "post_cutoff"
MANIFEST = HARNESS / "docs" / "generated" / "post_cutoff_md_manifest.csv"


def git_z(*args: str) -> list[str]:
    raw = subprocess.check_output(["git", *args], cwd=WORKSPACE)
    return [part.decode("utf-8", errors="surrogateescape") for part in raw.split(b"\0") if part]


def git_text(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=WORKSPACE,
        text=True,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
    ).strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    tracked = set(git_z("diff", "--name-only", "--diff-filter=ACMRTUXB", "-z", COMMIT, "--", "*.md"))
    untracked = set(git_z("ls-files", "--others", "--exclude-standard", "-z", "--", "*.md"))
    candidates = sorted(tracked | untracked)

    rows: list[dict[str, str]] = []
    MIRROR_ROOT.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)

    for rel_text in candidates:
        rel = PurePosixPath(rel_text.replace("\\", "/"))
        if rel.parts and rel.parts[0].lower() == "harness":
            continue
        source = WORKSPACE.joinpath(*rel.parts)
        if not source.is_file():
            continue
        mirror = MIRROR_ROOT.joinpath(*rel.parts)
        mirror.parent.mkdir(parents=True, exist_ok=True)
        if not mirror.exists() or sha256(mirror) != sha256(source):
            shutil.copy2(source, mirror)

        base_blob = ""
        try:
            base_blob = git_text("rev-parse", f"{COMMIT}:{rel.as_posix()}")
        except subprocess.CalledProcessError:
            pass

        stat = source.stat()
        rows.append(
            {
                "source_path": str(source),
                "source_relpath": rel.as_posix(),
                "mirror_path": mirror.relative_to(HARNESS).as_posix(),
                "git_status_class": "UNTRACKED" if rel_text in untracked else "DIFF_FROM_CUTOFF",
                "cutoff_commit": COMMIT,
                "base_blob": base_blob,
                "sha256": sha256(source),
                "size_bytes": str(stat.st_size),
                "creation_time_local": str(stat.st_ctime),
                "mtime_local": str(stat.st_mtime),
                "author_attribution": "AUTHOR_UNVERIFIED",
            }
        )

    fields = list(rows[0]) if rows else [
        "source_path",
        "source_relpath",
        "mirror_path",
        "git_status_class",
        "cutoff_commit",
        "base_blob",
        "sha256",
        "size_bytes",
        "creation_time_local",
        "mtime_local",
        "author_attribution",
    ]
    with MANIFEST.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"POST_CUTOFF_DOCS={len(rows)}")
    print(f"MANIFEST={MANIFEST}")
    print(f"MIRROR_ROOT={MIRROR_ROOT}")


if __name__ == "__main__":
    main()
