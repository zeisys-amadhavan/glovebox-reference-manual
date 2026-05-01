#!/usr/bin/env python3
import sys
from pathlib import Path
from collections import defaultdict

import pandas as pd


def normalize_key(value: object) -> str:
    """Normalize CSV/PDF names for comparison.

    - trims whitespace
    - strips a trailing .pdf if present
    - compares case-insensitively
    """
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if not text:
        return ""
    if text.lower().endswith(".pdf"):
        text = text[:-4]
    return text.casefold()


def usage(script_name: str) -> None:
    print(f"Usage: python {script_name} <csv_file> <match_column>")
    print("Example: python audit_pdf_vs_toc.py toc.csv FILENAME")


def main() -> None:
    if len(sys.argv) != 3:
        usage(Path(sys.argv[0]).name)
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    match_column = sys.argv[2]

    if not csv_path.is_file():
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)

    # Search the directory where this Python script lives.
    script_dir = Path(__file__).resolve().parent

    try:
        df = pd.read_csv(csv_path)
    except Exception as exc:
        print(f"Error reading CSV '{csv_path}': {exc}")
        sys.exit(1)

    if match_column not in df.columns:
        print(
            f"Error: CSV must contain a column named '{match_column}' "
            f"(case-sensitive). Available columns: {', '.join(df.columns)}"
        )
        sys.exit(1)

    pdf_files = sorted([p for p in script_dir.glob("*.pdf") if p.is_file()])
    print(f"Found {len(pdf_files)} PDF file(s) in {script_dir}")

    # Map normalized PDF basename -> list of actual PDF filenames
    pdf_map: dict[str, list[str]] = defaultdict(list)
    for pdf in pdf_files:
        pdf_key = normalize_key(pdf.stem)
        pdf_map[pdf_key].append(pdf.name)

    # Map normalized CSV filename -> row indices (to detect duplicate keys in CSV)
    csv_key_to_rows: dict[str, list[int]] = defaultdict(list)
    csv_keys: list[str] = []
    for idx, value in df[match_column].items():
        key = normalize_key(value)
        csv_keys.append(key)
        if key:
            csv_key_to_rows[key].append(idx)

    pdf_present_list = []
    matched_pdf_list = []
    audit_note_list = []

    for idx, raw_value in df[match_column].items():
        key = csv_keys[idx]
        notes: list[str] = []
        matched_pdf = ""
        present = False

        if not key:
            notes.append("Blank filename in CSV")
        elif key in pdf_map:
            present = True
            matched_names = sorted(pdf_map[key])
            matched_pdf = " | ".join(matched_names)
            if len(matched_names) > 1:
                notes.append("Multiple PDFs share this filename key")
        else:
            notes.append("Missing PDF for CSV row")

        if key and len(csv_key_to_rows.get(key, [])) > 1:
            notes.append("Duplicate filename key in CSV")

        pdf_present_list.append(present)
        matched_pdf_list.append(matched_pdf)
        audit_note_list.append("; ".join(notes))

    # Add markup columns without disturbing existing content.
    df["PDF_PRESENT"] = pdf_present_list
    df["MATCHED_PDF"] = matched_pdf_list
    df["PDF_AUDIT_NOTE"] = audit_note_list

    # Orphan PDFs = PDFs whose normalized basename is not represented in the CSV.
    csv_key_set = {k for k in csv_keys if k}
    orphan_rows: list[dict[str, str]] = []
    for key, pdf_names in sorted(pdf_map.items()):
        if key not in csv_key_set:
            for pdf_name in sorted(pdf_names):
                note = "PDF not represented in CSV"
                if len(pdf_names) > 1:
                    note += "; Multiple PDFs share this filename key"
                orphan_rows.append(
                    {
                        "PDF_FILENAME": pdf_name,
                        "PDF_KEY": key,
                        "PDF_AUDIT_NOTE": note,
                    }
                )

    orphan_df = pd.DataFrame(orphan_rows)

    output_csv = csv_path.with_name(f"{csv_path.stem}_pdf_audit.csv")
    orphans_csv = csv_path.with_name(f"{csv_path.stem}_orphan_pdfs.csv")

    try:
        df.to_csv(output_csv, index=False)
        orphan_df.to_csv(orphans_csv, index=False)
    except Exception as exc:
        print(f"Error saving output files: {exc}")
        sys.exit(1)

    missing_count = int((df["PDF_PRESENT"] == False).sum())  # noqa: E712
    present_count = int((df["PDF_PRESENT"] == True).sum())   # noqa: E712
    orphan_count = len(orphan_df)

    print("\nAudit complete.")
    print(f"- Marked-up CSV written to: {output_csv}")
    print(f"- Orphan PDF report written to: {orphans_csv}")
    print(f"- CSV rows with matching PDF: {present_count}")
    print(f"- CSV rows missing PDF: {missing_count}")
    print(f"- PDFs not represented in CSV: {orphan_count}")

    if missing_count:
        print("\nMissing CSV rows:")
        missing_subset = df[df["PDF_PRESENT"] == False]  # noqa: E712
        display_cols = [col for col in [match_column, "TITLE", "PDF_AUDIT_NOTE"] if col in missing_subset.columns]
        for _, row in missing_subset[display_cols].iterrows():
            title_part = f" | {row['TITLE']}" if "TITLE" in row and pd.notna(row.get("TITLE")) else ""
            print(f"  - {row[match_column]}{title_part}")

    if orphan_count:
        print("\nOrphan PDFs:")
        for _, row in orphan_df.iterrows():
            print(f"  - {row['PDF_FILENAME']}")


if __name__ == "__main__":
    main()
