# PDF Print-Ready Converter

A one-command tool that converts PDFs into high-resolution print-ready pages with correct bleed and odd/even positioning, combines them into a single PDF, and cleans up intermediate files automatically.

---

## Files Required

Place the following files in the same folder:

- `toprint.py`
- `draft-letter.yaml`
- Your original `.pdf` files

---

## Installation

Install the required Python packages once:

```bash
pip install pymupdf pyyaml tqdm
```

---

## How to Run

From the folder containing `toprint.py` and `draft-letter.yaml`, run:

```bash
python toprint.py draft-letter.yaml
```

On some systems, use:

```bash
python3 toprint.py draft-letter.yaml
```

---

## What the Script Does

The script will:

1. Delete any old `TOPRINT` folder.
2. Create fresh print-ready pages using the settings in `draft-letter.yaml`.
3. Combine all pages into one final PDF.
4. Delete the individual intermediate files.
5. Leave only the final combined PDF in the `TOPRINT` folder.

---

## Output

```text
TOPRINT/
└── COMBINED.pdf
```

`COMBINED.pdf` is the final ready-to-print file.

---

## Configuration

All settings are controlled through `draft-letter.yaml`.

Open `draft-letter.yaml` in any text editor to adjust:

- Page size
- Bleed
- Margins
- Filename text
- DPI
- Other layout settings

After changing the configuration, run the script again.

---

## Quick Tips

- Always run the command from the folder containing `toprint.py` and `draft-letter.yaml`.
- Every run starts fresh because the old `TOPRINT` folder is deleted automatically.
- Edit `draft-letter.yaml` whenever you need a different layout.
- Re-run the script as many times as needed.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `No module named 'yaml'` | Run `pip install pyyaml` |
| `No module named 'fitz'` | Run `pip install pymupdf` |
| No PDFs processed | Make sure your `.pdf` files are in the same folder as `toprint.py` |
| Old files still appear | Delete the `TOPRINT` folder manually and run the script again |

---

## Basic Command Sequence

```bash
pip install pymupdf pyyaml tqdm
python toprint.py draft-letter.yaml
```
