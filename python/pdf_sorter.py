#!/usr/bin/env python3
"""
PDF Duplex Scanner Sorter
Reorders pages from a non-duplex scanner where you've scanned
fronts first, then flipped the stack and scanned backs.
"""

import sys
import argparse
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def reorder_pages(input_pdf: str, output_pdf: str) -> None:
    """
    Reorder pages from duplex scanning.
    
    Args:
        input_pdf: Path to input PDF file
        output_pdf: Path to output PDF file
    """
    # Read the input PDF
    reader = PdfReader(input_pdf)
    total_pages = len(reader.pages)

    if total_pages < 2:
        print(f"Warning: PDF has only {total_pages} page(s). Nothing to reorder.")
        return

    # Calculate midpoint
    midpoint = (total_pages + 1) // 2

    # Front pages are the first half
    front_pages = list(range(0, midpoint))

    # Back pages are the second half, reversed
    back_pages = list(range(midpoint, total_pages))
    back_pages.reverse()

    print(f"Total pages: {total_pages:,}")
    print(f"Front pages: {len(front_pages):,}")
    print(f"Back pages: {len(back_pages):,}")

    # Create output PDF
    writer = PdfWriter()

    # Interleave front and back pages
    for i in range(max(len(front_pages), len(back_pages))):
        if i < len(front_pages):
            writer.add_page(reader.pages[front_pages[i]])
            print(f"Adding page {front_pages[i] + 1} (front)")

        if i < len(back_pages):
            writer.add_page(reader.pages[back_pages[i]])
            print(f"Adding page {back_pages[i] + 1} (back)")

    # Write output
    with open(output_pdf, 'wb') as output_file:
        writer.write(output_file)

    print(f"\nSuccess! Reordered PDF saved to: {output_pdf}")


def main():
    parser = argparse.ArgumentParser(
        description='Reorder PDF pages from non-duplex scanner scanning',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  %(prog)s input.pdf output.pdf
  %(prog)s scanned.pdf sorted.pdf

How it works:
  1. Scan all front pages (1, 2, 3, 4, 5...)
  2. Flip your entire stack over
  3. Scan all back pages (now in reverse order)
  4. Run this tool to interleave them correctly
        """,
    )

    parser.add_argument('input', help='Input PDF file')
    parser.add_argument('output', help='Output PDF file')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')

    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)

    if not input_path.suffix.lower() == '.pdf':
        print(f"Error: Input file must be a PDF.")
        sys.exit(1)

    # Prevent overwriting input file
    output_path = Path(args.output)
    if input_path.resolve() == output_path.resolve():
        print("Error: Output file cannot be the same as input file.")
        sys.exit(1)

    try:
        reorder_pages(args.input, args.output)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
