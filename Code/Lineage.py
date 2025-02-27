import os
import json
import subprocess
from collections import defaultdict
from datetime import datetime
import logging
from typing import Optional, Union

def reformat_name(name: str) -> str:
    """
    Formats a name into 'Title First Middle Last' format, handling titles appropriately.

    Args:
        name (str): The name string to format.

    Returns:
        str: The formatted name or the original name if formatting is not applicable.

    Raises:
        ValueError: If the input is not a string.
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
        return f"{title} {' '.join(rest)}".strip()
    else:
        return title.strip()

def format_name(name: str, format_type: str = "last_first") -> str:
    """
    Formats a name into the specified format.

    Args:
        name (str): The name to format.
        format_type (str): Either "last_first" or "first_last".

    Returns:
        str: Formatted name.
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
            formatted_name = format_name(rest, "last_first")
            return f"{title} {formatted_name}"
        else:
            formatted_name = format_name(rest, "first_last")
            return f"{title} {formatted_name}"
    else:
        return format_name(name, format_type)

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
    article = "an" if nationality.lower()[0] in "aeiou" else "a"
    return f"{name}, {article} {nationality} martial artist from {hometown}, is a student of {student_of}."

def parse_date(date_str: str) -> str:
    """
    Parses a date string into a standard format (YYYY-MM-DD).

    Args:
        date_str (str): The date string to parse.

    Returns:
        str: The parsed date in YYYY-MM-DD format or an error message if invalid.
    """
    if not isinstance(date_str, str):
        logging.error(f"Invalid date input: {date_str}")
        return "Invalid Date Format"

    if not date_str.strip():
        return "No Date Provided"

    formats = ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    logging.error(f"Could not parse date: {date_str}")
    return "Invalid Date Format"

def validate_directory(path: str) -> bool:
    """
    Validates if a directory exists.

    Args:
        path (str): Directory path.

    Returns:
        bool: True if valid, False otherwise.
    """
    if not os.path.exists(path):
        logging.error(f"Directory not found: {path}")
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
        logging.info(f"Created directory: {path}")

def load_bios(bio_dir: str) -> dict:
    """
    Loads bios from text files in a specified directory.

    Args:
        bio_dir (str): Path to the directory containing bio files.

    Returns:
        dict: A dictionary of teacher bios.
    """
    bios = {}
    if not validate_directory(bio_dir):
        logging.error(f"Bios directory not found at {bio_dir}.")
        return bios

    for filename in os.listdir(bio_dir):
        if filename.endswith(".txt"):
            teacher_name = os.path.splitext(filename)[0].replace("_", " ")
            teacher_name = reformat_name(teacher_name)
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
            except FileNotFoundError:
                logging.error(f"Bio file not found: {bio_path}")
            except PermissionError:
                logging.error(f"Permission denied for bio file: {bio_path}")
            except Exception as e:
                logging.error(f"Error reading bio file {bio_path}: {e}")
    return bios

def parse_raw_data_with_defaults(raw_data_dir: str, lineage: dict) -> None:
    """
    Parses raw data files from a directory and populates a lineage dictionary.

    Args:
        raw_data_dir (str): Path to the directory containing raw data files.
        lineage (dict): Dictionary to store lineage information.
    """
    if not os.path.isdir(raw_data_dir):
        logging.error(f"Provided path is not a directory: {raw_data_dir}")
        return

    for filename in os.listdir(raw_data_dir):
        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(raw_data_dir, filename)
        logging.info(f"Processing file: {file_path}")

        try:
            with open(file_path, "r") as file:
                for line in file:
                    parsed = parse_line_with_defaults(line)
                    if not parsed:
                        continue

                    teacher = reformat_name(parsed["teacher"])
                    address = parsed["address"]
                    student = parsed["student"]
                    date = parsed["date"]
                    ranking = parsed["ranking"]
                    number = parsed["number"]

                    if teacher not in lineage:
                        lineage[teacher] = {}
                    if address not in lineage[teacher]:
                        lineage[teacher][address] = []
                    lineage[teacher][address].append((student, date, ranking, number))
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
        except PermissionError:
            logging.error(f"Permission denied for file: {file_path}")
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {e}")

    if not lineage:
        logging.warning("Lineage data is empty. Verify input data and parsing logic.")

