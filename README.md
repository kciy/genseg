# Genseg
Genseg is a tool to generate a reference FASTA file consisting of all 8 Influenza segments, taken from eight individual files. It outputs a new FASTA file combining the segment files with a new, simple header.

### Requirements
Python 3.x

### Installation
```bash
git clone https://github.com/kciy/genseg
```

### Usage
```bash
usage: gen_segments.py [-h] [-fa FASTA [FASTA ...]]

required arguments:
    -fa FASTA [FASTA ...]   8 Input FASTA Files with one Influenza A virus segment per file

optional arguments:
    -h, --help              Show this help message and exit
```

Each FASTA file must contain a header line that starts with `>` and includes information about the Influenza type (A, B or C) segment, the subtype, the lineage/name of the genome, and the accession number. The sequence must contain only A, T, G and C bases.

### Example
```bash
python3 gen_segments.py -fa seq1.fasta seq2.fasta seq3.fasta seq4.fasta seq5.fasta seq6.fasta seq7.fasta seq8.fasta
```
