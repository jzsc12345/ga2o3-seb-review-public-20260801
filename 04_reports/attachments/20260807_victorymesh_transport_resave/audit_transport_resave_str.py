"""Offline audit for the one-time Victory Mesh transport-identity resave.

The audit reads two existing ASCII STR files.  It does not invoke a simulator.
GaN and ZnO are treated only as import transport identities; the physical
lineage remains the semantic region IDs and names from the frozen source STR.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


GA2O3_REGIONS = (1, 2, 3, 6, 7)
NIO_REGIONS = (9, 10)
UNCHANGED_REGIONS = (4, 5, 8, 11, 12, 13)


def read_str(path: Path):
    coords = {}
    triangles = defaultdict(list)
    materials = {}
    names = {}
    electrodes = {}
    doping = defaultdict(dict)
    doping_payload_lengths = defaultdict(Counter)
    labels = {}
    current_region = None
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
                materials[current_region] = int(parts[2])
            elif tag == "w" and current_region is not None:
                if len(parts) >= 4 and parts[1].isdigit():
                    names[current_region] = parts[2]
                    electrodes[current_region] = int(parts[3])
                elif len(parts) >= 2:
                    names[current_region] = parts[1]
            elif tag == "n" and len(parts) >= 8:
                # ATLAS ASCII STR: n node material region donor acceptor total net.
                # SAVE MODE=ATLAS may reorder records, so compare by node ID.
                region = int(parts[3])
                # The first two payload values are the frozen donor and
                # acceptor scalars.  The ATLAS-mode exporter may append or
                # reorder derived net/total fields, so those are audited as a
                # payload-layout observation rather than mislabelled doping.
                doping[region][int(parts[1])] = tuple(map(float, parts[4:6]))
                doping_payload_lengths[region][len(parts) - 4] += 1
            elif tag == "G" and len(parts) >= 3:
                labels[int(parts[1])] = " ".join(parts[2:]).strip('"')
            elif tag == "Q" and len(parts) >= 4 and parts[2] == "21":
                labels.setdefault(int(parts[1]), " ".join(parts[3:]).strip('"'))
    return {
        "coords": coords,
        "triangles": dict(triangles),
        "materials": materials,
        "names": names,
        "electrodes": electrodes,
        "doping": {region: dict(values) for region, values in doping.items()},
        "doping_payload_lengths": {
            region: dict(counts) for region, counts in doping_payload_lengths.items()
        },
        "labels": labels,
    }


def area(points):
    (x1, y1), (x2, y2), (x3, y3) = points
    return abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) / 2


def is_obtuse(points, tol=1e-14):
    for index in range(3):
        a = points[index]
        b = points[(index + 1) % 3]
        c = points[(index + 2) % 3]
        if (b[0] - a[0]) * (c[0] - a[0]) + (b[1] - a[1]) * (c[1] - a[1]) < -tol:
            return True
    return False


def vertical_interval(points, x0, tol=1e-12):
    ys = []
    for index in range(3):
        x1, y1 = points[index]
        x2, y2 = points[(index + 1) % 3]
        if abs(x1 - x0) <= tol:
            ys.append(y1)
        if abs(x2 - x0) <= tol:
            ys.append(y2)
        if (x1 < x0 < x2) or (x2 < x0 < x1):
            fraction = (x0 - x1) / (x2 - x1)
            ys.append(y1 + fraction * (y2 - y1))
    return None if len(ys) < 2 else (min(ys), max(ys))


def merge_intervals(intervals, ymin=0.0, ymax=0.6, tol=1e-10):
    items = sorted((max(a, ymin), min(b, ymax)) for a, b in intervals if b >= ymin and a <= ymax)
    if not items:
        return [], ymax - ymin
    merged = [list(items[0])]
    for start, end in items[1:]:
        if start <= merged[-1][1] + tol:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    gaps = [merged[0][0] - ymin, ymax - merged[-1][1]]
    gaps.extend(merged[i + 1][0] - merged[i][1] for i in range(len(merged) - 1))
    return merged, max(gaps)


def region_metrics(data, region):
    triangles = data["triangles"][region]
    points = [data["coords"][node] for tri in triangles for node in tri]
    return {
        "triangles": len(triangles),
        "area_um2": sum(area([data["coords"][node] for node in tri]) for tri in triangles),
        "xmin_um": min(p[0] for p in points),
        "xmax_um": max(p[0] for p in points),
        "ymin_um": min(p[1] for p in points),
        "ymax_um": max(p[1] for p in points),
    }


def roi_metrics(data, lineage_regions, xmin=10.10, xmax=10.40, ymin=0.0, ymax=0.6, xion=10.25):
    max_dx = 0.0
    max_dy = 0.0
    intervals = []
    obtuse = 0
    for region, triangles in data["triangles"].items():
        for triangle in triangles:
            points = [data["coords"][node] for node in triangle]
            obtuse += int(is_obtuse(points))
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            intersects = not (max(xs) < xmin or min(xs) > xmax or max(ys) < ymin or min(ys) > ymax)
            if intersects:
                max_dx = max(max_dx, max(xs) - min(xs))
                max_dy = max(max_dy, max(ys) - min(ys))
            if region in lineage_regions:
                interval = vertical_interval(points, xion)
                if interval is not None:
                    intervals.append(interval)
    merged, max_gap = merge_intervals(intervals, ymin, ymax)
    return {
        "max_dx_um": max_dx,
        "max_dy_um": max_dy,
        "full_y_continuity": max_gap <= 1e-10,
        "max_y_gap_um": max_gap,
        "merged_y_intervals": merged,
        "obtuse": obtuse,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    source = read_str(args.source)
    output = read_str(args.output)
    regions = sorted(source["triangles"])
    if regions != sorted(output["triangles"]):
        raise RuntimeError("runtime region IDs differ")

    coordinates_exact = source["coords"] == output["coords"]
    # SAVE MODE=ATLAS may reorder triangles and reverse their winding while
    # preserving the identical simplicial mesh.  Compare region-local triangle
    # node sets as multisets, not record order or orientation.
    source_topology = {
        region: Counter(tuple(sorted(triangle)) for triangle in triangles)
        for region, triangles in source["triangles"].items()
    }
    output_topology = {
        region: Counter(tuple(sorted(triangle)) for triangle in triangles)
        for region, triangles in output["triangles"].items()
    }
    connectivity_exact = source_topology == output_topology
    names_exact = source["names"] == output["names"]
    electrodes_exact = source["electrodes"] == output["electrodes"]
    doping_exact = source["doping"] == output["doping"]

    region_rows = []
    geometry_exact = True
    for region in regions:
        sm = region_metrics(source, region)
        om = region_metrics(output, region)
        metric_exact = all(
            math.isclose(sm[key], om[key], rel_tol=0.0, abs_tol=1e-12)
            for key in ("area_um2", "xmin_um", "xmax_um", "ymin_um", "ymax_um")
        ) and sm["triangles"] == om["triangles"]
        geometry_exact &= metric_exact
        source_code = source["materials"][region]
        output_code = output["materials"][region]
        region_rows.append(
            {
                "region_id": region,
                "semantic_name": source["names"].get(region, ""),
                "source_material_code": source_code,
                "source_material_label": source["labels"].get(source_code, ""),
                "output_material_code": output_code,
                "output_material_label": output["labels"].get(output_code, ""),
                "triangles": sm["triangles"],
                "source_area_um2": sm["area_um2"],
                "output_area_um2": om["area_um2"],
                "bbox_exact": all(sm[k] == om[k] for k in ("xmin_um", "xmax_um", "ymin_um", "ymax_um")),
                "geometry_metric_exact_1e-12": metric_exact,
                "doping_exact": source["doping"].get(region, []) == output["doping"].get(region, []),
                "electrode_id_source": source["electrodes"].get(region, ""),
                "electrode_id_output": output["electrodes"].get(region, ""),
            }
        )

    with (args.out_dir / "region_geometry_material_doping_comparison.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=list(region_rows[0]))
        writer.writeheader()
        writer.writerows(region_rows)

    dictionary_rows = []
    for origin, data in (("SOURCE", source), ("OUTPUT", output)):
        usage = Counter(data["materials"].values())
        for code in sorted(usage):
            dictionary_rows.append(
                {
                    "str": origin,
                    "material_code": code,
                    "material_label": data["labels"].get(code, ""),
                    "runtime_region_records": usage[code],
                    "region_ids": ";".join(str(r) for r in sorted(k for k, v in data["materials"].items() if v == code)),
                }
            )
    with (args.out_dir / "material_dictionary_and_region_table.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=list(dictionary_rows[0]))
        writer.writeheader()
        writer.writerows(dictionary_rows)

    source_roi = roi_metrics(source, set(GA2O3_REGIONS))
    output_roi = roi_metrics(output, set(GA2O3_REGIONS))
    mapping_exact = (
        all(source["materials"][r] == 50 and output["materials"][r] == 124 for r in GA2O3_REGIONS)
        and all(source["materials"][r] == 304 and output["materials"][r] == 209 for r in NIO_REGIONS)
        and all(source["materials"][r] == output["materials"][r] for r in UNCHANGED_REGIONS)
    )
    gate = next((row for row in region_rows if row["semantic_name"] == "gate"), None)
    thick_gate = bool(
        gate
        and gate["electrode_id_output"] == 3
        and gate["geometry_metric_exact_1e-12"]
        and math.isclose(gate["output_area_um2"], 0.235, rel_tol=0.0, abs_tol=1e-12)
    )
    summary = {
        "source_str": str(args.source),
        "output_str": str(args.output),
        "node_count_source": len(source["coords"]),
        "node_count_output": len(output["coords"]),
        "triangle_count_source": sum(map(len, source["triangles"].values())),
        "triangle_count_output": sum(map(len, output["triangles"].values())),
        "coordinates_exact": coordinates_exact,
        "triangle_connectivity_exact": connectivity_exact,
        "semantic_names_exact": names_exact,
        "geometry_area_bbox_exact_1e-12": geometry_exact,
        "interface_coordinates_exact_by_mesh_identity": coordinates_exact and connectivity_exact,
        "doping_arrays_exact": doping_exact,
        "doping_definition": "first two n-payload scalars: donor and acceptor",
        "doping_payload_lengths_source": source["doping_payload_lengths"],
        "doping_payload_lengths_output": output["doping_payload_lengths"],
        "derived_doping_payload_layout_changed": (
            source["doping_payload_lengths"] != output["doping_payload_lengths"]
        ),
        "electrodes_exact": electrodes_exact,
        "electrode_count": len(output["electrodes"]),
        "thick_stepped_gate_preserved": thick_gate,
        "gate_fp_present": any(name.lower() == "gate_fp" for name in output["names"].values()),
        "material_only_transformation_exact": mapping_exact,
        "output_gan_code": 124,
        "output_gan_label": output["labels"].get(124, ""),
        "output_zno_code": 209,
        "output_zno_label": output["labels"].get(209, ""),
        "ga2o3_runtime_records_after_resave": sum(code == 50 for code in output["materials"].values()),
        "nio_runtime_records_after_resave": sum(code == 304 for code in output["materials"].values()),
        "gan_runtime_records_after_resave": sum(code == 124 for code in output["materials"].values()),
        "zno_runtime_records_after_resave": sum(code == 209 for code in output["materials"].values()),
        "source_track_metrics": source_roi,
        "output_track_metrics_by_ga2o3_lineage_regions": output_roi,
        "sio2_unchanged": all(source["materials"][r] == output["materials"][r] == 1 for r in (4, 5)),
        "al2o3_unchanged": source["materials"][8] == output["materials"][8] == 229,
        "nickel_unchanged": all(source["materials"][r] == output["materials"][r] == 77 for r in (11, 12, 13)),
    }
    if not all(
        (
            len(source["coords"]) == len(output["coords"]) == 56454,
            summary["triangle_count_source"] == summary["triangle_count_output"] == 111350,
            source_roi["obtuse"] == output_roi["obtuse"] == 0,
            coordinates_exact,
            connectivity_exact,
            geometry_exact,
            doping_exact,
            electrodes_exact,
            mapping_exact,
            source_roi["full_y_continuity"],
            output_roi["full_y_continuity"],
        )
    ):
        raise RuntimeError("one or more frozen invariance gates failed")

    (args.out_dir / "transport_resave_invariance_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
