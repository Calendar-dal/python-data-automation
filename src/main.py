"""Batch-clean compatible CSV files and export the result to CSV and Excel."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


class DataProcessingError(Exception):
    """Raised when input data cannot be processed safely."""


@dataclass(frozen=True)
class ProcessingStats:
    input_files: int
    original_rows: int
    duplicates_removed: int
    missing_values_filled: int
    final_rows: int


def find_csv_files(input_dir: Path) -> list[Path]:
    """Return CSV files from an input directory in predictable order."""
    if not input_dir.exists():
        raise DataProcessingError(f"Input directory does not exist: {input_dir}")
    if not input_dir.is_dir():
        raise DataProcessingError(f"Input path is not a directory: {input_dir}")

    files = sorted(path for path in input_dir.glob("*.csv") if path.is_file())
    if not files:
        raise DataProcessingError(f"No CSV files found in: {input_dir}")
    return files


def load_csv_files(files: list[Path]) -> list[pd.DataFrame]:
    """Load CSV files and ensure that every file has the same columns."""
    frames: list[pd.DataFrame] = []
    expected_columns: list[str] | None = None

    for path in files:
        try:
            frame = pd.read_csv(path)
        except (OSError, UnicodeDecodeError, pd.errors.ParserError) as exc:
            raise DataProcessingError(f"Could not read CSV file '{path.name}': {exc}") from exc

        columns = frame.columns.tolist()
        if expected_columns is None:
            expected_columns = columns
        elif columns != expected_columns:
            raise DataProcessingError(
                f"Column mismatch in '{path.name}'. Expected {expected_columns}, "
                f"but found {columns}."
            )
        frames.append(frame)

    return frames


def clean_data(
    frames: list[pd.DataFrame], sort_by: str | None = None
) -> tuple[pd.DataFrame, int, int]:
    """Combine frames, remove duplicates, fill missing cells, and optionally sort."""
    combined = pd.concat(frames, ignore_index=True)
    before_deduplication = len(combined)
    combined = combined.drop_duplicates().copy()
    duplicates_removed = before_deduplication - len(combined)
    missing_values_filled = int(combined.isna().sum().sum())

    for column in combined.columns:
        if pd.api.types.is_numeric_dtype(combined[column]):
            median = combined[column].median()
            fill_value = 0 if pd.isna(median) else median
        else:
            fill_value = "Unknown"
        combined[column] = combined[column].fillna(fill_value)

    if sort_by:
        if sort_by not in combined.columns:
            raise DataProcessingError(
                f"Sort field '{sort_by}' was not found. "
                f"Available fields: {', '.join(combined.columns)}"
            )
        combined = combined.sort_values(sort_by, kind="stable", na_position="last")

    return combined.reset_index(drop=True), duplicates_removed, missing_values_filled


def write_outputs(data: pd.DataFrame, output_dir: Path, output_name: str) -> tuple[Path, Path]:
    """Write cleaned data to CSV and Excel files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"{output_name}.csv"
    excel_path = output_dir / f"{output_name}.xlsx"

    try:
        data.to_csv(csv_path, index=False)
        data.to_excel(excel_path, index=False, engine="openpyxl")
    except OSError as exc:
        raise DataProcessingError(f"Could not write output files: {exc}") from exc
    return csv_path, excel_path


def process_directory(
    input_dir: Path,
    output_dir: Path,
    sort_by: str | None = None,
    output_name: str = "cleaned_data",
) -> tuple[ProcessingStats, Path, Path]:
    """Run the complete CSV processing workflow."""
    files = find_csv_files(input_dir)
    frames = load_csv_files(files)
    original_rows = sum(len(frame) for frame in frames)
    cleaned, duplicates_removed, missing_values_filled = clean_data(frames, sort_by)
    csv_path, excel_path = write_outputs(cleaned, output_dir, output_name)
    stats = ProcessingStats(
        input_files=len(files),
        original_rows=original_rows,
        duplicates_removed=duplicates_removed,
        missing_values_filled=missing_values_filled,
        final_rows=len(cleaned),
    )
    return stats, csv_path, excel_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Combine, clean, sort, and export CSV files."
    )
    parser.add_argument("--input-dir", type=Path, default=Path("input"))
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--sort-by", help="Column used to sort the cleaned data")
    parser.add_argument("--output-name", default="cleaned_data")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        stats, csv_path, excel_path = process_directory(
            args.input_dir, args.output_dir, args.sort_by, args.output_name
        )
    except DataProcessingError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("Processing complete")
    print(f"Input files: {stats.input_files}")
    print(f"Original rows: {stats.original_rows}")
    print(f"Duplicate rows removed: {stats.duplicates_removed}")
    print(f"Missing values filled: {stats.missing_values_filled}")
    print(f"Final rows: {stats.final_rows}")
    print(f"CSV output: {csv_path}")
    print(f"Excel output: {excel_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
