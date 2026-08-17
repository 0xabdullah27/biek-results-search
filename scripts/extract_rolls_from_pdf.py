"""
Extract Roll Numbers from BIEK Result PDFs

This script extracts roll numbers from BIEK result PDF files and saves them to a text file.

Usage:
    python extract_rolls_from_pdf.py --pdf pdfs/sg_part2.pdf --output rollNumbers/sg_rolls.txt
    python extract_rolls_from_pdf.py --pdf pdfs/pm_part2.pdf --output rollNumbers/pm_rolls.txt

    # Process all PDFs in a folder
    python extract_rolls_from_pdf.py --folder pdfs --output rollNumbers/all_rolls.txt
"""

import re
import argparse
from pathlib import Path
import PyPDF2


def extract_roll_numbers_from_pdf(pdf_path: str) -> list[str]:
    """
    Extract roll numbers from a BIEK result PDF.

    In the gazettes, each student appears as a 6-digit roll number followed
    by their marks in parentheses, e.g. 312204(798). Rolls are matched by
    that pattern, so any group works regardless of the leading digit:
      - Part II 2026 Pre-Medical (PM):     3xxxxx (e.g., 312204)
      - Part II 2026 Pre-Engineering (SE): 8xxxxx (e.g., 804713)
      - Part I 2025 Pre-Medical (PM):      4xxxxx (e.g., 416921)
      - Part I 2025 Science General (SG):  7xxxxx (e.g., 716921)

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List of unique roll numbers found in the PDF
    """
    roll_numbers = set()

    # Match a 6-digit roll number immediately followed by an opening
    # parenthesis (the marks), e.g. "312204(798)". This avoids picking up
    # page numbers, dates, or statistics from the gazette. Use a negative
    # lookbehind instead of \b so a roll glued to a word char (e.g. a
    # "Grade : A" header immediately before the roll) is still matched.
    roll_pattern = re.compile(r'(?<!\d)(\d{6})\(')

    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)

            print(f"Processing {pdf_path}...")
            print(f"Total pages: {total_pages}")

            for page_num in range(total_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                # Find all roll numbers on this page
                matches = roll_pattern.findall(text)
                roll_numbers.update(matches)

                if (page_num + 1) % 10 == 0:
                    print(f"  Processed {page_num + 1}/{total_pages} pages, found {len(roll_numbers)} unique rolls so far")

            print(f"  Completed! Found {len(roll_numbers)} unique roll numbers")

    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return []

    # Sort roll numbers numerically
    return sorted(roll_numbers, key=lambda x: int(x))


def save_roll_numbers(roll_numbers: list[str], output_file: str):
    """Save roll numbers to a text file (one per line)."""
    with open(output_file, 'w') as f:
        for roll in roll_numbers:
            f.write(f"{roll}\n")
    print(f"\nSaved {len(roll_numbers)} roll numbers to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract roll numbers from BIEK result PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from single PDF
  python extract_rolls_from_pdf.py --pdf pdfs/sg_part2.pdf --output rollNumbers/sg_rolls.txt

  # Extract from all PDFs in a folder
  python extract_rolls_from_pdf.py --folder pdfs --output rollNumbers/all_rolls.txt
        """
    )

    parser.add_argument(
        "--pdf",
        help="Path to a single PDF file"
    )

    parser.add_argument(
        "--folder",
        help="Path to folder containing PDF files"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output text file for roll numbers"
    )

    args = parser.parse_args()

    if not args.pdf and not args.folder:
        parser.error("Please provide either --pdf or --folder")

    all_roll_numbers = set()

    if args.pdf:
        # Process single PDF
        rolls = extract_roll_numbers_from_pdf(args.pdf)
        all_roll_numbers.update(rolls)

    if args.folder:
        # Process all PDFs in folder
        folder_path = Path(args.folder)
        pdf_files = list(folder_path.glob("*.pdf"))

        if not pdf_files:
            print(f"No PDF files found in {args.folder}")
            return

        print(f"Found {len(pdf_files)} PDF files to process")
        print()

        for pdf_file in pdf_files:
            rolls = extract_roll_numbers_from_pdf(str(pdf_file))
            all_roll_numbers.update(rolls)
            print()

    # Sort and save
    sorted_rolls = sorted(all_roll_numbers, key=lambda x: int(x))
    save_roll_numbers(sorted_rolls, args.output)

    # Print summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total unique roll numbers: {len(sorted_rolls)}")
    if sorted_rolls:
        print(f"Range: {sorted_rolls[0]} to {sorted_rolls[-1]}")


if __name__ == "__main__":
    main()
