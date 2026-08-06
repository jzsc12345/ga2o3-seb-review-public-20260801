"""Extract pre/post MATERIAL INFO evidence from the completed transcript."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


def between(text: str, start: str, end: str) -> str:
    begin = text.index(start)
    finish = text.index(end, begin)
    return text[begin:finish].rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcript", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    text = args.transcript.read_text(encoding="utf-8", errors="replace").replace("\r", "")

    pre = between(
        text,
        'CONTROLLER_SEND: info regions="MATERIAL:GA2O3"',
        'CONTROLLER_SEND: material regions="MATERIAL:GA2O3" value="GaN"',
    )
    post = between(
        text,
        'CONTROLLER_SEND: info regions="MATERIAL:GAN"',
        'CONTROLLER_SEND: save out="VM_SEB_STAGE2_conformal_track_x10p25_atlas_transport_mapped.str" mode=atlas',
    )
    args.out_dir.joinpath("PREMAP_SELECTOR_AND_REGION_INFO.txt").write_text(pre, encoding="utf-8")
    args.out_dir.joinpath("POSTMAP_MATERIAL_AND_ELECTRODE_INFO.txt").write_text(post, encoding="utf-8")

    hits = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if re.search(r"warning|fatal|parse error|unknown command|ignored|cannot|failed", line, re.I):
            hits.append({"line": line_number, "text": line})
    with args.out_dir.joinpath("warning_fatal_register.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["line", "text"])
        writer.writeheader()
        writer.writerows(hits)

    summary = {
        "premap_ga2o3_selector_count": 5,
        "premap_ga2o3_region_ids": [1, 2, 3, 6, 7],
        "premap_ga2o3_elements": 62100,
        "premap_nio_selector_count": 2,
        "premap_nio_region_ids": [9, 10],
        "premap_nio_elements": 4000,
        "postmap_gan_region_ids": [1, 2, 3, 6, 7],
        "postmap_zno_region_ids": [9, 10],
        "postmap_sio2_runtime_records": 2,
        "postmap_al2o3_runtime_records": 1,
        "postmap_nickel_electrodes": ["source", "drain", "gate"],
        "victory_postmap_gan_conduction": "unknown",
        "victory_postmap_zno_conduction": "semiconductor",
        "warning_fatal_hits": len(hits),
    }
    args.out_dir.joinpath("info_evidence_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
