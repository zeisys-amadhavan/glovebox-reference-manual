import fitz  # PyMuPDF
from pathlib import Path
import sys
from tqdm import tqdm

def combine_pdfs(input_dir="TOPRINT"):
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ Folder '{input_dir}' not found!")
        return

    # Get and sort all PDF files alphabetically
    pdf_files = sorted([f for f in input_path.glob("*.pdf") if f.is_file()])
    
    if not pdf_files:
        print("❌ No PDF files found in the folder.")
        return

    print(f"✅ Found {len(pdf_files)} PDF files. Combining in alphabetical order...")

    combined_doc = fitz.open()
    total_pages = 0
    font_error_shown = False

    for pdf_path in tqdm(pdf_files, desc="Processing files"):
        filename_text = pdf_path.name  # full filename with .pdf
        
        try:
            source_doc = fitz.open(str(pdf_path))
            
            for page_num in range(len(source_doc)):
                source_page = source_doc[page_num]
                page_rect = source_page.rect
                
                # Create new page
                new_page = combined_doc.new_page(width=page_rect.width, height=page_rect.height)
                
                # Copy the original page content (vector quality)
                new_page.show_pdf_page(new_page.rect, source_doc, page_num)
                
                total_pages += 1
                
                # === ADD FILENAME AT THE VERY TOP ===
                try:
                    margin = 30
                    text_height = 32          # increased for larger font
                    text_rect = fitz.Rect(margin, margin, page_rect.width - margin, margin + text_height)
                    
                    # Light background box
                    new_page.draw_rect(
                        text_rect,
                        color=None,
                        fill=(0.98, 0.98, 0.98),
                        width=0
                    )
                    
                    # Insert filename using Courier-Bold at fontsize 12
                    new_page.insert_textbox(
                        text_rect,
                        filename_text,
                        fontsize=12,                 # ← TWO SIZES BIGGER
                        fontname="Courier-Bold",
                        align=fitz.TEXT_ALIGN_CENTER,
                        color=(0, 0, 0),
                        fill_opacity=1.0
                    )
                except Exception as text_err:
                    if not font_error_shown:
                        print(f"\n⚠️  Warning: Could not add filename text (font issue). Pages are still being combined.")
                        font_error_shown = True
            
            source_doc.close()
            
        except Exception as e:
            print(f"⚠️  Error processing {pdf_path.name}: {e}")

    # Save COMBINED.pdf inside the TOPRINT folder
    output_path = input_path / "COMBINED.pdf"
    combined_doc.save(
        str(output_path),
        garbage=4,
        deflate=True,
        clean=True,
        expand=0
    )
    combined_doc.close()
    
    print(f"\n🎉 SUCCESS! Combined PDF created:")
    print(f"   📄 {output_path}")
    print(f"   📄 Total pages: {total_pages}")
    print(f"   📄 Filenames now appear at the top in **Courier-Bold 12pt**.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        combine_pdfs(sys.argv[1])
    else:
        combine_pdfs()
