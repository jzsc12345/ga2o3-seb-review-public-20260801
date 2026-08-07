"""Read-only Victory Mesh STR contract analyzer for the 2026-08-07 one-shot mesh.

The script never invokes SSH or a simulator.  All spacing metrics are triangle
axis-aligned bounding-box extents, matching Victory Mesh conformal-minimal size
semantics.  P95 uses numpy's linear percentile definition.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from analyze_victorymesh_seb_str import (
    is_obtuse,
    merge_intervals,
    read_str,
    triangle_area,
    triangle_intersects_rect,
    vertical_intersection_interval,
)


MATERIAL = {1: "sio2", 50: "ga2o3", 51: "nio", 77: "nickel", 229: "al2o3", 304: "nio"}
TRACK_ROI = (10.10, 10.40, 0.00, 0.60)
XION = 10.25

WINDOWS = {
    "gate_drain_edge": (5.95, 6.05, -0.20, -0.12),
    "channel_region5": (0.975, 1.025, 0.000, 0.150),
    "channel_n_d": (13.975, 14.025, 0.000, 0.150),
    "substrate_uid": (6.50, 7.50, 0.375, 0.425),
    "uid_channel": (6.50, 7.50, 0.175, 0.225),
}

SEMICONDUCTOR_SEMANTICS = {"substrate", "uid", "channel", "region5", "n_d"}
WINDOW_SEMANTICS = {
    "track": SEMICONDUCTOR_SEMANTICS,
    "gate_drain_edge": None,
    "channel_region5": {"channel", "region5"},
    "channel_n_d": {"channel", "n_d"},
    "substrate_uid": {"substrate", "uid"},
    "uid_channel": {"uid", "channel"},
}


def semantic_name(region: int, name: str, material: int, bbox: tuple[float, float, float, float]) -> str:
    if name:
        return name.lower()
    xmin, xmax, ymin, ymax = bbox
    if material == 50 and math.isclose(xmin, 0.0) and math.isclose(xmax, 1.0) and math.isclose(ymin, 0.0) and math.isclose(ymax, 0.15):
        return "region5"
    return f"runtime_region_{region}"


def stats(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "min": None, "median": None, "p95": None, "max": None}
    data = np.asarray(values, dtype=float)
    return {
        "count": int(data.size),
        "min": float(np.min(data)),
        "median": float(np.median(data)),
        "p95": float(np.percentile(data, 95, method="linear")),
        "max": float(np.max(data)),
    }


def edge_key(a: tuple[float, float], b: tuple[float, float]) -> tuple[tuple[float, float], tuple[float, float]]:
    p = (round(a[0], 12), round(a[1], 12))
    q = (round(b[0], 12), round(b[1], 12))
    return (p, q) if p <= q else (q, p)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--str", dest="str_path", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--case", required=True)
    args = ap.parse_args()

    coords, triangles, region_material, region_names, electrode_ids, node_doping, material_labels = read_str(args.str_path)
    if not coords or not triangles:
        raise RuntimeError("STR contains no usable coordinates or triangles")
    # DevEdit raw STR writes electrodes as ``w name workfunc electrode_id``;
    # remeshed Atlas-mode STR writes a different w-record layout.  Preserve
    # the shared reader behavior and supplement only the raw layout here.
    current_region = None
    with args.str_path.open("r", encoding="utf-8", errors="replace") as stream:
        for line in stream:
            parts = line.split()
            if not parts:
                continue
            if parts[0] == "r" and len(parts) >= 3:
                current_region = int(parts[1])
            elif parts[0] == "w" and current_region is not None and len(parts) >= 4 and not parts[1].isdigit():
                region_names[current_region] = parts[1]
                electrode_ids[current_region] = int(parts[3])
    args.out_dir.mkdir(parents=True, exist_ok=True)

    tri_rows: list[dict] = []
    region_rows: list[dict] = []
    edge_owners: dict[tuple, list[tuple[int, int]]] = defaultdict(list)
    semantic_by_region: dict[int, str] = {}
    obtuse_triangles = 0

    for region in sorted(triangles):
        used_nodes = {node for item in triangles[region] for node in item}
        xs = [coords[node][0] for node in used_nodes]
        ys = [coords[node][1] for node in used_nodes]
        bbox = (min(xs), max(xs), min(ys), max(ys))
        sem = semantic_name(region, region_names.get(region, ""), region_material.get(region, -1), bbox)
        semantic_by_region[region] = sem
        region_area = 0.0
        for tri_index, node_ids in enumerate(triangles[region], start=1):
            points = [coords[node] for node in node_ids]
            tx = [p[0] for p in points]
            ty = [p[1] for p in points]
            region_area += triangle_area(points)
            row = {
                "region_id": region,
                "semantic_name": sem,
                "material": MATERIAL.get(region_material.get(region), str(region_material.get(region))),
                "triangle_index": tri_index,
                "xmin": min(tx), "xmax": max(tx), "ymin": min(ty), "ymax": max(ty),
                "dx": max(tx) - min(tx), "dy": max(ty) - min(ty),
                "node_ids": node_ids,
                "points": points,
            }
            obtuse_triangles += int(is_obtuse(points))
            tri_rows.append(row)
            for i in range(3):
                edge_owners[edge_key(points[i], points[(i + 1) % 3])].append((region, len(tri_rows) - 1))
        donor = [v[0] for v in node_doping.get(region, [])]
        acceptor = [v[1] for v in node_doping.get(region, [])]
        region_rows.append({
            "region_id": region,
            "semantic_name": sem,
            "material": MATERIAL.get(region_material.get(region), str(region_material.get(region))),
            "electrode_id": electrode_ids.get(region, ""),
            "triangles": len(triangles[region]),
            "area_um2": region_area,
            "xmin": bbox[0], "xmax": bbox[1], "ymin": bbox[2], "ymax": bbox[3],
            "donor_min": min(donor) if donor else "", "donor_max": max(donor) if donor else "",
            "acceptor_min": min(acceptor) if acceptor else "", "acceptor_max": max(acceptor) if acceptor else "",
        })

    def rows_in_rect(rect: tuple[float, float, float, float], semantics: set[str] | None = None) -> list[dict]:
        xmin, xmax, ymin, ymax = rect
        selected = []
        for row in tri_rows:
            if semantics is not None and row["semantic_name"] not in semantics:
                continue
            if triangle_intersects_rect(row["points"], xmin, xmax, ymin, ymax):
                selected.append(row)
        return selected

    metric_rows: list[dict] = []
    for label, rect in {"track": TRACK_ROI, **WINDOWS}.items():
        # Boundary windows are evaluated only on the two semantic regions
        # that form the named boundary.  This prevents a dielectric triangle
        # touching the closed y=0 boundary from contaminating a semiconductor
        # spacing gate.  The strike ROI likewise uses semiconductor triangles
        # only, matching the full-y continuity population.
        selected = rows_in_rect(rect, WINDOW_SEMANTICS[label])
        dxs, dys = [r["dx"] for r in selected], [r["dy"] for r in selected]
        sx, sy = stats(dxs), stats(dys)
        metric_rows.append({
            "metric": label, "xmin": rect[0], "xmax": rect[1], "ymin": rect[2], "ymax": rect[3],
            "triangles": len(selected),
            "dx_min": sx["min"], "dx_median": sx["median"], "dx_p95": sx["p95"], "dx_max": sx["max"],
            "dy_min": sy["min"], "dy_median": sy["median"], "dy_p95": sy["p95"], "dy_max": sy["max"],
        })

    # Exact full-y coverage by semiconductor triangles at xion.
    intervals = []
    for row in tri_rows:
        if row["material"] != "ga2o3":
            continue
        interval = vertical_intersection_interval(row["points"], XION)
        if interval is not None:
            intervals.append(interval)
    merged, max_gap = merge_intervals(intervals, TRACK_ROI[2], TRACK_ROI[3])

    # Finite-length shared interfaces and adjacent triangle AABB metrics.
    interface_groups: dict[tuple[str, str, str], dict] = defaultdict(lambda: {"length": 0.0, "dx": [], "dy": [], "edges": 0})
    semantic_groups: dict[tuple[str, str, str], dict] = defaultdict(lambda: {"length": 0.0, "dx": [], "dy": [], "edges": 0})
    for (a, b), owners in edge_owners.items():
        distinct = sorted({region for region, _ in owners})
        if len(distinct) != 2:
            continue
        ra, rb = distinct
        length = math.dist(a, b)
        if length <= 1e-12:
            continue
        dx_edge, dy_edge = abs(a[0] - b[0]), abs(a[1] - b[1])
        orientation = "horizontal" if dy_edge <= 1e-10 else "vertical" if dx_edge <= 1e-10 else "diagonal"
        owner_rows = [tri_rows[idx] for region, idx in owners if region in (ra, rb)]
        ma, mb = MATERIAL.get(region_material[ra], str(region_material[ra])), MATERIAL.get(region_material[rb], str(region_material[rb]))
        mat_key = tuple(sorted((ma, mb))) + (orientation,)
        sem_key = tuple(sorted((semantic_by_region[ra], semantic_by_region[rb]))) + (orientation,)
        for groups, key in ((interface_groups, mat_key), (semantic_groups, sem_key)):
            groups[key]["length"] += length
            groups[key]["edges"] += 1
            groups[key]["dx"].extend(row["dx"] for row in owner_rows)
            groups[key]["dy"].extend(row["dy"] for row in owner_rows)

    interface_rows = []
    for (left, right, orientation), data in sorted(interface_groups.items()):
        sx, sy = stats(data["dx"]), stats(data["dy"])
        normal_axis = "y" if orientation == "horizontal" else "x" if orientation == "vertical" else "mixed"
        normal_max = sy["max"] if normal_axis == "y" else sx["max"] if normal_axis == "x" else None
        interface_rows.append({
            "material_a": left, "material_b": right, "orientation": orientation,
            "finite_length_um": data["length"], "shared_edges": data["edges"], "normal_axis": normal_axis,
            "dx_max": sx["max"], "dy_max": sy["max"], "normal_max": normal_max,
        })

    semantic_rows = []
    for (left, right, orientation), data in sorted(semantic_groups.items()):
        sx, sy = stats(data["dx"]), stats(data["dy"])
        semantic_rows.append({
            "semantic_a": left, "semantic_b": right, "orientation": orientation,
            "finite_length_um": data["length"], "shared_edges": data["edges"],
            "dx_max": sx["max"], "dy_max": sy["max"],
        })

    def vertical_layer_metrics(name: str, xmin: float, xmax: float, ymin: float, ymax: float, samples: list[float]) -> dict:
        selected = rows_in_rect((xmin, xmax, ymin, ymax), {name})
        dy = stats([row["dy"] for row in selected])
        counts = []
        for x in samples:
            ys = {round(ymin, 12), round(ymax, 12)}
            for row in selected:
                interval = vertical_intersection_interval(row["points"], x)
                if interval is not None:
                    ys.add(round(max(ymin, interval[0]), 12))
                    ys.add(round(min(ymax, interval[1]), 12))
            ordered = sorted(y for y in ys if ymin - 1e-10 <= y <= ymax + 1e-10)
            counts.append(max(0, len(ordered) - 1))
        return {
            "layer": name, "thickness_um": ymax - ymin, "sample_x": ";".join(map(str, samples)),
            "min_intervals": min(counts) if counts else 0, "interval_counts": ";".join(map(str, counts)),
            "normal_dy_max": dy["max"],
        }

    layer_rows = [
        vertical_layer_metrics("barrier", 0.5, 14.5, -0.02, 0.0, [0.75, 1.25, 1.75, 3.0, 5.0, 10.25, 14.25]),
        vertical_layer_metrics("p-", 2.0, 4.0, -0.07, -0.02, [2.1, 3.0, 3.9]),
        vertical_layer_metrics("p+", 2.0, 4.0, -0.12, -0.07, [2.1, 3.0, 3.9]),
    ]

    def semantic_connected_components(name: str) -> int:
        """Count finite-area mesh components, independent of STR record splitting.

        A raw DevEdit STR can serialize two disconnected polygons under one
        runtime region record, while an Atlas-mode Victory STR can serialize
        the same polygons as two records.  Shared triangle edges therefore
        define the comparable topology; record count does not.
        """

        selected = {index for index, row in enumerate(tri_rows) if row["semantic_name"] == name}
        if not selected:
            return 0
        parent = {index: index for index in selected}

        def find(index: int) -> int:
            while parent[index] != index:
                parent[index] = parent[parent[index]]
                index = parent[index]
            return index

        def union(left: int, right: int) -> None:
            root_left, root_right = find(left), find(right)
            if root_left != root_right:
                parent[root_right] = root_left

        for owners in edge_owners.values():
            adjacent = sorted({index for _, index in owners if index in selected})
            for left, right in zip(adjacent, adjacent[1:]):
                union(left, right)
        return len({find(index) for index in selected})

    semantic_keys = {row["semantic_name"] for row in region_rows}
    summary = {
        "case": args.case,
        "str": str(args.str_path),
        "points": len(coords),
        "triangles": sum(len(v) for v in triangles.values()),
        "obtuse_triangles_computed": obtuse_triangles,
        "runtime_region_records": len(region_rows),
        "semantic_region_count": len(semantic_keys),
        "oxide_connected_components": semantic_connected_components("oxide"),
        "electrode_count": sum(1 for r in region_rows if r["electrode_id"] != ""),
        "electrode_names": [r["semantic_name"] for r in region_rows if r["electrode_id"] != ""],
        "track": next(r for r in metric_rows if r["metric"] == "track"),
        "full_y_continuity": max_gap <= 1e-10,
        "max_y_gap_um": max_gap,
        "merged_y_intervals": merged,
        "intervals_per_radius_from_track_max": 0.05 / max(next(r for r in metric_rows if r["metric"] == "track")["dx_max"], next(r for r in metric_rows if r["metric"] == "track")["dy_max"]),
        "intervals_per_diameter_from_track_max": 0.10 / max(next(r for r in metric_rows if r["metric"] == "track")["dx_max"], next(r for r in metric_rows if r["metric"] == "track")["dy_max"]),
    }

    prefix = args.out_dir / args.case
    write_csv(prefix.with_name(prefix.name + "_regions.csv"), region_rows)
    write_csv(prefix.with_name(prefix.name + "_roi_metrics.csv"), metric_rows)
    write_csv(prefix.with_name(prefix.name + "_material_interfaces.csv"), interface_rows)
    write_csv(prefix.with_name(prefix.name + "_semantic_interfaces.csv"), semantic_rows)
    write_csv(prefix.with_name(prefix.name + "_thin_layers.csv"), layer_rows)
    prefix.with_name(prefix.name + "_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
