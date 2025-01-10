import os
import json
import subprocess
from collections import defaultdict
from datetime import datetime
from collections import defaultdict

def reformat_name(name: str) -> str:
    """
    Formats a name into 'Title First Middle Last' format.
    Handles titles and ensures proper name structure.

    Args:
        name (str): The name string to format.

    Returns:
        str: The formatted name or the original name if formatting is not applicable.
    """
    if not isinstance(name, str):
        raise ValueError("Input must be a string.")

    name = name.strip().rstrip(",")
    name_parts = name.split()
    valid_titles = {"Grand Master", "Master", "Mr.", "Ms.", "Mrs."}

    # Handle multi-word and single-word titles
    if len(name_parts) > 1 and " ".join(name_parts[:2]) in valid_titles:
        title = " ".join(name_parts[:2])  # Multi-word title
        rest = name_parts[2:]
    elif name_parts[0] in valid_titles:
        title = name_parts[0]  # Single-word title
        rest = name_parts[1:]
    else:
        title = ""
        rest = name_parts

    if rest:
        # Preserve the rest of the name in correct order
        return f"{title} {' '.join(rest)}".strip()
    else:
        # Only a title with no additional name parts
        return title.strip()


def format_student_name(name: str, format_type: str = "last_first") -> str:
    """
    Formats a student's name into the desired format.

    Args:
        name (str): The student's name.
        format_type (str): Either "last_first" or "first_last".

    Returns:
        str: Formatted student name.
    """
    name = name.strip().rstrip(",")
    if "," in name:
        last, first_middle = [part.strip() for part in name.split(",", 1)]
        if format_type == "last_first":
            return f"{last}, {first_middle}"
        else:
            return f"{first_middle} {last}"
    else:
        parts = name.split()
        if format_type == "last_first":
            return f"{parts[-1]}, {' '.join(parts[:-1])}"
        else:
            return f"{' '.join(parts[:-1])} {parts[-1]}"

def format_teacher_name(name: str, format_type: str = "title_first_last") -> str:
    """
    Formats a teacher's name with title into the desired format.

    Args:
        name (str): The teacher's name.
        format_type (str): Either "last_first", "first_last", or "title_first_last".

    Returns:
        str: Formatted teacher name with title.
    """
    name = name.strip().rstrip(",")
    titles = {"Grand Master", "Master", "Mr.", "Ms.", "Mrs."}
    parts = name.split()

    if len(parts) > 1 and parts[0] in titles:
        title = parts[0]
        rest = " ".join(parts[1:])
        if format_type == "title_first_last":
            return f"{title} {rest}"
        elif format_type == "last_first":
            formatted_name = format_student_name(rest, "last_first")
            return f"{title} {formatted_name}"
        else:
            formatted_name = format_student_name(rest, "first_last")
            return f"{title} {formatted_name}"
    else:
        return format_student_name(name, format_type)

def generate_bio_paragraph(name: str, bio: dict) -> str:
    """
    Generates a paragraph for the instructor bio.

    Args:
        name (str): The instructor's name.
        bio (dict): The bio details, including hometown, student_of, and nationality.

    Returns:
        str: A paragraph summarizing the instructor's bio.
    """
    hometown = bio.get("hometown", "an unknown location")
    student_of = bio.get("student_of", "an unknown instructor")
    nationality = bio.get("nationality", "unknown")

    # Determine the correct article ("a" or "an") based on the nationality
    article = "an" if nationality.lower()[0] in "aeiou" else "a"

    return (
        f"{name}, {article} {nationality} martial artist from {hometown}, is a student of {student_of}."
    )

def generate_index(names_with_pages: dict, file) -> None:
    """
    Generates an index for all names with page numbers.

    Args:
        names_with_pages (dict): A dictionary mapping names to page numbers.
        file: The LaTeX file object to write the index into.
    """
    file.write("\\chapter{Index}\\n")
    file.write("\\begin{longtable}{|p{6cm}|p{8cm}|}\\n")
    file.write("\\hline\\n")
    file.write("\\textbf{Name} & \\textbf{Page Numbers} \\\\\\ \\hline\\n")

    for name, pages in sorted(names_with_pages.items()):
        pages_str = ", ".join(map(str, sorted(pages)))
        file.write(f"{name} & {pages_str} \\\\\\ \\hline\\n")

    file.write("\\end{longtable}\\n")


