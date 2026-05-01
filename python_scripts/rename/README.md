# PDF Batch Renamer

A command-line tool for batch renaming PDF files using a CSV file that maps old filenames to new filenames.

This is useful when you have a folder of PDF files and a table of contents or filename mapping CSV, and you need the actual PDF filenames to match the updated naming system.

---

## Purpose

This program reads a CSV file with two filename columns:

- One column for the current PDF filename.
- One column for the new PDF filename.

It then renames the matching PDF files in the selected folder.

---

## Files Required

Place the following files in your working folder:

- `rename.py`
- Your CSV filename mapping file
- The PDF files you want to rename

Example:

```text
project-folder/
├── rename.py
├── toc.csv
├── A01-Old-Name.pdf
├── A03-Old-Name.pdf
└── A05-Old-Name.pdf
```

---

## Installation

No special package installation is required.

This script uses only Python’s built-in libraries:

- `argparse`
- `csv`
- `os`
- `pathlib`

You only need Python installed.

---

## CSV Format

Your CSV must contain one column for the old filenames and one column for the new filenames.

By default, the script expects these column names:

| Column | Meaning |
|---|---|
| `OLDFILE` | Current PDF filename |
| `Newfile` | New PDF filename |

Example:

```csv
OLDFILE,Newfile
A01-Old-Name.pdf,A01-Assess-Section-Intro.pdf
A03-Old-Name.pdf,A03-OODA-Loop.pdf
A05-Old-Name.pdf,A05-Winching-Towing-Hoisting.pdf
```

The `.pdf` extension is optional in the CSV. If it is missing, the script adds it automatically.

These are both valid:

```csv
OLDFILE,Newfile
A01-Old-Name,A01-Assess-Section-Intro
A03-Old-Name.pdf,A03-OODA-Loop.pdf
```

---

## Basic Command

From the folder containing `rename.py`, run:

```bash
python rename.py toc.csv
```

On some systems, use:

```bash
python3 rename.py toc.csv
```

This uses the default CSV columns:

```text
OLDFILE
Newfile
```

It also searches for PDF files in the current folder by default.

---

## Recommended First Run: Dry Run

Before renaming files, run the script in dry-run mode:

```bash
python rename.py toc.csv --dry-run
```

Dry-run mode shows what would be renamed without changing any files.

Example output:

```text
[DRY RUN] Would rename: A01-Old-Name.pdf → A01-Assess-Section-Intro.pdf
[DRY RUN] Would rename: A03-Old-Name.pdf → A03-OODA-Loop.pdf

Dry-run complete. 2 file(s) would have been renamed.
```

After confirming the output is correct, run the real rename command:

```bash
python rename.py toc.csv
```

---

## Using Different Column Names

If your CSV uses different column names, specify them with command-line options.

Example CSV:

```csv
CURRENT_FILENAME,NEW_FILENAME
A01-Old-Name.pdf,A01-Assess-Section-Intro.pdf
A03-Old-Name.pdf,A03-OODA-Loop.pdf
```

Run:

```bash
python rename.py toc.csv --old-column CURRENT_FILENAME --new-column NEW_FILENAME
```

---

## Renaming PDFs in a Different Folder

By default, the script renames PDF files in the current directory.

To rename files in a different folder, use `--directory` or `-d`.

```bash
python rename.py toc.csv --directory ./PDFS
```

Or:

```bash
python rename.py toc.csv -d ./PDFS
```

---

## Full Example

Run a dry run first:

```bash
python rename.py toc.csv --old-column OLDFILE --new-column Newfile --directory ./PDFS --dry-run
```

Then run the actual rename:

```bash
python rename.py toc.csv --old-column OLDFILE --new-column Newfile --directory ./PDFS
```

---

## What the Script Does

For each row in the CSV, the script:

1. Reads the old filename.
2. Reads the new filename.
3. Adds `.pdf` if the extension is missing.
4. Looks for the old PDF file in the selected folder.
5. Renames the file to the new filename.
6. Prints a message showing what happened.

---

## What the Script Skips

The script skips a row when:

- The old filename is blank.
- The new filename is blank.
- The old and new filenames are identical.

It prints a warning when:

- The source PDF file is not found.
- A required CSV column is missing.
- The CSV file is not found.
- The selected directory does not exist.
- A file cannot be renamed due to permissions or another error.

---

## Important Safety Notes

Always run `--dry-run` first.

Before batch renaming, it is also wise to keep a backup copy of the folder.

The script does not create a separate undo file. Once filenames are changed, reversing them requires another CSV mapping or manual renaming.

Be careful with target filenames that already exist in the folder. Depending on your operating system, renaming to an existing filename may fail or replace the existing file.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `CSV file not found` | Check the CSV filename or path |
| `Columns ... not found in CSV` | Check the exact column names and capitalization |
| `Directory does not exist` | Check the folder path used with `--directory` |
| `Source file not found` | Make sure the old filename in the CSV matches the actual PDF filename |
| Files are not renamed | Run without `--dry-run` after checking the dry-run output |
| Permission denied | Close the PDF file if it is open, then run the script again |

---

## Basic Command Sequence

```bash
python rename.py toc.csv --dry-run
python rename.py toc.csv
```

Use this program when you need to rename a folder of PDF files so the filenames match a table of contents, print order, or updated naming system.
