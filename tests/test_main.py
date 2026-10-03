from pathlib import Path

import pandas as pd
import pytest

from src.main import DataProcessingError, clean_data, find_csv_files, load_csv_files, process_directory


def test_csv_files_load_and_merge(tmp_path: Path) -> None:
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    first.write_text("id,name\n1,Ada\n", encoding="utf-8")
    second.write_text("id,name\n2,Linus\n", encoding="utf-8")

    frames = load_csv_files(find_csv_files(tmp_path))
    combined, _, _ = clean_data(frames)

    assert combined.to_dict("records") == [
        {"id": 1, "name": "Ada"},
        {"id": 2, "name": "Linus"},
    ]


def test_duplicate_rows_are_removed() -> None:
    frame = pd.DataFrame([{"id": 1, "name": "Ada"}, {"id": 1, "name": "Ada"}])

    cleaned, duplicates_removed, _ = clean_data([frame])

    assert len(cleaned) == 1
    assert duplicates_removed == 1


def test_process_directory_creates_csv_and_excel(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    (input_dir / "data.csv").write_text("id,name\n2,Bob\n1,\n", encoding="utf-8")

    stats, csv_path, excel_path = process_directory(input_dir, output_dir, "id")

    assert stats.missing_values_filled == 1
    assert stats.final_rows == 2
    assert csv_path.exists()
    assert excel_path.exists()
    assert pd.read_excel(excel_path).iloc[0]["id"] == 1


def test_mismatched_columns_raise_clear_error(tmp_path: Path) -> None:
    (tmp_path / "first.csv").write_text("id,name\n1,Ada\n", encoding="utf-8")
    (tmp_path / "second.csv").write_text("id,email\n2,a@example.com\n", encoding="utf-8")

    with pytest.raises(DataProcessingError, match="Column mismatch"):
        load_csv_files(find_csv_files(tmp_path))


def test_empty_directory_raises_clear_error(tmp_path: Path) -> None:
    with pytest.raises(DataProcessingError, match="No CSV files"):
        find_csv_files(tmp_path)