def parse_line_with_defaults(line: str) -> Optional[dict]:
    """
    Parses a single line from the standardized student list, handling missing fields.

    Args:
        line (str): The line to parse.

    Returns:
        Optional[dict]: Parsed data or None if parsing fails.
    """
    try:
        parts = [x.strip() for x in line.split("|")]
        if len(parts) != 6:
            logging.error(f"Malformed line: {line.strip()}")
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
        logging.error(f"Error parsing line: {line.strip()} - {e}")
        return None

def escape_latex_special_characters(text: str) -> str:
    """
    Escapes special LaTeX characters in text.

    Args:
        text (str): The text to escape.

    Returns:
        str: Text with LaTeX special characters escaped.
    """
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

def format_name_for_latex_table(name: str) -> str:
    """
    Formats name as 'Last, First Middle' for LaTeX tables.

    Args:
        name (str): The name to format.

    Returns:
        str: Formatted name.
    """
    parts = name.split()
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[1]}, {parts[0]}"
    else:
        return f"{parts[-1]}, {' '.join(parts[:-1])}"

def generate_latex_preamble(file, title: str, author: str) -> None:
    """
    Writes the LaTeX document preamble.

    Args:
        file: The file object to write to.
        title (str): Document title.
        author (str): Document author.
    """
    file.write("\\documentclass[oneside]{book}\n")
    file.write("\\usepackage[utf8]{inputenc}\n")
    file.write("\\usepackage{longtable}\n")
    file.write("\\usepackage{hyperref}\n")
    file.write("\\usepackage{makeidx}\n")
    file.write("\\usepackage{graphicx}\n")
    file.write("\\makeindex\n")
    file.write("\\begin{document}\n")
    file.write("\\begin{titlepage}\n")
    file.write("\\begin{center}\n")
    file.write("\\vspace*{1cm}\n")
    file.write("\\Huge \\textbf{Lineage of Grand Master Chong Woong Kim}\\\\[1.5cm]\n")
    file.write(f"\\Large {author}\\\\[1cm]\n")
    file.write("\\normalsize \\today\\\\[2cm]\n")
    file.write("\\includegraphics[width=0.4\\textwidth]{Output/logo/logo.jpg}\n")
    file.write("\\end{center}\n")
    file.write("\\end{titlepage}\n")

def generate_license_section(file) -> None:
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

def generate_introduction_section(file) -> None:
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

def generate_teacher_section(file, teacher: str, bio: dict, lineage: dict, is_first_chapter: bool = False) -> None:
    """
    Generates a LaTeX section for a teacher, including their bio and lineage.

    Args:
        file: The file object to write to.
        teacher (str): Teacher's name.
        bio (dict): Bio details.
        lineage (dict): Lineage data.
        is_first_chapter (bool): Whether this is the first chapter.
    """
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

def generate_student_table(file, address: str, students: list) -> None:
    """
    Generates a LaTeX table for students at a specific address, avoiding extra \hline at the end.

    Args:
        file: The file object to write to.
        address (str): The address.
        students (list): List of student tuples (student, date, ranking, number).
    """
    address_str = escape_latex_special_characters(address)
    file.write(f"\\section*{{{address_str}}}\n")
    file.write("\\begin{longtable}{|c|p{4cm}|p{2.5cm}|p{2.5cm}|p{2.5cm}|}\n")
    file.write("\\hline\n")
    file.write("No. & Student Name & Date & Ranking & Number \\\\ \\hline\n")

    sorted_students = sorted(students, key=lambda s: format_name_for_latex_table(s[0]))
    for idx, (student, date, ranking, number) in enumerate(sorted_students, start=1):
        formatted_name = format_name_for_latex_table(student)
        file.write(f"{idx} & {escape_latex_special_characters(formatted_name)} & "
                   f"{escape_latex_special_characters(date)} & "
                   f"{escape_latex_special_characters(ranking)} & "
                   f"{escape_latex_special_characters(number)} \\\\\n")
        file.write(f"\\index{{{escape_latex_special_characters(formatted_name)}}}\n")
        if idx < len(sorted_students):
            file.write("\\hline\n")
    file.write("\\end{longtable}\n")

