"""Convert all McNaughton Neurolab subject-sessions to NWB."""

from __future__ import annotations

import argparse
from pathlib import Path

from .convert_session import convert_session


SUBJECTS = [
    "FD4RAT1",
    "FD4RAT2",
    "FD4RAT3",
    "FD9RAT1",
    "FD9RAT2",
    "PREFLI~1",
    "PREFLI~2",
    "PREFLI~3",
]


def convert_all(
    base_dir: Path,
    output_dir: Path,
    subjects: list[str] | None = None,
    stub_test: bool = False,
) -> None:
    subjects = subjects or SUBJECTS
    output_dir.mkdir(parents=True, exist_ok=True)

    for subject in subjects:
        print(f"Converting {subject}...")
        try:
            out_path = convert_session(
                base_dir=base_dir,
                subject_name=subject,
                output_dir=output_dir,
                stub_test=stub_test,
            )
            print(f"  Wrote: {out_path}")
        except Exception as e:
            print(f"  FAILED: {e}")


def main():
    parser = argparse.ArgumentParser(description="Convert McNaughton Neurolab data to NWB")
    parser.add_argument(
        "--base",
        required=True,
        help="Path to McNaughton_Neurolab directory",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output directory for NWB files",
    )
    parser.add_argument(
        "--subjects",
        nargs="*",
        default=None,
        help="Subset of subjects to convert (default: all)",
    )
    parser.add_argument(
        "--stub-test",
        action="store_true",
        help="Only convert a small subset for quick testing",
    )
    args = parser.parse_args()

    convert_all(
        base_dir=Path(args.base),
        output_dir=Path(args.output),
        subjects=args.subjects,
        stub_test=args.stub_test,
    )


if __name__ == "__main__":
    main()
