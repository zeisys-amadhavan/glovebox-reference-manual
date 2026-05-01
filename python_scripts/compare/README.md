# PDF Folder vs. Table of Contents Audit

A small command-line tool for comparing the PDF files in a folder against a table of contents CSV file.

The program checks whether every PDF listed in the table of contents exists in the folder, and whether the folder contains extra PDF files that are not listed in the CSV.

This is useful when building or printing a manual where the folder contents and `toc.csv` must match exactly.

---

## Files Required

Place the following files in your working folder:

- `compare.py`
- `toc.csv`
- All PDF files that should appear in the table of contents

> Important: `compare.py` searches for PDF files in the same folder where `compare.py` is located.

---

## Installation

Install the required Python package once:

```bash
pip install pandas
```

---

## How to Run

From the folder containing `compare.py`, run:

```bash
python compare.py toc.csv FILENAME
```

On some systems, use:

```bash
python3 compare.py toc.csv FILENAME
```

Replace `FILENAME` with the exact column name in `toc.csv` that contains the expected PDF filenames.

Column names are case-sensitive.

---

## Example

If your `toc.csv` has a column named `NEWFILENAME`, run:

```bash
python compare.py toc.csv NEWFILENAME
```

If your `toc.csv` has a column named `FILENAME`, run:

```bash
python compare.py toc.csv FILENAME
```

---

## What the Script Checks

The script compares:

1. PDF files found in the folder.
2. Expected PDF filenames listed in the selected CSV column.

The comparison is normalized by:

- Trimming extra spaces.
- Ignoring `.pdf` at the end of filenames.
- Comparing filenames case-insensitively.

For example, these are treated as the same filename:

```text
A01-Section-Intro
A01-Section-Intro.pdf
a01-section-intro.pdf
```

---

## Output Files

The script creates two CSV reports.

### 1. Marked-Up TOC Audit CSV

```text
toc_pdf_audit.csv
```

This is a copy of your original `toc.csv` with three added columns:

| Column | Meaning |
|---|---|
| `PDF_PRESENT` | `True` if the PDF exists in the folder; `False` if missing |
| `MATCHED_PDF` | The actual PDF filename found in the folder |
| `PDF_AUDIT_NOTE` | Notes such as missing PDF, duplicate filename key, or blank filename |

---

### 2. Orphan PDF Report

```text
toc_orphan_pdfs.csv
```

This lists PDF files found in the folder that are not represented in the selected CSV column.

These are “orphan PDFs” because they exist in the folder but are not listed in the table of contents.

---

## Console Summary

After running, the script prints a summary like this:

```text
Audit complete.
- Marked-up CSV written to: toc_pdf_audit.csv
- Orphan PDF report written to: toc_orphan_pdfs.csv
- CSV rows with matching PDF: 120
- CSV rows missing PDF: 3
- PDFs not represented in CSV: 2
```

If there are problems, it also prints:

- CSV rows that are missing matching PDF files.
- PDF files that are not represented in the CSV.

---

## Common Workflow

1. Put `compare.py` in the folder containing your PDF files.
2. Put `toc.csv` in the same folder, or provide the path to it.
3. Run the script.
4. Open `toc_pdf_audit.csv`.
5. Fix missing, renamed, duplicated, or extra files.
6. Re-run until the CSV and folder match.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `No module named 'pandas'` | Run `pip install pandas` |
| `CSV file not found` | Make sure the CSV filename or path is correct |
| `CSV must contain a column named...` | Check the exact spelling and capitalization of the column name |
| No PDFs found | Make sure the PDF files are in the same folder as `compare.py` |
| PDFs are listed as missing | Confirm the selected CSV column contains the correct filenames |
| Extra PDFs appear in orphan report | Add them to the CSV or remove them from the folder |

---

## Basic Command Sequence

```bash
pip install pandas
python compare.py toc.csv FILENAME
```

Use this program whenever you need to confirm that the PDF folder and the table of contents match before printing, combining, or finalizing the manual.
