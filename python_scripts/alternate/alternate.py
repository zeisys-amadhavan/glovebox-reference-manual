import sys
from pypdf import PdfReader, PdfWriter

def main():
    if len(sys.argv) != 4:
        print("Usage: python alternate.py <odd_pages.pdf> <even_page.pdf> <output_full.pdf>")
        print("Example: python alternate.py odd_pages.pdf even_page.pdf full.pdf")
        print("\nThis script inserts the even page after every odd page,")
        print("creating a new PDF that is exactly double the original size.")
        sys.exit(1)

    odd_pdf_path = sys.argv[1]
    even_pdf_path = sys.argv[2]
    output_path = sys.argv[3]

    try:
        # Load the PDFs
        odd_reader = PdfReader(odd_pdf_path)
        even_reader = PdfReader(even_pdf_path)

        if len(even_reader.pages) == 0:
            print("Error: The even page PDF has no pages.")
            sys.exit(1)

        # Use the first page of the even PDF
        even_page = even_reader.pages[0]

        writer = PdfWriter()

        # Interleave: odd1, even, odd2, even, ..., oddN, even
        for odd_page in odd_reader.pages:
            writer.add_page(odd_page)   # Original odd page
            writer.add_page(even_page)  # Insert the same even page after it

        # Save to the user-specified output file
        with open(output_path, "wb") as output_file:
            writer.write(output_file)

        print(f"✅ Success! Created '{output_path}'")
        print(f"   Original pages : {len(odd_reader.pages)}")
        print(f"   Final pages    : {len(writer.pages)} (exactly double)")

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
