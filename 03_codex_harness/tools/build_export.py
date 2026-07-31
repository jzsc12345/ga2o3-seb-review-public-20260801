from __future__ import annotations

import csv
import hashlib
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import zipfile


WORKSPACE = Path(__file__).resolve().parents[2]
HARNESS = WORKSPACE / "harness"
COMMIT = "540379dab74fdda861f688204b4d45ec5f59a9d2"
ALLOWED = {".md", ".py", ".mjs", ".in", ".c", ".sh", ".csv", ".png", ".json", ".txt", ".sdb", ".pl", ".pptx"}
ROOT_ALLOW = {".gitignore", "AGENTS.md", "INSTALL.md", "PREFLIGHT.md", "README.md", "SEB.in", "mySEU.c"}
TREE_ALLOW = {"skills", "claude-sentaurus-skill-main", "decks", "docs", "knowledge", "scripts"}
RUN_DIRS = [
    "RUN053_lgd14-subfe-wf578-idvg",
    "RUN082_wang-static-et",
    "RUN094_wang1000-nofp-lgd9-x11-reference",
    "RUN095_wang1000-nofp-lgd9-x11-heatfull",
    "RUN096_wang1000-nofp-lgd9-x11-hfo2hc",
    "RUN102_wang1000-nofp-lgd9-x11-bandt-rafique",
    "RUN103_wang1000-nofp-lgd9-x11-mobt-ma18",
    "RUN108_ndsub1p15e16-seb1000",
    "RUN109_ndsub5e15-seb1000",
    "RUN118_wang1000-fvsatt-short500ns",
    "RUN119_wang1000-uidnd1e16-short500ns",
]
REPORT_DIRS = [
    "RUN096_108_109_ndsub_path_overlay_20260731",
    "RUN096_109_2d_topology_20260731",
    "RUN096_118_fvsatn_topology_20260731",
    "RUN104_107_vds_ndsub_adjudication_20260731",
]
DECK_PREFIXES = ("RUN053_", "RUN082_", "RUN094_", "RUN095_", "RUN096_", "RUN102_", "RUN103_", "RUN108_", "RUN109_", "RUN118_", "RUN119_")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def git_paths() -> list[str]:
    return subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", COMMIT], cwd=WORKSPACE, text=True, encoding="utf-8"
    ).splitlines()


def write_git_object(rel: str, target: Path) -> None:
    data = subprocess.check_output(["git", "show", f"{COMMIT}:{rel}"], cwd=WORKSPACE)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def allowed(path: Path) -> bool:
    return path.name == ".gitignore" or path.suffix.lower() in ALLOWED


def copy_file(source: Path, target: Path) -> None:
    if not source.is_file() or not allowed(source):
        return
    if source.stat().st_size > 25 * 1024 * 1024:
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def copy_tree(source: Path, target: Path) -> None:
    if not source.exists():
        return
    for path in source.rglob("*"):
        if path.is_file() and allowed(path):
            copy_file(path, target / path.relative_to(source))


def build(destination: Path) -> tuple[Path, Path]:
    if destination.exists():
        raise SystemExit(f"refusing to overwrite existing destination: {destination}")
    destination.mkdir(parents=True)
    precut = destination / "01_claude_pre_cutoff"
    light = destination / "02_lightweight_project"
    harness_out = destination / "03_codex_harness"
    reports_out = destination / "04_reports"

    for rel in git_paths():
        pure = PurePosixPath(rel)
        top = pure.parts[0]
        if rel in ROOT_ALLOW or top in TREE_ALLOW:
            if top == "decks" and len(pure.parts) > 1 and pure.parts[1] == "ref_examples_aux_set":
                continue
            if Path(rel).name != ".gitignore" and Path(rel).suffix.lower() not in ALLOWED:
                continue
            write_git_object(rel, precut.joinpath(*pure.parts))

    readable_chat = WORKSPACE / "outputs" / "claude_chat_restore_20260727" / "claude_terminal_readable.md"
    if readable_chat.exists():
        copy_file(readable_chat, precut / "history" / readable_chat.name)
    raw_chat = Path(r"C:\Users\Administrator\.claude\projects\d--SILVACO-LOCAL\c1c5b402-2126-47ff-b212-2eb49e23375e.jsonl")
    if raw_chat.exists():
        (precut / "history").mkdir(parents=True, exist_ok=True)
        (precut / "history" / "RAW_SESSION_SHA256.txt").write_text(
            f"path={raw_chat}\nsha256={sha256(raw_chat)}\nsize={raw_chat.stat().st_size}\n"
            "raw JSONL deliberately excluded from GitHub package; readable transcript is included.\n",
            encoding="utf-8",
        )

    for run in RUN_DIRS:
        source = WORKSPACE / "outputs" / "runs" / run
        copy_tree(source, light / "outputs" / "runs" / run)
    for report in REPORT_DIRS:
        source = WORKSPACE / "outputs" / "reports" / report
        copy_tree(source, light / "outputs" / "reports" / report)
    for path in (WORKSPACE / "decks").glob("*"):
        if path.is_file() and path.name.startswith(DECK_PREFIXES):
            copy_file(path, light / "decks" / path.name)

    copy_tree(HARNESS, harness_out)

    report_md = HARNESS / "docs" / "research-results" / "Ga2O3_SEB_有效进展与拟合审计_20260801.md"
    paper_md = HARNESS / "docs" / "research-results" / "小论文图表补充清单_20260801.md"
    pptx = WORKSPACE / "outputs" / "reports" / "导师汇报_Ga2O3_SEB拟合进展_20260801.pptx"
    for source in (report_md, paper_md, pptx):
        if source.exists():
            copy_file(source, reports_out / source.name)

    readme = destination / "README.md"
    readme.write_text(
        "# Ga2O3 SEB audit package\n\n"
        f"- cutoff: 2026-07-27 09:20:00 +08:00\n- pre-cutoff git anchor: `{COMMIT}`\n"
        "- `01_claude_pre_cutoff`: bytes read from the git object, not the current worktree.\n"
        "- `02_lightweight_project`: selected RUN decks, CSV and PNG only; no STR/LOG/PDF.\n"
        "- `03_codex_harness`: post-cutoff isolation, plans and checks.\n"
        "- `04_reports`: advisor report and paper figure-gap list.\n\n"
        "The pre-cutoff snapshot is an auditable time boundary, not a claim that every byte has a single author.\n",
        encoding="utf-8",
    )

    rows = []
    for path in sorted(destination.rglob("*")):
        if path.is_file():
            rows.append({"path": path.relative_to(destination).as_posix(), "size_bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = destination / "PACKAGE_MANIFEST.csv"
    with manifest.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "size_bytes", "sha256"])
        writer.writeheader()
        writer.writerows(rows)

    zip_path = destination.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(destination.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(destination.parent))
    return manifest, zip_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python build_export.py <new-destination-directory>")
    manifest_path, zip_file = build(Path(sys.argv[1]).resolve())
    print(f"MANIFEST={manifest_path}")
    print(f"ZIP={zip_file}")