def parse_date(date_str: str) -> str:
    """
    Parses a date string into a standard format (YYYY-MM-DD).
    Handles multiple input formats and returns a default message for invalid inputs.

    Args:
        date_str (str): The date string to parse.

    Returns:
        str: The parsed date in YYYY-MM-DD format or an error message if invalid.
    """
    if not isinstance(date_str, str):
        return "Invalid Date Format"

    if not date_str.strip():
        return "No Date Provided"

    formats = ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return "Invalid Date Format"

def log_message(message: str, log_file: str = "error_log.txt", error_code: str = "INFO") -> None:
    """
    Logs a message to the console and a log file.

    Args:
        message (str): The message to log.
        log_file (str): The path to the log file.
        error_code (str): Error category or code.
    """
    with open(log_file, "a") as log:
        log.write(f"[{datetime.now()}] [{error_code}] {message}\n")

def validate_directory(path: str) -> bool:
    """
    Validates if a directory exists.

    Args:
        path (str): Directory path.

    Returns:
        bool: True if valid, False otherwise.
    """
    if not os.path.exists(path):
        log_message(f"Directory not found: {path}", error_code="ERROR")
        return False
    return True

def ensure_directory_exists(path: str) -> None:
    """
    Ensures a directory exists by creating it if necessary.

    Args:
        path (str): Directory path.
    """
    if not os.path.exists(path):
        os.makedirs(path)
        log_message(f"Created directory: {path}", error_code="INFO")

def load_bios(bio_dir: str, log_file: str) -> dict:
    """
    Loads bios from text files in a specified directory.

    Args:
        bio_dir (str): Path to the directory containing bio files.
        log_file (str): Path to the log file.

    Returns:
        dict: A dictionary of teacher bios.
    """
    bios = {}
    if not validate_directory(bio_dir):
        log_message(f"Error: Bios directory not found at {bio_dir}.", log_file, error_code="MISSING_DIR")
        return bios

    for filename in os.listdir(bio_dir):
        if filename.endswith(".txt"):
            # Normalize the teacher's name by replacing underscores with spaces
            teacher_name = os.path.splitext(filename)[0].replace("_", " ")
            teacher_name = reformat_name(teacher_name)  # Ensure consistent formatting
            bio_path = os.path.join(bio_dir, filename)
            try:
                with open(bio_path, "r") as bio_file:
                    bio_data = {}
                    for line in bio_file:
                        if line.startswith("Hometown:"):
                            bio_data["hometown"] = line.replace("Hometown:", "").strip() or "Unknown"
                        elif line.startswith("Student of:"):
                            bio_data["student_of"] = line.replace("Student of:", "").strip() or "Unknown"
                        elif line.startswith("Nationality:"):
                            bio_data["nationality"] = line.replace("Nationality:", "").strip() or "Unknown"
                    bios[teacher_name] = bio_data
            except Exception as e:
                log_message(f"Error reading bio file {bio_path}: {e}", log_file, error_code="UNKNOWN_ERROR")
    return bios


import os
import json

def parse_raw_data_with_defaults(raw_data_dir, lineage, log_file):
    """
    Parses raw data files from a directory and populates a lineage dictionary.

    Args:
        raw_data_dir (str): Path to the directory containing raw data files.
        lineage (dict): Dictionary to store lineage information.
        log_file (str): Path to the log file.
    """
    # Ensure the provided path is a directory
    if not os.path.isdir(raw_data_dir):
        log_message(f"Provided path is not a directory: {raw_data_dir}", log_file, error_code="INVALID_PATH")
        return

    try:
        for filename in os.listdir(raw_data_dir):
            # Skip non-text files
            if not filename.endswith(".txt"):
                continue

            file_path = os.path.join(raw_data_dir, filename)
            print(f"Processing file: {file_path}")  # Debugging: Show which file is being processed

            with open(file_path, "r") as file:
                for line in file:
                    parsed = parse_line_with_defaults(line, log_file)
                    if not parsed:
                        continue

                    teacher = reformat_name(parsed["teacher"])
                    address = parsed["address"]
                    student = parsed["student"]
                    date = parsed["date"]
                    ranking = parsed["ranking"]
                    number = parsed["number"]

                    # Ensure teacher exists in lineage
                    if teacher not in lineage:
                        lineage[teacher] = {}

                    # Ensure address exists under teacher
                    if address not in lineage[teacher]:
                        lineage[teacher][address] = []

                    # Add student data to the teacher's address entry
                    lineage[teacher][address].append((student, date, ranking, number))

        # Debugging: Print lineage data
        print("Lineage Data after Parsing:")
        print(json.dumps(lineage, indent=2))
        if not lineage:
            log_message("Lineage data is empty. Verify input data and parsing logic.", log_file, error_code="EMPTY_DATA")
    except Exception as e:
        log_message(f"Error processing directory {raw_data_dir}: {e}", log_file, error_code="UNKNOWN_ERROR")


