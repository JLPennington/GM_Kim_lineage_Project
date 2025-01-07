import os
import json
from collections import defaultdict
from datetime import datetime

def reformat_name(name: str) -> str:
    """
    Formats a name into 'Title Last Name, First Middle' format.
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

    if len(name_parts) < 2:
        return name  # Single-word names

    if " ".join(name_parts[:2]) in valid_titles:
        title = " ".join(name_parts[:2])
        rest = name_parts[2:]
    elif name_parts[0] in valid_titles:
        title = name_parts[0]
        rest = name_parts[1:]
    else:
        title = ""
        rest = name_parts

    if rest and "," in rest[0]:
        return f"{title} {' '.join(rest)}".strip()
    elif rest:
        last_name = rest[-1]
        first_middle = " ".join(rest[:-1])
        return f"{title} {last_name}, {first_middle}".strip()
    else:
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
            teacher_name = os.path.splitext(filename)[0]
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
                        else:
                            log_message(f"Unrecognized line in {filename}: {line.strip()}", log_file, error_code="DATA_WARNING")
                    bios[reformat_name(teacher_name)] = bio_data
            except FileNotFoundError:
                log_message(f"Bio file not found: {bio_path}", log_file, error_code="FILE_NOT_FOUND")
            except Exception as e:
                log_message(f"Error reading bio file {bio_path}: {e}", log_file, error_code="UNKNOWN_ERROR")
    return bios

def parse_raw_data(raw_data_dir: str, lineage: dict, log_file: str) -> None:
    """
    Parses raw data files to populate a lineage dictionary.

    Args:
        raw_data_dir (str): Path to the directory containing raw data files.
        lineage (dict): Dictionary to store lineage information.
        log_file (str): Path to the log file.
    """
    if not validate_directory(raw_data_dir):
        return

    for filename in os.listdir(raw_data_dir):
        file_path = os.path.join(raw_data_dir, filename)
        if not filename.endswith(".txt"):
            continue
        try:
            with open(file_path, "r") as file:
                for line in file:
                    parts = [x.strip() for x in line.split(",")]
                    if len(parts) < 5:
                        log_message(f"Skipping malformed line in {filename}: {line.strip()}", log_file, error_code="DATA_ERROR")
                        continue

                    teacher = reformat_name(parts[0]) or "Unknown Teacher"
                    address = parts[1] or "Unknown Address"
                    student = parts[2] or "Unknown Student"
                    date = parse_date(parts[3])
                    ranking = parts[4] or "Unknown Ranking"
                    number = parts[5] if len(parts) > 5 else "N/A"

                    if teacher not in lineage:
                        lineage[teacher] = {}
                    if address not in lineage[teacher]:
                        lineage[teacher][address] = []
                    lineage[teacher][address].append((student, date, ranking, number))
        except FileNotFoundError:
            log_message(f"File not found: {file_path}", log_file, error_code="FILE_NOT_FOUND")
        except Exception as e:
            log_message(f"Error processing file {file_path}: {e}", log_file, error_code="UNKNOWN_ERROR")

def generate_latex(lineage: dict, bios: dict, tex_file: str, log_file: str, intro_dir: str, license_file: str) -> None:
    """
    Generates a LaTeX document from lineage and bios data.

    Args:
        lineage (dict): Lineage data.
        bios (dict): Teacher bios.
        tex_file (str): Path to the output LaTeX file.
        log_file (str): Path to the log file.
        intro_dir (str): Path to the introduction directory.
        license_file (str): Path to the license file.
    """
    try:
        with open(tex_file, "w") as file:
            # LaTeX document preamble
            file.write("\\documentclass[oneside]{book}\n")
            file.write("\\usepackage[utf8]{inputenc}\n")
            file.write("\\usepackage{longtable}\n")
            file.write("\\title{Lineage of Masters}\n")
            file.write("\\author{Compiled Documentation}\n")
            file.write("\\date{\\today}\n")
            file.write("\\begin{document}\n")
            file.write("\\maketitle\n")

            # License Page
            file.write("\\clearpage\n")
            file.write("\\chapter*{Copyright and License}\n")
            if os.path.exists(license_file):
                with open(license_file, "r") as license_f:
                    license_text = license_f.read()
                file.write(license_text.replace("\n", "\\\\\n") + "\n")
            else:
                log_message(f"License file not found: {license_file}", log_file, error_code="MISSING_LICENSE")
                file.write("License information is unavailable.\n")

            # Table of Contents
            file.write("\\tableofcontents\n")
            file.write("\\clearpage\n")

            # Introduction Section
            intro_file = os.path.join(intro_dir, "intro.txt")
            if os.path.exists(intro_file):
                with open(intro_file, "r") as intro_f:
                    intro_content = intro_f.read()
                file.write("\\chapter*{Introduction}\n")
                file.write(intro_content.replace("\n", "\\\\\n") + "\n")
            else:
                log_message(f"Introduction file not found: {intro_file}", log_file, error_code="MISSING_INTRO")
                file.write("\\chapter*{Introduction}\n")
                file.write("Introduction content is unavailable.\n")

            # Main Content
            for teacher, locations in lineage.items():
                formatted_teacher = format_teacher_name(teacher, "title_first_last")
                file.write(f"\\chapter{{{formatted_teacher}}}\n")
                bio = bios.get(teacher, {})
                if bio:
                    hometown = bio.get("hometown", "Unknown")
                    student_of = bio.get("student_of", "Unknown")
                    nationality = bio.get("nationality", "Unknown")
                    file.write(f"\\textbf{{Hometown}}: {hometown}\\\\\n")
                    file.write(f"\\textbf{{Student of}}: {student_of}\\\\\n")
                    file.write(f"\\textbf{{Nationality}}: {nationality}\\\\\n")
                else:
                    log_message(f"Bio not found for teacher: {teacher}", log_file, error_code="MISSING_BIO")
                    file.write("Bio information is unavailable.\\\\\n")

                for address, students in locations.items():
                    file.write(f"\\section*{{{address}}}\n")
                    file.write("\\begin{longtable}{|c|p{4cm}|p{2.5cm}|p{2.5cm}|p{2.5cm}|}\n")
                    file.write("\\hline\n")
                    file.write("\\textbf{No.} & \\textbf{Student Name} & \\textbf{Date} & \\textbf{Ranking} & \\textbf{Number} \\\hline\n")

                    for idx, (student, date, ranking, number) in enumerate(students, start=1):
                        formatted_student = format_student_name(student, "last_first")
                        file.write(f"{idx} & {formatted_student} & {date} & {ranking} & {number} \\\\ \hline\n")

                    file.write("\\end{longtable}\n")
            file.write("\\end{document}\n")
    except Exception as e:
        log_message(f"Error writing LaTeX file: {e}", log_file, error_code="LATEX_ERROR")

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

def main():
    config = load_config("config.json")

    raw_data_dir = config.get("raw_data_dir", "RAW Data")
    bio_dir = config.get("bio_dir", "Bios")
    intro_dir = config.get("intro_dir", "Introduction")
    output_dir = config.get("output_dir", os.getcwd())
    log_file = config.get("log_file", "error_log.txt")
    tex_file = os.path.join(output_dir, "lineage_document.tex")
    license_file = config.get("license_file", os.path.join(os.path.dirname(os.getcwd()), "LICENSE"))

    ensure_directory_exists(output_dir)

    lineage = defaultdict(dict)
    bios = load_bios(bio_dir, log_file)
    parse_raw_data(raw_data_dir, lineage, log_file)
    generate_latex(lineage, bios, tex_file, log_file, intro_dir, license_file)

    log_message(f"LaTeX document generated at: {tex_file}", log_file, error_code="SUCCESS")

if __name__ == "__main__":
    main()