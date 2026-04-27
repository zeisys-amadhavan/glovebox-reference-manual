import fitz  # PyMuPDF - pip install pymupdf
from pathlib import Path
import sys
from tqdm import tqdm  # optional progress bar - pip install tqdm

def process_pdfs(input_dir="."):
    input_path = Path(input_dir)
    output_dir = input_dir / "TOPRINT" if isinstance(input_dir, Path) else Path(input_dir) / "TOPRINT"
    output_dir.mkdir(exist_ok=True)

    pdf_files = list(input_path.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files. Processing...\n")

    for pdf_path in tqdm(pdf_files, desc="Converting PDFs"):
        # Skip already-processed files and hidden files
        if "TOPRINT" in str(pdf_path.parent).upper() or pdf_path.name.startswith("~") or pdf_path.name.startswith("."):
            continue

        out_path = output_dir / pdf_path.name

        try:
            # Open original PDF
            doc = fitz.open(str(pdf_path))
            if len(doc) == 0:
                doc.close()
                continue

            # We'll process every page (most of your files are single-page labels)
            for page_num in range(len(doc)):
                page = doc[page_num]

                # Render page at exactly 300 DPI
                matrix = fitz.Matrix(300 / 72.0, 300 / 72.0)
                pix = page.get_pixmap(matrix=matrix, alpha=False)

                # Create new Letter-size PDF (8.5 x 11 inches)
                letter_width_pt = 8.5 * 72
                letter_height_pt = 11 * 72
                new_doc = fitz.open()
                new_page = new_doc.new_page(width=letter_width_pt, height=letter_height_pt)

                # Calculate centered position (keeps exact 5"x8" physical size)
                img_width_pt = pix.width * 72 / 300
                img_height_pt = pix.height * 72 / 300
                x_offset = (letter_width_pt - img_width_pt) / 2
                y_offset = (letter_height_pt - img_height_pt) / 2

                rect = fitz.Rect(x_offset, y_offset, x_offset + img_width_pt, y_offset + img_height_pt)

                # Insert the 300 DPI image
                new_page.insert_image(rect, pixmap=pix)

                # Save optimized PDF
                new_doc.save(str(out_path), garbage=3, deflate=True, clean=True, expand=0)
                new_doc.close()

            doc.close()
            print(f"✅ {pdf_path.name} → TOPRINT/{pdf_path.name} (processed)")

        except Exception as e:
            print(f"❌ Error with {pdf_path.name}: {e}")

    print("\n🎉 All done! Check the TOPRINT folder.")


if __name__ == "__main__":
    # Usage: python pdf_to_letter.py [optional input folder]
    input_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    process_pdfs(input_dir)