def parse_line_with_defaults(line, log_file):
    """Parses a single line from the standardized student list, handling missing fields."""
    try:
        parts = [x.strip() for x in line.split("|")]
        if len(parts) != 6:
            log_message(f"Malformed line: {line.strip()}", log_file, error_code="DATA_ERROR")
            return None

        return {
            "teacher": parts[0] or "Unknown Teacher",
            "address": parts[1] or "Unknown Address",
            "student": parts[2] or "Unknown Student",
            "date": parts[3] or "Unknown Date",
            "ranking": parts[4] or "Unknown Ranking",
            "number": parts[5] or "N/A",
        }
    except Exception as e:
        log_message(f"Error parsing line: {line.strip()} - {e}", log_file, error_code="PARSE_ERROR")
        return None



import subprocess
import os
from collections import defaultdict

def escape_latex_special_characters(text):
    """Escapes special LaTeX characters in text."""
    if not isinstance(text, str):
        text = str(text)
    special_chars = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
        '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}', '\\': r'\textbackslash{}'
    }
    for char, escape in special_chars.items():
        text = text.replace(char, escape)
    return text

def format_student_name(name):
    """Formats student name as Last name, First name Middle name."""
    parts = name.split()
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[1]}, {parts[0]}"
    else:
        return f"{parts[-1]}, {' '.join(parts[:-1])}"

def generate_latex_preamble(file, title, author):
    """Writes the LaTeX document preamble."""
    file.write("\\documentclass[oneside]{book}\n")
    file.write("\\usepackage[utf8]{inputenc}\n")
    file.write("\\usepackage{longtable}\n")
    file.write("\\usepackage{hyperref}\n")
    file.write("\\usepackage{makeidx}\n")
    file.write("\\makeindex\n")
    file.write(f"\\title{{{title}}}\n")
    file.write(f"\\author{{{author}}}\n")
    file.write("\\date{\\today}\n")
    file.write("\\begin{document}\n")
    file.write("\\maketitle\n")

def generate_license_section(file):
    """Writes the license section."""
    license_text = (
        "This document is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 "
        "International License. You are free to share and adapt the material under the following terms: "
        "give appropriate credit, do not use it for commercial purposes, and distribute your contributions "
        "under the same license."
    )
    file.write("\\clearpage\n")
    file.write("\\chapter*{Copyright and License}\n")
    file.write(escape_latex_special_characters(license_text) + "\n")

def generate_introduction_section(file):
    """Writes the introduction section."""
    introduction_text = (
        "Welcome to the lineage document of Grand Master Chong Woong Kim. This work seeks to preserve "
        "and share the profound legacy of a martial artist who has touched countless lives. Through these "
        "pages, we explore the connections, stories, and achievements of students and teachers who form an "
        "unbroken chain of knowledge and tradition."
    )
    file.write("\\clearpage\n")
    file.write("\\chapter*{Introduction}\n")
    file.write(escape_latex_special_characters(introduction_text) + "\n")

def generate_teacher_section(file, teacher, bio, lineage, is_first_chapter=False):
    """Generates a LaTeX section for a teacher, including their bio and lineage."""
    teacher_str = escape_latex_special_characters(teacher)
    file.write(f"\\chapter{{{teacher_str}}}\n")
    file.write(f"\\index{{{teacher_str}}}\n")

    if is_first_chapter:
        hardcoded_bio = (
            "Grand Master Chong Woong Kim is a distinguished martial artist whose legacy is rooted in his "
            "dedication to Taekwondo and his profound impact on students worldwide. Born in Seoul, South Korea, "
            "Grand Master Kim has spent decades sharing his expertise and fostering respect, discipline, and "
            "excellence in martial arts."
        )
        file.write(escape_latex_special_characters(hardcoded_bio) + "\n\n")
    else:
        nationality = bio.get('nationality', 'Unknown')
        article = "an" if nationality.lower()[0] in "aeiou" else "a"
        formatted_bio = (
            f"{teacher}, {article} {nationality} martial artist, from {bio.get('hometown', 'Unknown')}. "
            f"A student of {bio.get('student_of', 'Unknown')}."
        )
        file.write(escape_latex_special_characters(formatted_bio) + "\n\n")