def generate_latex(lineage: dict, bios: dict, tex_file: str) -> None:
    """
    Generates a LaTeX document with teacher and student information, including a table of contents.

    Args:
        lineage (dict): Lineage data.
        bios (dict): Bio data.
        tex_file (str): Path to the output TeX file.
    """
    try:
        with open(tex_file, "w") as file:
            # Write preamble, license, and introduction
            generate_latex_preamble(file, "Lineage of Grand Master Chong Woong Kim", "Compiled Lineage Working Group")
            generate_license_section(file)
            generate_introduction_section(file)
            
            # Add table of contents
            file.write("\\clearpage\n")
            file.write("\\tableofcontents\n")
            file.write("\\clearpage\n")

            # Define the Grand Master's name
            grand_master_name = "Grand Master Chong Woong Kim"
            
            # Generate Chapter 1 for Grand Master Chong Woong Kim
            if grand_master_name in lineage:
                generate_teacher_section(file, grand_master_name, bios.get(grand_master_name, {}), lineage, is_first_chapter=True)
                for address, students in lineage[grand_master_name].items():
                    generate_student_table(file, address, students)
                # Remove to prevent reprocessing
                del lineage[grand_master_name]
            else:
                logging.warning(f"'{grand_master_name}' not found in lineage dictionary.")

            # Generate remaining chapters in alphabetical order
            for teacher in sorted(lineage.keys()):
                bio_data = bios.get(teacher, {})
                generate_teacher_section(file, teacher, bio_data, lineage, is_first_chapter=False)
                for address, students in lineage[teacher].items():
                    generate_student_table(file, address, students)

            # Finalize document
            file.write("\\clearpage\n")
            file.write("\\printindex\n")
            file.write("\\end{document}\n")
        logging.info("LaTeX document generated successfully.")
    except IOError as e:
        logging.error(f"Error writing LaTeX file {tex_file}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error generating LaTeX document: {e}")

def compile_latex(tex_file: str, output_dir: str) -> None:
    """
    Compiles a LaTeX document and generates the index.

    Args:
        tex_file (str): Path to the LaTeX file.
        output_dir (str): Directory for the compiled PDF.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        compile_command = ["pdflatex", "-output-directory", output_dir, tex_file]
        makeindex_command = ["makeindex", os.path.join(output_dir, os.path.basename(tex_file).replace(".tex", ".idx"))]

        subprocess.run(compile_command, check=True)
        subprocess.run(makeindex_command, check=True)
        subprocess.run(compile_command, check=True)

        logging.info("LaTeX document compiled successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during LaTeX compilation: {e}")
    except FileNotFoundError:
        logging.error("pdflatex or makeindex not found. Ensure LaTeX is installed.")
    except Exception as e:
        logging.error(f"Unexpected error during compilation: {e}")

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
        logging.error(f"Config file not found: {config_file}")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON in config file: {config_file}")
        return {}
    except Exception as e:
        logging.error(f"Unexpected error loading config: {e}")
        return {}

def main():
    """Main function to orchestrate the lineage document generation."""
    config = load_config("config.json")
    raw_data_dir = config.get("raw_data_dir", "RAW Data")
    bio_dir = config.get("bio_dir", "Bios")
    output_dir = config.get("output_dir", os.getcwd())
    log_file = config.get("log_file", "error_log.txt")
    tex_file = os.path.join(output_dir, "lineage_document.tex")

    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

    try:
        ensure_directory_exists(output_dir)
        lineage = defaultdict(dict)
        bios = load_bios(bio_dir)
        parse_raw_data_with_defaults(raw_data_dir, lineage)
        generate_latex(lineage, bios, tex_file)
        compile_latex(tex_file, output_dir)
        logging.info(f"LaTeX document compiled and saved in: {output_dir}")
    except Exception as e:
        logging.error(f"Unexpected error in main: {e}")
        raise

if __name__ == "__main__":
    main()