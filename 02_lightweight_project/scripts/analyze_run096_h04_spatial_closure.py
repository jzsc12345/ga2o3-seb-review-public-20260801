#!/usr/bin/env python3
"""Build shared-scale RUN096 spatial maps from frozen VictoryExtract CSVs.

This is post-processing only.  It never starts ATLAS or VictoryExtract.  The
electron/current fields come from the existing RUN096 topology archive; Joule
heat and ionized Fe come from ANALYSIS096-H04.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import Normalize


TIMES = ("t50ns", "t100ns", "t500ns")
TIME_LABEL = {"t50ns": "50 ns", "t100ns": "100 ns", "t500ns": "500 ns"}
ZONES = ("shallow", "substrate")
FIELDS = (
    ("electron", "Electron concentration", r"log$_{10}$(n / cm$^{-3}$)", "viridis"),
    ("je", "Electron current magnitude", r"log$_{10}$(|J$_e$| / A cm$^{-2}$)", "magma"),
    ("joule", "Joule heat power", r"log$_{10}$(|J·E| / W cm$^{-3}$)", "inferno"),
    ("fe", "Ionized Fe acceptor", r"log$_{10}$(N$_{Fe^-}$ / cm$^{-3}$)", "cividis"),
)


@dataclass
class Grid:
    x: np.ndarray
    y: np.ndarray
    values: dict[str, np.ndarray]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RUN096 H04 shared-scale spatial closure")
    parser.add_argument("--topology-dir", required=True, type=Path)
    parser.add_argument("--thermal-dir", required=True, type=Path)
    parser.add_argument("--path-metrics", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    return parser.parse_args()


def read_frame(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, skipinitialspace=True)
    frame.columns = [str(name).strip().strip('"') for name in frame.columns]
    frame = frame.sort_values(["y", "x"], kind="stable").reset_index(drop=True)
    return frame


def reshape(frame: pd.DataFrame, name: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x = np.sort(frame["x"].astype(float).unique())
    y = np.sort(frame["y"].astype(float).unique())
    if len(frame) != len(x) * len(y):
        raise ValueError(
            f"incomplete regular grid for {name}: rows={len(frame)}, nx={len(x)}, ny={len(y)}"
        )
    values = np.nan_to_num(frame[name].to_numpy(float), nan=0.0, posinf=0.0, neginf=0.0)
    return x, y, values.reshape(len(y), len(x))


def load_grid(topology: Path, thermal: Path) -> Grid:
    top = read_frame(topology)
    therm = read_frame(thermal)
    required_top = {"x", "y", "electron conc", "je- x", "je- y"}
    required_therm = {
        "x",
        "y",
        "joule heat power",
        "acceptor trap dos #1",
        "acceptor trap ionized density #1",
    }
    if missing := required_top - set(top.columns):
        raise ValueError(f"{topology}: missing {sorted(missing)}")
    if missing := required_therm - set(therm.columns):
        raise ValueError(f"{thermal}: missing {sorted(missing)}")

    tx, ty, electron = reshape(top, "electron conc")
    _, _, jx = reshape(top, "je- x")
    _, _, jy = reshape(top, "je- y")
    hx, hy, joule = reshape(therm, "joule heat power")
    _, _, fe = reshape(therm, "acceptor trap ionized density #1")
    _, _, fe_dos = reshape(therm, "acceptor trap dos #1")
    if not (np.array_equal(tx, hx) and np.array_equal(ty, hy)):
        raise ValueError(f"coordinate mismatch: {topology.name} vs {thermal.name}")

    return Grid(
        tx,
        ty,
        {
            "electron": np.maximum(electron, 0.0),
            "je": np.hypot(jx, jy),
            "joule": np.abs(joule),
            "fe": np.maximum(fe, 0.0),
            "fe_dos": np.maximum(fe_dos, 0.0),
        },
    )


def positive_log(values: np.ndarray) -> np.ndarray:
    out = np.full(values.shape, np.nan, dtype=float)
    mask = np.isfinite(values) & (values > 0.0)
    out[mask] = np.log10(values[mask])
    return out


def shared_limits(grids: dict[tuple[str, str], Grid], field: str) -> tuple[float, float, float]:
    positives = np.concatenate(
        [g.values[field][g.values[field] > 0.0].ravel() for g in grids.values()]
    )
    if positives.size == 0:
        return -1.0, 1.0, 0.0
    actual_min = float(np.min(positives))
    actual_max = float(np.max(positives))
    vmax = math.log10(actual_max)
    vmin = max(math.log10(actual_min), vmax - 12.0)
    if math.isclose(vmin, vmax):
        vmin -= 1.0
    return vmin, vmax, actual_min


def draw_geometry(ax: plt.Axes, max_y: float) -> None:
    ax.axhline(0.15, color="white", ls="--", lw=0.55, alpha=0.8)
    ax.axhline(0.35, color="white", ls=":", lw=0.65, alpha=0.9)
    ax.axvline(9.0, color="white", ls="--", lw=0.5, alpha=0.65)
    ax.axvline(11.0, color="#55e6ff", ls=":", lw=0.7, alpha=0.95)
    ax.axvline(18.0, color="#ffd84d", ls="--", lw=0.55, alpha=0.8)
    ax.set_xlim(0.0, 20.0)
    ax.set_ylim(max_y, 0.0)
    ax.set_xlabel("x (µm)")


def plot_matrix(
    grids: dict[tuple[str, str], Grid],
    limits: dict[str, tuple[float, float, float]],
    out_path: Path,
    max_y: float,
) -> None:
    fig, axes = plt.subplots(4, 3, figsize=(17.5, 14.0), constrained_layout=True)
    for row, (field, title, color_label, cmap) in enumerate(FIELDS):
        vmin, vmax, _ = limits[field]
        norm = Normalize(vmin=vmin, vmax=vmax, clip=True)
        last = None
        for col, time in enumerate(TIMES):
            ax = axes[row, col]
            for zone in ZONES:
                grid = grids[(time, zone)]
                mask = grid.y <= max_y + 1e-12
                if not np.any(mask):
                    continue
                last = ax.pcolormesh(
                    grid.x,
                    grid.y[mask],
                    positive_log(grid.values[field][mask]),
                    shading="nearest",
                    cmap=cmap,
                    norm=norm,
                    rasterized=True,
                )
            draw_geometry(ax, max_y)
            if col == 0:
                ax.set_ylabel(f"{title}\ndepth y (µm)")
            if row == 0:
                ax.set_title(TIME_LABEL[time])
        if last is not None:
            fig.colorbar(last, ax=axes[row, :], shrink=0.86, label=color_label)
    fig.suptitle(
        "RUN096 spatial closure — shared color scale within each row\n"
        "white: channel/UID boundaries; cyan: ion track x=11 µm; yellow: drain edge",
        fontsize=14,
    )
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def maximum_record(time: str, zone: str, field: str, grid: Grid) -> dict[str, float | str]:
    values = grid.values[field]
    index = np.unravel_index(int(np.nanargmax(values)), values.shape)
    return {
        "time_label": time,
        "zone": zone,
        "field": field,
        "max_value": float(values[index]),
        "x_at_max_um": float(grid.x[index[1]]),
        "y_at_max_um": float(grid.y[index[0]]),
    }


def write_metrics(
    grids: dict[tuple[str, str], Grid],
    path_metrics: Path,
    out_dir: Path,
    limits: dict[str, tuple[float, float, float]],
) -> None:
    records: list[dict[str, float | str]] = []
    for time in TIMES:
        for zone in ZONES:
            grid = grids[(time, zone)]
            for field, *_ in FIELDS:
                records.append(maximum_record(time, zone, field, grid))
    pd.DataFrame(records).to_csv(out_dir / "RUN096_H04_spatial_maxima.csv", index=False)

    scale_rows = []
    for field, title, *_ in FIELDS:
        vmin, vmax, actual_min = limits[field]
        actual_max = 10.0**vmax
        scale_rows.append(
            {
                "field": field,
                "label": title,
                "actual_min_positive": actual_min,
                "actual_max": actual_max,
                "display_log10_min": vmin,
                "display_log10_max": vmax,
            }
        )
    pd.DataFrame(scale_rows).to_csv(out_dir / "RUN096_H04_shared_color_scales.csv", index=False)

    paths = pd.read_csv(path_metrics)
    paths = paths[(paths["run"] == "RUN096") & (paths["path_kind"] == "directed")]
    if "method" in paths.columns:
        paths = paths[paths["method"] == "native-vertex-Delaunay"]
    if "endpoint_case" in paths.columns:
        paths = paths[paths["endpoint_case"] == "x2-x18_channel-edge"]
    paths = paths[paths["time_label"].isin(TIMES)].copy()
    keep = [
        "time_label",
        "path_score_Acm-2",
        "bottleneck_x_um",
        "bottleneck_y_um",
        "bottleneck_zone",
        "bottleneck_Je_mag_Acm-2",
        "path_channel_fraction",
        "path_UID_fraction",
        "path_substrate_fraction",
    ]
    paths[keep].to_csv(out_dir / "RUN096_H04_connectivity_bottleneck.csv", index=False)

    occupancy_rows = []
    for time in TIMES:
        for zone in ZONES:
            grid = grids[(time, zone)]
            dos = grid.values["fe_dos"]
            ionized = grid.values["fe"]
            mask = dos > 0.0
            occupancy = np.divide(ionized[mask], dos[mask]) if np.any(mask) else np.array([])
            occupancy_rows.append(
                {
                    "time_label": time,
                    "zone": zone,
                    "positive_dos_points": int(mask.sum()),
                    "Fe_occupation_median": float(np.median(occupancy)) if occupancy.size else math.nan,
                    "Fe_occupation_max": float(np.max(occupancy)) if occupancy.size else math.nan,
                }
            )
    pd.DataFrame(occupancy_rows).to_csv(out_dir / "RUN096_H04_Fe_occupation.csv", index=False)


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    grids: dict[tuple[str, str], Grid] = {}
    for time in TIMES:
        for zone in ZONES:
            topology = args.topology_dir / f"RUN096_{time}_{zone}.csv"
            thermal = args.thermal_dir / f"RUN096_{time}_{zone}_thermaltrap.csv"
            grids[(time, zone)] = load_grid(topology, thermal)

    limits = {field: shared_limits(grids, field) for field, *_ in FIELDS}
    plot_matrix(grids, limits, args.out_dir.parent / "figs" / "RUN096_H04_fourfield_full_depth.png", 5.35)
    plot_matrix(grids, limits, args.out_dir.parent / "figs" / "RUN096_H04_fourfield_shallow_zoom.png", 0.35)
    write_metrics(grids, args.path_metrics, args.out_dir, limits)
    print("[ok] RUN096 H04 spatial closure complete")


if __name__ == "__main__":
    main()
