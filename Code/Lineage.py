import os
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

def log_message(message: str, log_file: str = "error_log.txt") -> None:
    """
    Logs a message to the console and a log file.

    Args:
        message (str): The message to log.
        log_file (str): The path to the log file.
    """
    with open(log_file, "a") as log:
        log.write(f"{message}\n")



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
    if not os.path.exists(bio_dir):
        log_message(f"Error: Bios directory not found at {bio_dir}.", log_file)
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
                            bio_data["hometown"] = line.replace("Hometown:", "").strip()
                        elif line.startswith("Student of:"):
                            bio_data["student_of"] = line.replace("Student of:", "").strip()
                        elif line.startswith("Nationality:"):
                            bio_data["nationality"] = line.replace("Nationality:", "").strip()
                    bios[teacher_name] = bio_data
            except Exception as e:
                log_message(f"Error reading bio file {bio_path}: {e}", log_file)
    return bios

def parse_raw_data(raw_data_dir: str, lineage: dict, log_file: str) -> None:
    """
    Parses raw data files to populate a lineage dictionary.

    Args:
        raw_data_dir (str): Path to the directory containing raw data files.
        lineage (dict): Dictionary to store lineage information.
        log_file (str): Path to the log file.
    """
    if not os.path.exists(raw_data_dir):
        log_message(f"Error: RAW Data directory not found at {raw_data_dir}.", log_file)
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
                        log_message(f"Skipping malformed line in {filename}: {line.strip()}", log_file)
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
        except Exception as e:
            log_message(f"Error processing file {file_path}: {e}", log_file)

def generate_latex(lineage: dict, bios: dict, tex_file: str, output_dir: str, intro_dir: str, license_file: str) -> None:
    """
    Generates a LaTeX document from lineage and bios data.

    Args:
        lineage (dict): Lineage data.
        bios (dict): Teacher bios.
        tex_file (str): Path to the output LaTeX file.
        output_dir (str): Path to the output directory.
        intro_dir (str): Path to the introduction files.
        license_file (str): Path to the license file.
    """
    try:
        with open(tex_file, "w") as file:
            # LaTeX document preamble
            file.write("\\documentclass[oneside]{book}\n")
            file.write("\\usepackage[utf8]{inputenc}\n")
            file.write("\\usepackage{longtable}\n")
            file.write("\\usepackage{titlesec}\n")
            file.write("\\titleformat{\\chapter}[display]{\\bfseries\\Huge}{}{0pt}{}[\\vspace{1em}]\n")
            file.write("\\begin{document}\n")
            
            # Title Page
            file.write("\\begin{titlepage}\n")
            file.write("\\pagestyle{empty}\n")
            file.write("\\centering\n")
            file.write("{\\Huge Lineage of Grand Master Chong Woong Kim}\\par\n")
            file.write("\\vspace{2cm}\n")
            file.write("{\\Large Documented and Compiled}\\par\n")
            file.write("\\vfill\n")
            file.write("{\\large \\today}\n")
            file.write("\\end{titlepage}\n")
            
            # License Page
            file.write("\\clearpage\n")
            file.write("\\pagestyle{empty}\n")
            file.write("\\chapter*{Copyright and License}\n")
            if os.path.exists(license_file):
                with open(license_file, "r") as license_f:
                    license_text = license_f.read()
                file.write(license_text.replace("\n", "\n\n"))
            else:
                log_message(f"Warning: License file not found at {license_file}.", "error_log.txt")
                file.write("License information is currently unavailable.\n")

            # Introduction Section
            intro_file = os.path.join(intro_dir, "intro.txt")
            if os.path.exists(intro_file):
                with open(intro_file, "r") as intro_f:
                    intro_content = intro_f.read()
                file.write("\\clearpage\n")
                file.write("\\chapter*{Introduction}\n")
                file.write(intro_content.replace("\n", "\n\n") + "\n")
            else:
                log_message(f"Warning: Introduction file not found at {intro_file}.", "error_log.txt")
                file.write("\\clearpage\n")
                file.write("\\chapter*{Introduction}\n")
                file.write("Introduction content is currently unavailable.\n")

            # Table of Contents
            file.write("\\clearpage\n")
            file.write("\\pagestyle{plain}\n")
            file.write("\\tableofcontents\n")
            file.write("\\clearpage\n")
            file.write("\\pagenumbering{arabic}\n")

            for chapter_num, (teacher, locations) in enumerate(lineage.items(), start=1):
                teacher_clean = teacher.strip().rstrip(",")
                file.write(f"\\chapter{{{teacher_clean}}}\n")
                bio = bios.get(teacher_clean, {})
                if bio:
                    hometown = bio.get("hometown", "Unknown")
                    student_of = bio.get("student_of", "Unknown")
                    nationality = bio.get("nationality", "Unknown")
                    bio_paragraph = (
                        f"{teacher_clean} is originally from {hometown}. "
                        f"They studied under {student_of} and hold {nationality} nationality."
                    )
                    file.write(f"\\section*{{Biography}}\n{bio_paragraph}\n")
                else:
                    log_message(f"Warning: Bio not found for teacher {teacher_clean}.", "error_log.txt")

                for address, students in locations.items():
                    file.write(f"\\section*{{{address}}}\n")
                    file.write("\\begin{longtable}{|c|p{4cm}|p{2.5cm}|p{2.5cm}|p{2.5cm}|}\n")
                    file.write("\\hline\n")
                    file.write("\\textbf{No.} & \\textbf{Student Name} & \\textbf{Date} & \\textbf{Ranking} & \\textbf{Number} \\\\\n")
                    file.write("\\hline\n")
                    file.write("\\endhead\n")
                    for idx, (student, date, ranking, number) in enumerate(students, start=1):
                        file.write(f"{idx} & {student} & {date} & {ranking} & {number} \\\n")
                        file.write("\\hline\n")
                    file.write("\\end{longtable}\n")
            file.write("\\end{document}\n")
    except Exception as e:
        log_message(f"Error writing LaTeX file: {e}", "error_log.txt")

if __name__ == "__main__":
    current_dir = os.getcwd()
    raw_data_dir = os.path.join(current_dir, "RAW Data")
    bio_dir = os.path.join(current_dir, "Bios")
    intro_dir = os.path.join(current_dir, "Introduction")
    output_dir = os.path.dirname(current_dir)
    tex_file = os.path.join(output_dir, "lineage_document.tex")
    log_file = os.path.join(output_dir, "error_log.txt")
    license_file = os.path.join(os.path.dirname(current_dir), "LICENSE")

    # Clear the error log at the start
    if os.path.exists(log_file):
        os.remove(log_file)

    lineage = defaultdict(dict)
    bios = load_bios(bio_dir, log_file)

    if not os.path.exists(raw_data_dir):
        log_message(f"RAW Data directory not found: {raw_data_dir}", log_file)
    if not os.path.exists(bio_dir):
        log_message(f"Bios directory not found: {bio_dir}", log_file)
    if not os.path.exists(intro_dir):
        log_message(f"Introduction directory not found: {intro_dir}", log_file)
    if not os.path.exists(license_file):
        log_message(f"License file not found: {license_file}", log_file)

    parse_raw_data(raw_data_dir, lineage, log_file)

    generate_latex(lineage, bios, tex_file, output_dir, intro_dir, license_file)

    log_message(f"LaTeX document generated at: {tex_file}", log_file)
    log_message(f"Error log can be found at: {log_file}", log_file)
