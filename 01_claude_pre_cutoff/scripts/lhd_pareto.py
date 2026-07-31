#!/usr/bin/env python3
"""LHD sampling and BV↑/Ron↓ Pareto refinement for the DeckBuild SWEEP line."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np


def parse_var(spec: str) -> tuple[str, float, float, bool]:
    parts = spec.split(":")
    if len(parts) not in (3, 4):
        raise argparse.ArgumentTypeError(
            f"{spec!r}: expected name:min:max[:log]"
        )
    name = parts[0].strip()
    low, high = float(parts[1]), float(parts[2])
    is_log = len(parts) == 4 and parts[3].lower() == "log"
    if not name or low >= high:
        raise argparse.ArgumentTypeError(f"{spec!r}: require name and min < max")
    if len(parts) == 4 and not is_log:
        raise argparse.ArgumentTypeError(f"{spec!r}: fourth field must be 'log'")
    if is_log and low <= 0:
        raise argparse.ArgumentTypeError(f"{spec!r}: log lower bound must be > 0")
    return name, low, high, is_log


def lhs_values(
    n: int, variables: list[tuple[str, float, float, bool]], seed: int
) -> np.ndarray:
    if n < 1:
        raise ValueError("sample count must be >= 1")
    rng = np.random.default_rng(seed)
    unit = np.empty((n, len(variables)), dtype=float)
    for column in range(len(variables)):
        strata = (np.arange(n) + rng.random(n)) / n
        unit[:, column] = strata[rng.permutation(n)]

    values = np.empty_like(unit)
    for column, (_, low, high, is_log) in enumerate(variables):
        if is_log:
            values[:, column] = np.exp(
                np.log(low) + unit[:, column] * (np.log(high) - np.log(low))
            )
        else:
            values[:, column] = low + unit[:, column] * (high - low)
    return values


def write_samples(
    path: Path,
    variables: list[tuple[str, float, float, bool]],
    values: np.ndarray,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow([var[0] for var in variables])
        writer.writerows([[f"{value:.12g}" for value in row] for row in values])


def write_sweep_main(
    path: Path,
    variables: list[tuple[str, float, float, bool]],
    values: np.ndarray,
    load_file: str,
    save_file: str,
) -> None:
    if len(variables) != 1:
        raise ValueError(
            "DeckBuild SWEEP type=list binds one parameter; refusing to turn "
            "multi-dimensional LHD columns into a Cartesian product"
        )
    name = variables[0][0]
    data = ",".join(f"{value:.12g}" for value in values[:, 0])
    text = (
        "GO internal\n\n"
        f"LOAD infile={load_file}\n\n"
        f'SWEEP parameter={name} type=list data="{data}"\n\n'
        f"SAVE type=sdb outfile={save_file}\n\n"
        "QUIT\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def read_numeric_csv(path: Path) -> tuple[list[str], list[dict[str, float]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path}: missing header")
        rows = [
            {name: float(value) for name, value in row.items()}
            for row in reader
            if row and all(value not in (None, "") for value in row.values())
        ]
    if not rows:
        raise ValueError(f"{path}: no complete numeric rows")
    return list(reader.fieldnames), rows


def pareto_rows(
    rows: list[dict[str, float]], bv_name: str, ron_name: str
) -> tuple[list[dict[str, float]], list[dict[str, float]]]:
    frontier: list[dict[str, float]] = []
    dominated: list[dict[str, float]] = []
    for index, row in enumerate(rows):
        is_dominated = any(
            other[bv_name] >= row[bv_name]
            and other[ron_name] <= row[ron_name]
            and (
                other[bv_name] > row[bv_name]
                or other[ron_name] < row[ron_name]
            )
            for other_index, other in enumerate(rows)
            if other_index != index
        )
        (dominated if is_dominated else frontier).append(row)
    return frontier, dominated


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def print_rows(rows: list[dict[str, float]], fieldnames: list[str]) -> None:
    print(",".join(fieldnames))
    for row in rows:
        print(",".join(f"{row[name]:.12g}" for name in fieldnames))


def command_pareto(args: argparse.Namespace) -> None:
    fieldnames, rows = read_numeric_csv(args.input)
    for required in (args.bv, args.ron):
        if required not in fieldnames:
            raise ValueError(f"{args.input}: missing column {required!r}")
    frontier, dominated = pareto_rows(rows, args.bv, args.ron)
    write_rows(args.output, fieldnames, frontier)
    print(
        f"rows={len(rows)} frontier={len(frontier)} dominated={len(dominated)} "
        f"objectives={args.bv}:max,{args.ron}:min"
    )
    print_rows(frontier, fieldnames)
    print(f"wrote {args.output}")


def command_sample(args: argparse.Namespace) -> None:
    values = lhs_values(args.count, args.variables, args.seed)
    write_samples(args.output, args.variables, values)
    if args.sweep_out is not None:
        write_sweep_main(
            args.sweep_out,
            args.variables,
            values,
            args.load,
            args.save,
        )
    print(
        f"samples={args.count} dimensions={len(args.variables)} seed={args.seed} "
        "method=numpy-stratified-permuted"
    )
    print_rows(
        [
            {var[0]: value for var, value in zip(args.variables, row)}
            for row in values
        ],
        [var[0] for var in args.variables],
    )
    print(f"wrote {args.output}")
    if args.sweep_out is not None:
        print(f"wrote {args.sweep_out}")


def refined_variables(
    frontier: list[dict[str, float]],
    variables: list[tuple[str, float, float, bool]],
    shrink: float,
) -> list[tuple[str, float, float, bool]]:
    if not 0 < shrink < 1:
        raise ValueError("shrink must be between 0 and 1")
    refined = []
    for name, low, high, is_log in variables:
        coordinates = np.array([row[name] for row in frontier])
        if is_log:
            box_low, box_high = np.log(low), np.log(high)
            point_low, point_high = np.log(coordinates.min()), np.log(coordinates.max())
        else:
            box_low, box_high = low, high
            point_low, point_high = coordinates.min(), coordinates.max()

        target_width = (box_high - box_low) * shrink
        center = (point_low + point_high) / 2
        new_low, new_high = center - target_width / 2, center + target_width / 2
        if new_low < box_low:
            new_high += box_low - new_low
            new_low = box_low
        if new_high > box_high:
            new_low -= new_high - box_high
            new_high = box_high
        new_low, new_high = max(new_low, box_low), min(new_high, box_high)
        if is_log:
            new_low, new_high = np.exp(new_low), np.exp(new_high)
        refined.append((name, float(new_low), float(new_high), is_log))
    return refined


def command_refine(args: argparse.Namespace) -> None:
    fieldnames, rows = read_numeric_csv(args.input)
    required = {args.bv, args.ron, *(var[0] for var in args.variables)}
    missing = sorted(required.difference(fieldnames))
    if missing:
        raise ValueError(f"{args.input}: missing columns {missing}")
    frontier, dominated = pareto_rows(rows, args.bv, args.ron)
    variables = refined_variables(frontier, args.variables, args.shrink)
    values = lhs_values(args.count, variables, args.seed)
    write_samples(args.output, variables, values)
    if args.sweep_out is not None:
        write_sweep_main(
            args.sweep_out, variables, values, args.load, args.save
        )
    print(
        f"source_rows={len(rows)} frontier={len(frontier)} "
        f"dominated={len(dominated)} shrink={args.shrink}"
    )
    for name, low, high, is_log in variables:
        print(f"next_box {name}=[{low:.12g},{high:.12g}] scale={'log' if is_log else 'linear'}")
    print_rows(
        [
            {var[0]: value for var, value in zip(variables, row)}
            for row in values
        ],
        [var[0] for var in variables],
    )
    print(f"wrote {args.output}")
    if args.sweep_out is not None:
        print(f"wrote {args.sweep_out}")


def add_sampling_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-n", "--count", type=int, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--var",
        dest="variables",
        action="append",
        type=parse_var,
        required=True,
        help="name:min:max[:log]; repeat for more dimensions",
    )
    parser.add_argument("--out", dest="output", type=Path, required=True)
    parser.add_argument("--sweep-out", type=Path)
    parser.add_argument("--load", default="lhd_round1_aux.in")
    parser.add_argument("--save", default="lhd_round1.dat")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    pareto = subparsers.add_parser("pareto")
    pareto.add_argument("input", type=Path)
    pareto.add_argument("--out", dest="output", type=Path, required=True)
    pareto.add_argument("--bv", default="bv")
    pareto.add_argument("--ron", default="ron")
    pareto.set_defaults(func=command_pareto)

    sample = subparsers.add_parser("sample")
    add_sampling_arguments(sample)
    sample.set_defaults(func=command_sample)

    refine = subparsers.add_parser("refine")
    refine.add_argument("input", type=Path)
    refine.add_argument("--bv", default="bv")
    refine.add_argument("--ron", default="ron")
    refine.add_argument("--shrink", type=float, default=0.5)
    add_sampling_arguments(refine)
    refine.set_defaults(func=command_refine)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
