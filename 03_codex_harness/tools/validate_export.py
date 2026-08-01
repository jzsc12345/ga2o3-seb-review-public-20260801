#!/usr/bin/env python3
"""Validate the isolated private/public GitHub review export."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote


FORBIDDEN_EXTENSIONS = {
    ".pdf", ".zip", ".str", ".log", ".pem", ".key", ".p12", ".pfx", ".env"
}
HIGH_CONFIDENCE_SECRETS = {
    "private_key": re.compile(rb"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
    "github_token": re.compile(rb"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "openai_key": re.compile(rb"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "aws_key": re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    "slack_token": re.compile(rb"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
}
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
WINDOWS_PATH = re.compile(r"(?<![A-Za-z0-9+.-])(?:[A-Za-z]:[\\/])")
RAW_MESSAGE_ID = re.compile(r"\bmsg_[0-9a-f-]{20,}\b", re.IGNORECASE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def files_under(root: Path) -> list[Path]:
    return sorted(
        (path for path in root.rglob("*") if path.is_file() and ".git" not in path.parts),
        key=lambda path: path.relative_to(root).as_posix(),
    )


def is_text_candidate(path: Path) -> bool:
    return path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif", ".pptx", ".xlsx"}


def validate_manifest(root: Path, manifest_name: str, errors: list[str]) -> None:
    manifest = root / manifest_name
    if not manifest.is_file():
        errors.append(f"missing manifest: {manifest_name}")
        return
    with manifest.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    actual = {
        path.relative_to(root).as_posix(): path
        for path in files_under(root)
        if path.name != manifest_name
    }
    declared = {row["path"]: row for row in rows}
    if len(declared) != len(rows):
        errors.append("manifest contains duplicate paths")
    if set(actual) != set(declared):
        missing = sorted(set(actual) - set(declared))
        extra = sorted(set(declared) - set(actual))
        errors.append(f"manifest coverage mismatch: missing={missing} extra={extra}")
        return
    for rel, path in actual.items():
        row = declared[rel]
        if str(path.stat().st_size) != row["size_bytes"]:
            errors.append(f"manifest size mismatch: {rel}")
        if sha256(path) != row["sha256"].upper():
            errors.append(f"manifest hash mismatch: {rel}")


def validate_links(root: Path, errors: list[str]) -> None:
    for path in files_under(root):
        if path.suffix.lower() not in {".md", ".markdown"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for raw in MARKDOWN_LINK.findall(text):
            target = raw.strip().strip("<>").split("#", 1)[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "restricted://", "workspace://")):
                continue
            if WINDOWS_PATH.search(target) or target.startswith("/"):
                continue
            resolved = (path.parent / unquote(target)).resolve()
            if not resolved.exists():
                errors.append(f"broken markdown link: {path.relative_to(root).as_posix()} -> {raw}")


def validate_lock(root: Path, mode: str, errors: list[str]) -> None:
    lock_path = (
        root / "harness/docs/rules/claude-frozen/RULES_LOCK.json"
        if mode == "private"
        else root / "05_governance/RULES_LOCK.json"
    )
    if not lock_path.is_file():
        errors.append("missing RULES_LOCK.json")
        return
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if lock.get("technical_review") != "PASS" or lock.get("agent_seal") != "SEALED" or lock.get("user_seal") != "SEALED":
        errors.append("seal state is not PASS/SEALED/SEALED")
    if lock.get("candidate_counts", {}).get("unaccounted") != 0:
        errors.append("candidate unaccounted is not zero")
    base = lock_path.parent
    for rel, expected in lock.get("files", {}).items():
        target = (base / rel).resolve()
        if not target.is_file():
            if mode == "private":
                errors.append(f"lock target missing: {rel}")
            continue
        if sha256(target) != expected.upper():
            errors.append(f"lock target hash mismatch: {rel}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("private", "public"), required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    manifest_name = "PRIVATE_MANIFEST.csv" if args.mode == "private" else "PUBLIC_MANIFEST.csv"
    errors: list[str] = []
    files = files_under(root)

    allowed_private_jsonl = "harness/docs/rules/claude-frozen/USER_SEAL_AUTHORIZATION.jsonl"
    large_files = 0
    secret_hits = 0
    restricted_extension_hits = 0
    raw_transcript_hits = 0
    public_path_hits = 0

    for path in files:
        rel = path.relative_to(root).as_posix()
        suffix = path.suffix.lower()
        if suffix in FORBIDDEN_EXTENSIONS or suffix == ".jsonl":
            allowed = args.mode == "private" and rel == allowed_private_jsonl
            if not allowed:
                restricted_extension_hits += 1
                errors.append(f"forbidden extension: {rel}")
        lowered_parts = {part.lower() for part in path.parts}
        if {"archive", "quarantine", "browser profile", "vmware", "license"} & lowered_parts:
            errors.append(f"forbidden path segment: {rel}")
        if "typescript" in path.name.lower() or path.name.upper().startswith("EXIT"):
            raw_transcript_hits += 1
            errors.append(f"raw transcript/EXIT artifact: {rel}")
        if path.stat().st_size > 95 * 1024 * 1024:
            large_files += 1
            errors.append(f"file exceeds 95 MiB: {rel}")
        data = path.read_bytes()
        for label, pattern in HIGH_CONFIDENCE_SECRETS.items():
            if pattern.search(data):
                secret_hits += 1
                errors.append(f"secret-shaped value ({label}): {rel}")
        # This validator necessarily contains the literal path/session patterns it detects.
        # Exempt only this exact source file from those two self-referential content checks;
        # extension, size, filename, secret, link, lock, and manifest checks still cover it.
        if args.mode == "public" and is_text_candidate(path) and path.resolve() != Path(__file__).resolve():
            text = data.decode("utf-8", errors="replace")
            if WINDOWS_PATH.search(text) or "/root/" in text or "D:\\LocalUserFolders" in text or "C:\\Users" in text:
                public_path_hits += 1
                errors.append(f"public absolute path: {rel}")
            if RAW_MESSAGE_ID.search(text) or "restricted://codex-session" in text:
                errors.append(f"public message/session identifier: {rel}")

    validate_links(root, errors)
    validate_lock(root, args.mode, errors)
    validate_manifest(root, manifest_name, errors)

    print(f"EXPORT_MODE={args.mode.upper()}")
    print(f"FILE_COUNT={len(files)}")
    print(f"LARGE_FILE_COUNT={large_files}")
    print(f"SECRET_HIT_COUNT={secret_hits}")
    print(f"RESTRICTED_EXTENSION_HIT_COUNT={restricted_extension_hits}")
    print(f"RAW_TRANSCRIPT_EXIT_HIT_COUNT={raw_transcript_hits}")
    print(f"PUBLIC_ABSOLUTE_PATH_FILE_COUNT={public_path_hits}")
    print(f"ERROR_COUNT={len(errors)}")
    for error in errors:
        print(f"ERROR: {error}")
    print("EXPORT_VALIDATION=" + ("PASS" if not errors else "FAIL"))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
