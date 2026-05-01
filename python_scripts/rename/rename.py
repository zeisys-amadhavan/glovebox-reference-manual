import argparse
import csv
import os
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Rename PDF files in a folder based on a CSV mapping of old to new filenames.")
    parser.add_argument("csv_file", help="Path to the CSV file containing the rename mapping")
    parser.add_argument("--old-column", default="OLDFILE", help="Column name for old filename (default: OLDFILE)")
    parser.add_argument("--new-column", default="Newfile", help="Column name for new filename (default: Newfile)")
    parser.add_argument("--directory", "-d", default=".", help="Directory where the PDF files are located (default: current directory)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be renamed without actually renaming files")

    args = parser.parse_args()

    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        return

    dir_path = Path(args.directory).resolve()
    if not dir_path.exists():
        print(f"Error: Directory {dir_path} does not exist.")
        return

    renamed_count = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Check that the required columns exist
        if args.old_column not in reader.fieldnames or args.new_column not in reader.fieldnames:
            print(f"Error: Columns '{args.old_column}' or '{args.new_column}' not found in CSV.")
            print(f"Available columns: {reader.fieldnames}")
            return

        for row_num, row in enumerate(reader, start=2):  # start=2 because line 1 is the header
            old_name = str(row[args.old_column]).strip()
            new_name = str(row[args.new_column]).strip()

            if not old_name or not new_name:
                print(f"Skipping row {row_num}: empty filename(s)")
                continue

            # Ensure .pdf extension (user can put names with or without extension in CSV)
            if not old_name.lower().endswith('.pdf'):
                old_name = old_name + '.pdf'
            if not new_name.lower().endswith('.pdf'):
                new_name = new_name + '.pdf'

            old_path = dir_path / old_name
            new_path = dir_path / new_name

            if old_path == new_path:
                print(f"Skipping row {row_num}: old and new names are identical")
                continue

            if old_path.exists():
                if args.dry_run:
                    print(f"[DRY RUN] Would rename: {old_name} → {new_name}")
                    renamed_count += 1
                else:
                    try:
                        os.rename(old_path, new_path)
                        print(f"✅ Renamed: {old_name} → {new_name}")
                        renamed_count += 1
                    except FileExistsError:
                        print(f"❌ Row {row_num}: Target already exists: {new_name}")
                    except PermissionError:
                        print(f"❌ Row {row_num}: Permission denied renaming {old_name}")
                    except Exception as e:
                        print(f"❌ Row {row_num}: Error renaming {old_name} → {e}")
            else:
                print(f"⚠️  Warning row {row_num}: Source file not found: {old_name}")

    if not args.dry_run:
        print(f"\n✅ Done! {renamed_count} file(s) renamed.")
    else:
        print(f"\n✅ Dry-run complete. {renamed_count} file(s) would have been renamed.")

if __name__ == "__main__":
    main()
