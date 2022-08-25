import re
import os
from typing import List


def validate_fastas(fastas: List[str]) -> List[dict]:
    """ Checks if there is a fasta for each of the 8 segments """
    segments = [
        {"segment": ["PB2"], "present": False, "file": None, "header": ""},
        {"segment": ["PB1", "PB1-F2"], "present": False, "file": None, "header": ""},
        {"segment": ["PA"], "present": False, "file": None, "header": ""},
        {"segment": ["HA"], "present": False, "file": None, "header": ""},
        {"segment": ["NP"], "present": False, "file": None, "header": ""},
        {"segment": ["NA"], "present": False, "file": None, "header": ""},
        {"segment": ["M1", "M2"], "present": False, "file": None, "header": ""},
        {"segment": ["NS1", "NEP"], "present": False, "file": None, "header": ""}
    ]

    for fa in fastas:
        found = False
        with open(fa, "r") as file:
            content_lines = file.readlines()
            lower_sequence = False
            for line in content_lines[1:]:  # sequence consists of A, T, G, C only
                if re.search(r'\b^[atgc \n]+$', line) and not lower_sequence:
                    print(f"Warning: {fa} contains lowercase ATGC characters and will be converted to uppercase")
                    lower_sequence = True
                elif not re.search(r'^[ATGC \n]+$', line) and not lower_sequence:
                    print(f"Warning: {fa} contains non-ATGC characters")

            if lower_sequence:
                to_uppercase(fa)

            for pos, segment in enumerate(segments):
                pos += 1
                if found == False and segment["present"] == False:
                    header_line = content_lines[0]
                    if re.search(r'\bsegment ' + str(pos) + r'\b', header_line.lower()):  # e.g. "segment 4"
                        segment["present"] = True
                        segment["file"] = fa
                        segment["segment"] = segment["segment"][0]
                        found = True
                    else:
                        for s in segment["segment"]:
                            if re.search(r'\b' + s + r'(?!-)\b', header_line) and found == False: # e.g. "PB1"
                                segment["present"] = True
                                segment["file"] = fa
                                segment["segment"] = s
                                found = True

    return segments


def to_uppercase(file_name: str) -> str:
    """ Convert fasta sequence to uppercase """
    with open(file_name, "r") as file:
        content_lines = file.readlines()
        uppercase_content_lines = [line.upper() for line in content_lines if not line.startswith(">")]
        uppercase_content_lines.insert(0, content_lines[0])
    
    if os.path.exists(file_name):
        delete_files([file_name])
    with open(file_name, "w") as file:
        file.writelines(uppercase_content_lines)
    
    return file_name


def all_segments_exist(segments: List[dict]) -> bool:
    """ Check if all segments are present """
    for segment in range(len(segments)):
        if not segments[segment]["present"]:
            print("Error: One of " + str(segments[segment]["segment"]) + " does not exist")
            return False

    return True


def generate_header(segments_dict: List[dict]) -> List[dict]:
    """ Generates header line for each segment.
    Returns a list of header lines in order of segments.

    >Position of segment | Segment | Genome | Subtype | Accession number

    E.g.:
    >1 | PB2 | A/Hawaii/70/2019 | H1N1 | MN976431.1
    """
    for pos, segment in enumerate(segments_dict):
        position = pos + 1
        segment_name = segment["segment"]
        with open(segment["file"], "r") as file:
            header_line = file.readline()
            genome = re.search(r'[A|B|C]\/[\w]+\ *[\w]*[\/[\w]*]*\/\S*\/[0-9]{4}', header_line)
            subtype = re.search(r'\bH[0-9]+N[0-9]+\b', header_line)
            accession = re.search(r'\b[A-Z]{2}[0-9]{6}[.[0-9]*', header_line)

        genome = genome.group() if genome else ""
        subtype = subtype.group() if subtype else ""
        accession = accession.group() if accession else ""
        if any(string == "" for string in [position, segment_name, genome, subtype, accession]):
            print("Warning: fasta file does not contain all information for header")
        segment["header"] = f">{position} | {segment_name} | {genome} | {subtype} | {accession}"

    return segments_dict


def apply_header(segments: List[dict]) -> List[str]:
    """ Modify each file: replace the header line and bring sequence in one line"""
    modified_fasta_filenames = []
    for segment in segments:
        with open(segment["file"], "r") as file:
            content_lines = file.readlines()
            content_lines.remove(content_lines[0])

            seq_lines_strip = [line.replace("\n", "") for line in content_lines]

            sequence_one_line = []
            if len(seq_lines_strip) > 1:
                sequence_one_line = "".join(d for d in seq_lines_strip)

            new_lines = []
            new_lines.append(segment["header"] + '\n')
            new_lines.append(sequence_one_line + '\n')

            new_fasta = os.path.basename(segment["file"]) + "_sg.fasta"
            modified_fasta_filenames.append(new_fasta)

            with open(new_fasta, "w") as file:
                file.writelines(new_lines)

    return modified_fasta_filenames


def output_fasta(all_files: List[str]) -> str:
    """ Generate output fasta by concatenating all fasta files with new header """
    all_fastas_file = "all_sg.fasta"
    if os.path.isfile(all_fastas_file):
        print("Warning: overwriting existing file: " + all_fastas_file)
        delete_files([all_fastas_file])
    for file in all_files:
        with open(file, "r") as file:
            content = file.readlines()
            with open(all_fastas_file, "a+") as file:
                file.writelines("%s" % line for line in content)

    delete_files(all_files)
    remove_last_newline(all_fastas_file)

    return all_fastas_file


def delete_files(files: List[str]):
    """ Delete files for cleanup """
    for file in files:
        if os.path.isfile(file):
            os.remove(file)


def remove_last_newline(all_fastas_file: str) -> None:
    """ Remove last (empty) line from all_fastas_file """
    with open(all_fastas_file, "r") as file:
        content = file.readlines()
        last = content[-1].replace("\n", "")

        content.pop()
        content.append(last)

        with open(all_fastas_file, "w") as file:
            file.writelines("%s" % line for line in content)