def generate_student_table(file, address, students):
    """Generates a LaTeX table for students at a specific address."""
    address_str = escape_latex_special_characters(address)
    file.write(f"\\section*{{{address_str}}}\n")
    file.write("\\begin{longtable}{|c|p{4cm}|p{2.5cm}|p{2.5cm}|p{2.5cm}|}\n")
    file.write("\\hline\n")
    file.write("No. & Student Name & Date & Ranking & Number \\\\ \\hline\n")

    sorted_students = sorted(students, key=lambda s: format_student_name(s[0]))
    for idx, (student, date, ranking, number) in enumerate(sorted_students, start=1):
        formatted_name = format_student_name(student)
        file.write(f"{idx} & {escape_latex_special_characters(formatted_name)} & "
                   f"{escape_latex_special_characters(date)} & "
                   f"{escape_latex_special_characters(ranking)} & "
                   f"{escape_latex_special_characters(number)} \\\\ \\hline\n")
        file.write(f"\\index{{{escape_latex_special_characters(formatted_name)}}}\n")  # Add student to index
    file.write("\\end{longtable}\n")

def generate_latex(lineage, bios, tex_file, log_file):
    """Generates a LaTeX document with teacher and student information."""
    try:
        with open(tex_file, "w") as file:
            generate_latex_preamble(file, "Lineage of Grand Master Chong Woong Kim", "Compiled Lineage Working Group")
            generate_license_section(file)
            generate_introduction_section(file)

            for idx, (teacher, locations) in enumerate(lineage.items()):
                bio_data = bios.get(teacher, {})
                generate_teacher_section(file, teacher, bio_data, lineage, is_first_chapter=(idx == 0))

                for address, students in locations.items():
                    generate_student_table(file, address, students)

            file.write("\\clearpage\n")
            file.write("\\printindex\n")
            file.write("\\end{document}\n")
            print("LaTeX document generated successfully.")
    except Exception as e:
        print(f"Error generating LaTeX document: {e}")

def compile_latex(tex_file, output_dir):
    """Compiles a LaTeX document and generates the index."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        compile_command = ["pdflatex", "-output-directory", output_dir, tex_file]
        makeindex_command = ["makeindex", os.path.join(output_dir, os.path.basename(tex_file).replace(".tex", ".idx"))]

        for _ in range(2):
            subprocess.run(compile_command, check=True)
            subprocess.run(makeindex_command, check=True)
            subprocess.run(compile_command, check=True)

        print("LaTeX document compiled successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during LaTeX compilation: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")







def load_config(config_file: str) -> dict:
    """
    Loads configuration from a JSON file.

    Args:
        config_file (str): Path to the configuration file.

    Returns:
        dict: Configuration dictionary.
    """
    try:
        with open(config_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        log_message(f"Config file not found: {config_file}", error_code="FILE_NOT_FOUND")
        return {}
    except json.JSONDecodeError:
        log_message(f"Error decoding JSON in config file: {config_file}", error_code="JSON_ERROR")
        return {}

import subprocess
import os

def compile_latex(tex_file, output_dir):
    """
    Compiles a LaTeX document and generates the index.

    Args:
        tex_file (str): Path to the LaTeX file to compile.
        output_dir (str): Directory where the compiled PDF will be saved.

    Returns:
        None
    """
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Commands to compile the LaTeX document
        compile_command = ["pdflatex", "-output-directory", output_dir, tex_file]
        makeindex_command = ["makeindex", os.path.join(output_dir, os.path.basename(tex_file).replace(".tex", ".idx"))]

        # Compile LaTeX and generate index twice to ensure proper processing
        for _ in range(2):
            subprocess.run(compile_command, check=True)
            subprocess.run(makeindex_command, check=True)
            subprocess.run(compile_command, check=True)

        print("LaTeX document compiled successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during LaTeX compilation: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def main():
    config = load_config("config.json")

    raw_data_dir = config.get("raw_data_dir", "RAW Data")
    bio_dir = config.get("bio_dir", "Bios")
    output_dir = config.get("output_dir", os.getcwd())
    log_file = config.get("log_file", "error_log.txt")
    tex_file = os.path.join(output_dir, "lineage_document.tex")

    ensure_directory_exists(output_dir)

    lineage = defaultdict(dict)
    bios = load_bios(bio_dir, log_file)
    
    # Process all files in the RAW Data directory
    parse_raw_data_with_defaults(raw_data_dir, lineage, log_file)
    
    # Generate the LaTeX document
    generate_latex(lineage, bios, tex_file, log_file)

    # Compile the LaTeX document
    compile_latex(tex_file, output_dir)

    log_message(f"LaTeX document compiled and saved in: {output_dir}", log_file, error_code="SUCCESS")

if __name__ == "__main__":
    main()


