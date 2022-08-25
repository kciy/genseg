#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
usage: gen_segments.py [-h] [-fa FASTA [FASTA ...]]

required arguments:
    -fa FASTA [FASTA ...]   8 FASTA Files with one Influenza A virus segment per file

optional arguments:
    -h, --help              Show this help message and exit
"""

import sys
import argparse
import os
import pygenseg as sg


def main(args):
    if len(args.fasta) != 8:
        print("Error: Need exactly 8 FASTA Files, one for each segment")
        sys.exit(1)

    segments = sg.validate_fastas(args.fasta)
    if not sg.all_segments_exist(segments):
        sys.exit(1)

    found_segments = sg.generate_header(segments)
    new_files = sg.apply_header(found_segments)
    fasta = sg.output_fasta(new_files)
    print("Generated " + fasta + ". Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate fasta from segments")
    parser.add_argument("-fa", "--fasta", nargs="+", type=str, help="Input 8 FASTA files", required=True)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    for i in range(len(args.fasta)):
        if not os.path.exists(args.fasta[i]):
            print("Error: %s does not exist" % args.fasta[i])
            sys.exit(1)

    main(args)
