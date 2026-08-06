"""Measure actual Victory Mesh ASCII STR geometry and track-grid metrics.

This is a read-only postprocessor for an existing STR.  It does not invoke
DevEdit, Victory Mesh, ATLAS, or any other simulator.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


def read_str(path: Path):
    coords: dict[int, tuple[float, float]] = {}
    triangles: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
    region_material: dict[int, int] = {}
    region_names: dict[int, str] = {}
    electrode_ids: dict[int, int] = {}
    node_doping: dict[int, list[tuple[float, float]]] = defaultdict(list)
    material_labels: dict[int, str] = {}
    current_region: int | None = None

    with path.open("r", encoding="utf-8", errors="replace") as stream:
        for line in stream:
            parts = line.split()
            if not parts:
                continue
            tag = parts[0]
            if tag == "c" and len(parts) >= 4:
                coords[int(parts[1])] = (float(parts[2]), float(parts[3]))
            elif tag == "t" and len(parts) >= 6:
                triangles[int(parts[2])].append(tuple(map(int, parts[3:6])))
            elif tag == "r" and len(parts) >= 3:
                current_region = int(parts[1])
                region_material[current_region] = int(parts[2])
            elif tag == "w" and current_region is not None:
                if len(parts) >= 4 and parts[1].isdigit():
                    region_names[current_region] = parts[2]
                    electrode_ids[current_region] = int(parts[3])
                elif len(parts) >= 2:
                    region_names[current_region] = parts[1]
            elif tag == "n" and len(parts) >= 8:
                # ATLAS ASCII STR: n node material region donor acceptor total net
                node_doping[int(parts[3])].append((float(parts[4]), float(parts[5])))
            elif tag == "G" and len(parts) >= 3:
                material_labels[int(parts[1])] = parts[2].strip('"')
            elif tag == "Q" and len(parts) >= 4 and parts[2] == "21":
                material_labels.setdefault(int(parts[1]), " ".join(parts[3:]).strip('"'))

    return coords, triangles, region_material, region_names, electrode_ids, node_doping, material_labels


def triangle_area(points: list[tuple[float, float]]) -> float:
    (x1, y1), (x2, y2), (x3, y3) = points
    return abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) / 2.0


def is_obtuse(points: list[tuple[float, float]], tol: float = 1e-14) -> bool:
    for i in range(3):
        ax, ay = points[(i + 1) % 3][0] - points[i][0], points[(i + 1) % 3][1] - points[i][1]
        bx, by = points[(i + 2) % 3][0] - points[i][0], points[(i + 2) % 3][1] - points[i][1]
        if ax * bx + ay * by < -tol:
            return True
    return False


def point_in_rect(point, xmin, xmax, ymin, ymax, tol=1e-12):
    x, y = point
    return xmin - tol <= x <= xmax + tol and ymin - tol <= y <= ymax + tol


def orient(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def on_segment(a, b, p, tol=1e-12):
    return (
        abs(orient(a, b, p)) <= tol
        and min(a[0], b[0]) - tol <= p[0] <= max(a[0], b[0]) + tol
        and min(a[1], b[1]) - tol <= p[1] <= max(a[1], b[1]) + tol
    )


def segments_intersect(a, b, c, d, tol=1e-12):
    o1, o2, o3, o4 = orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b)
    if ((o1 > tol and o2 < -tol) or (o1 < -tol and o2 > tol)) and (
        (o3 > tol and o4 < -tol) or (o3 < -tol and o4 > tol)
    ):
        return True
    return any(
        (
            abs(o1) <= tol and on_segment(a, b, c),
            abs(o2) <= tol and on_segment(a, b, d),
            abs(o3) <= tol and on_segment(c, d, a),
            abs(o4) <= tol and on_segment(c, d, b),
        )
    )


def point_in_triangle(p, tri, tol=1e-12):
    values = [orient(tri[i], tri[(i + 1) % 3], p) for i in range(3)]
    return not (any(v > tol for v in values) and any(v < -tol for v in values))


def triangle_intersects_rect(tri, xmin, xmax, ymin, ymax):
    if any(point_in_rect(p, xmin, xmax, ymin, ymax) for p in tri):
        return True
    corners = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
    if any(point_in_triangle(p, tri) for p in corners):
        return True
    tri_edges = [(tri[i], tri[(i + 1) % 3]) for i in range(3)]
    rect_edges = [(corners[i], corners[(i + 1) % 4]) for i in range(4)]
    return any(segments_intersect(a, b, c, d) for a, b in tri_edges for c, d in rect_edges)


def vertical_intersection_interval(tri, x0, tol=1e-12):
    ys: list[float] = []
    for i in range(3):
        x1, y1 = tri[i]
        x2, y2 = tri[(i + 1) % 3]
        if abs(x1 - x0) <= tol:
            ys.append(y1)
        if abs(x2 - x0) <= tol:
            ys.append(y2)
        if (x1 < x0 < x2) or (x2 < x0 < x1):
            t = (x0 - x1) / (x2 - x1)
            ys.append(y1 + t * (y2 - y1))
    if len(ys) < 2:
        return None
    return min(ys), max(ys)


def merge_intervals(intervals, ymin, ymax, tol=1e-10):
    clipped = sorted((max(a, ymin), min(b, ymax)) for a, b in intervals if b >= ymin and a <= ymax)
    if not clipped:
        return [], ymax - ymin
    merged = [list(clipped[0])]
    for start, end in clipped[1:]:
        if start <= merged[-1][1] + tol:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    gaps = [max(0.0, merged[0][0] - ymin), max(0.0, ymax - merged[-1][1])]
    gaps.extend(max(0.0, merged[i + 1][0] - merged[i][1]) for i in range(len(merged) - 1))
    return merged, max(gaps)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--str", dest="str_path", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--case", required=True)
    parser.add_argument("--roi", nargs=4, type=float, metavar=("XMIN", "XMAX", "YMIN", "YMAX"), required=True)
    parser.add_argument("--xion", type=float, required=True)
    args = parser.parse_args()

    xmin, xmax, ymin, ymax = args.roi
    coords, triangles, materials, names, electrode_ids, node_doping, material_labels = read_str(args.str_path)
    if not coords or not triangles:
        raise RuntimeError("STR contains no usable coordinates or triangles")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    roi_rows = []
    region_rows = []
    obtuse = 0
    track_intervals = []

    for region in sorted(triangles):
        region_points = []
        region_area = 0.0
        region_triangles = triangles[region]
        for index, node_ids in enumerate(region_triangles, start=1):
            tri = [coords[node] for node in node_ids]
            region_points.extend(tri)
            region_area += triangle_area(tri)
            obtuse += int(is_obtuse(tri))
            if triangle_intersects_rect(tri, xmin, xmax, ymin, ymax):
                xs = [p[0] for p in tri]
                ys = [p[1] for p in tri]
                roi_rows.append(
                    {
                        "region_id": region,
                        "region_name": names.get(region, ""),
                        "material_code": materials.get(region, ""),
                        "triangle_index": index,
                        "xmin_um": min(xs),
                        "xmax_um": max(xs),
                        "ymin_um": min(ys),
                        "ymax_um": max(ys),
                        "dx_um": max(xs) - min(xs),
                        "dy_um": max(ys) - min(ys),
                    }
                )
            if materials.get(region) == 50:
                interval = vertical_intersection_interval(tri, args.xion)
                if interval is not None:
                    track_intervals.append(interval)

        xs = [p[0] for p in region_points]
        ys = [p[1] for p in region_points]
        region_rows.append(
            {
                "region_id": region,
                "semantic_name": names.get(region, ""),
                "material_code": materials.get(region, ""),
                "material_label_in_str": material_labels.get(materials.get(region, -1), ""),
                "electrode_id": electrode_ids.get(region, ""),
                "triangles": len(region_triangles),
                "area_um2": region_area,
                "xmin_um": min(xs),
                "xmax_um": max(xs),
                "ymin_um": min(ys),
                "ymax_um": max(ys),
                "donor_min_cm3": min((item[0] for item in node_doping.get(region, [])), default=""),
                "donor_max_cm3": max((item[0] for item in node_doping.get(region, [])), default=""),
                "acceptor_min_cm3": min((item[1] for item in node_doping.get(region, [])), default=""),
                "acceptor_max_cm3": max((item[1] for item in node_doping.get(region, [])), default=""),
            }
        )

    merged, max_gap = merge_intervals(track_intervals, ymin, ymax)
    max_dx = max(row["dx_um"] for row in roi_rows)
    max_dy = max(row["dy_um"] for row in roi_rows)
    semantic_keys = {row["semantic_name"] or f"region_{row['region_id']}" for row in region_rows}
    electrode_count = sum(bool(row["electrode_id"] != "") for row in region_rows)
    gate = next((row for row in region_rows if row["semantic_name"] == "gate"), None)
    thick_gate_preserved = bool(
        gate
        and math.isclose(gate["xmin_um"], 1.5, abs_tol=1e-10)
        and math.isclose(gate["xmax_um"], 6.0, abs_tol=1e-10)
        and math.isclose(gate["ymin_um"], -0.2, abs_tol=1e-10)
        and math.isclose(gate["ymax_um"], -0.12, abs_tol=1e-10)
        and math.isclose(gate["area_um2"], 0.235, rel_tol=1e-8, abs_tol=1e-10)
    )

    roi_csv = args.out_dir / f"{args.case}_roi_triangles.csv"
    with roi_csv.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(roi_rows[0]))
        writer.writeheader()
        writer.writerows(roi_rows)

    regions_csv = args.out_dir / f"{args.case}_regions.csv"
    with regions_csv.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(region_rows[0]))
        writer.writeheader()
        writer.writerows(region_rows)

    summary = {
        "case": args.case,
        "str": str(args.str_path),
        "points": len(coords),
        "triangles": sum(len(items) for items in triangles.values()),
        "obtuse_triangles_computed": obtuse,
        "runtime_region_records": len(region_rows),
        "semantic_region_count": len(semantic_keys),
        "electrode_count": electrode_count,
        "thick_gate_preserved": thick_gate_preserved,
        "roi": {"xmin_um": xmin, "xmax_um": xmax, "ymin_um": ymin, "ymax_um": ymax},
        "roi_intersecting_triangles": len(roi_rows),
        "track_max_dx_um": max_dx,
        "track_max_dy_um": max_dy,
        "xion_um": args.xion,
        "full_y_continuity": max_gap <= 1e-10,
        "max_y_gap_um": max_gap,
        "merged_y_intervals": merged,
    }
    summary_path = args.out_dir / f"{args.case}_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
