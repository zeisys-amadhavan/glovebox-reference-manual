import fitz  # PyMuPDF
from pathlib import Path
import sys
import yaml  # pip install pyyaml
from tqdm import tqdm
import shutil

def load_config(config_path):
    config_path = Path(config_path)
    if not config_path.exists():
        print(f"❌ Error: Config file not found: {config_path}")
        print("Usage: python toprint.py <config.yaml>")
        sys.exit(1)
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error reading config file {config_path}: {e}")
        sys.exit(1)

def prepare_output_dir(output_dir):
    output_path = Path(output_dir)
    if output_path.exists():
        print(f"🗑️  Existing folder '{output_dir}' found. Deleting it and all contents...")
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"📁 Created fresh output folder: {output_dir}")
    return output_path

def process_individual_pdfs(input_dir, config, output_dir):
    input_path = Path(input_dir)
    pdf_files = list(input_path.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files to process...\n")

    for file_idx, pdf_path in enumerate(tqdm(pdf_files, desc="Converting PDFs")):
        if config.get("output_subdir", "TOPRINT").upper() in str(pdf_path.parent).upper() or pdf_path.name.startswith(("~", ".")):
            continue

        out_path = output_dir / pdf_path.name

        try:
            doc = fitz.open(str(pdf_path))
            if len(doc) == 0:
                doc.close()
                continue

            new_doc = fitz.open()

            for page_num in range(len(doc)):
                # Determine odd/even page for correct bleed/offset
                global_page_idx = file_idx + page_num
                is_odd_page = (global_page_idx % 2 == 0)  # first page = odd (right-hand)

                page = doc[page_num]

                # Target trim size
                target_img_width_pt = config["trim_width_inches"] * 72
                target_img_height_pt = config["trim_height_inches"] * 72

                # Render at exact DPI
                scale_x = target_img_width_pt / page.rect.width
                scale_y = target_img_height_pt / page.rect.height
                render_scale_x = (config["dpi"] / 72.0) * scale_x
                render_scale_y = (config["dpi"] / 72.0) * scale_y

                matrix = fitz.Matrix(render_scale_x, render_scale_y)
                pix = page.get_pixmap(matrix=matrix, alpha=False)

                # Full page size (with bleed)
                page_width_pt = config["page_width_inches"] * 72
                page_height_pt = config["page_height_inches"] * 72
                new_page = new_doc.new_page(width=page_width_pt, height=page_height_pt)

                # === ODD / EVEN CONTENT POSITIONING ===
                if is_odd_page:
                    x_offset_pt = config.get("odd_page_content_x_offset_inches", 0.0) * 72
                else:
                    x_offset_pt = config.get("even_page_content_x_offset_inches", 0.125) * 72
                y_offset_pt = config.get("content_y_offset_inches", 0.125) * 72

                rect = fitz.Rect(x_offset_pt, y_offset_pt,
                                 x_offset_pt + target_img_width_pt,
                                 y_offset_pt + target_img_height_pt)

                new_page.insert_image(rect, pixmap=pix)

                # Optional filename on individual pages
                if config.get("print_filename", False):
                    filename_text = pdf_path.name
                    if len(doc) > 1:
                        filename_text += f" (Page {page_num + 1})"
                    font_size = config.get("filename_font_size", 12)
                    color = tuple(config.get("filename_color", [0, 0, 0]))
                    margin_pt = config.get("filename_margin_inches", 0.25) * 72
                    text_y = margin_pt if config.get("filename_position", "top") == "top" else page_height_pt - margin_pt - (font_size * 2.5)
                    text_rect = fitz.Rect(0, text_y, page_width_pt, text_y + font_size * 3)
                    new_page.insert_textbox(text_rect, filename_text, fontsize=font_size, color=color, align=fitz.TEXT_ALIGN_CENTER)

            new_doc.save(str(out_path), garbage=3, deflate=True, clean=True, expand=0)
            new_doc.close()
            doc.close()

        except Exception as e:
            print(f"❌ Error with {pdf_path.name}: {e}")

    print(f"✅ All individual PDFs created in {output_dir.name}\n")

def combine_pdfs(output_dir, config):
    output_filename = config.get("combined_filename", "COMBINED.pdf")
    input_path = Path(output_dir)

    pdf_files = sorted([
        f for f in input_path.glob("*.pdf")
        if f.is_file() and f.name.lower() != output_filename.lower()
    ])

    if not pdf_files:
        print("❌ No PDFs found to combine.")
        return

    print(f"✅ Combining {len(pdf_files)} PDFs into '{output_filename}'...")

    combined_doc = fitz.open()
    total_pages = 0
    font_error_shown = False

    # Combined filename settings
    print_filename_combined = config.get("print_filename_combined", True)
    x_offset_pt = config.get("combined_filename_x_offset_inches", 0.42) * 72
    y_offset_pt = config.get("combined_filename_y_offset_inches", 0.42) * 72
    font_name = config.get("combined_filename_font", "Courier-Bold")
    font_size = config.get("combined_filename_font_size", 12)
    color = tuple(config.get("combined_filename_color", [0, 0, 0]))

    for pdf_path in tqdm(pdf_files, desc="Combining"):
        filename_text = pdf_path.name
        try:
            source_doc = fitz.open(str(pdf_path))
            for page_num in range(len(source_doc)):
                source_page = source_doc[page_num]
                page_rect = source_page.rect

                new_page = combined_doc.new_page(width=page_rect.width, height=page_rect.height)
                new_page.show_pdf_page(new_page.rect, source_doc, page_num)
                total_pages += 1

                if print_filename_combined:
                    try:
                        text_rect = fitz.Rect(
                            x_offset_pt,
                            y_offset_pt,
                            page_rect.width - x_offset_pt,
                            y_offset_pt + font_size * 2.5
                        )
                        new_page.draw_rect(text_rect, color=None, fill=(0.98, 0.98, 0.98), width=0)
                        new_page.insert_textbox(
                            text_rect,
                            filename_text,
                            fontsize=font_size,
                            fontname=font_name,
                            align=fitz.TEXT_ALIGN_CENTER,
                            color=color,
                            fill_opacity=1.0
                        )
                    except Exception:
                        if not font_error_shown:
                            print(f"\n⚠️  Warning: Could not add filename text.")
                            font_error_shown = True
            source_doc.close()
        except Exception as e:
            print(f"⚠️  Error processing {pdf_path.name}: {e}")

    output_path = input_path / output_filename
    combined_doc.save(str(output_path), garbage=4, deflate=True, clean=True, expand=0)
    combined_doc.close()

    print(f"\n🎉 Combined PDF created: {output_path}")
    print(f"   Total pages: {total_pages}")

    # Delete individual files
    print(f"\n🗑️  Deleting {len(pdf_files)} individual PDF files...")
    deleted_count = 0
    for pdf_path in pdf_files:
        try:
            pdf_path.unlink()
            deleted_count += 1
        except Exception as e:
            print(f"   ⚠️  Could not delete {pdf_path.name}: {e}")

    print(f"\n✅ DONE! Only **{output_filename}** remains in the folder.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python toprint.py <config.yaml>")
        sys.exit(1)

    config = load_config(sys.argv[1])

    output_dir = prepare_output_dir(config["output_subdir"])
    process_individual_pdfs(".", config, output_dir)
    combine_pdfs(output_dir, config)

    print(f"\n🎉 All finished! Your final file is:")
    print(f"   📄 {output_dir / config.get('combined_filename', 'COMBINED.pdf')}")
