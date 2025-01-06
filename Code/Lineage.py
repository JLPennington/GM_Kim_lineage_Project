import os
import subprocess
from collections import defaultdict
from datetime import datetime


def reformat_name(name):
    """
    Reformats a name to: Title Last Name, First Name Middle Name.
    """
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


def parse_date(date_str):
    """
    Parses a date string and returns it in YYYY-MM-DD format.
    """
    if not date_str:
        return "No Date Provided"

    formats = ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return "Invalid Date"


def log_message(message, log_file="error_log.txt"):
    """
    Logs a message to the console and a log file.
    """
    print(message)
    with open(log_file, "a") as log:
        log.write(f"{message}\n")


def load_bios(bio_dir):
    """
    Loads bios for teachers from the Bios subdirectory.
    """
    bios = {}
    if not os.path.exists(bio_dir):
        log_message(f"Error: Bios directory not found at {bio_dir}.")
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
                log_message(f"Error reading bio file {bio_path}: {e}")
    return bios


def parse_raw_data(raw_data_dir, lineage):
    """
    Parses files in the RAW Data directory and populates the lineage dictionary.
    """
    if not os.path.exists(raw_data_dir):
        log_message(f"Error: RAW Data directory not found at {raw_data_dir}.")
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
                        log_message(f"Skipping malformed line in {filename}: {line.strip()}")
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
            log_message(f"Error processing file {file_path}: {e}")


def generate_latex(lineage, bios, tex_file, output_dir):
    """
    Generates a LaTeX document for single-sided printing with proper page numbering.
    """
    try:
        with open(tex_file, "w") as file:
            # LaTeX document preamble for single-sided printing
            file.write("\\documentclass[oneside]{book}\n")
            file.write("\\usepackage[utf8]{inputenc}\n")
            file.write("\\usepackage{longtable}\n")
            file.write("\\usepackage{titlesec}\n")
            file.write("\\titleformat{\\chapter}[display]{\\bfseries\\Huge}{}{0pt}{}[\\vspace{1em}]\n")
            file.write("\\pagestyle{plain}\n")
            file.write("\\begin{document}\n")
            file.write("\\tableofcontents\n")
            file.write("\\clearpage\n")

            # Generate a chapter for each teacher
            for chapter_num, (teacher, locations) in enumerate(lineage.items(), start=1):
                teacher_clean = teacher.strip().rstrip(",")
                file.write(f"\\chapter{{{teacher_clean}}}\n")

                # Add teacher bio if available
                if teacher_clean in bios:
                    bio_data = bios[teacher_clean]
                    hometown = bio_data.get("hometown", "Unknown hometown")
                    student_of = bio_data.get("student_of", "Unknown teacher")
                    nationality = bio_data.get("nationality", "Unknown nationality")
                    file.write(
                        f"{teacher_clean}, a {nationality} martial artist, is from {hometown} and was trained under {student_of}. \n\n"
                    )
                else:
                    log_message(f"Warning: Missing bio for teacher '{teacher_clean}'.")
                    file.write(f"A biography for {teacher_clean} is currently unavailable.\n\n")

                # Generate sections for each address
                for address, students in locations.items():
                    file.write(f"\\section*{{{address}}}\n")
                    file.write("\\begin{longtable}{|c|p{4cm}|p{2.5cm}|p{2.5cm}|p{2.5cm}|}\n")
                    file.write("\\hline\n")
                    file.write("\\textbf{No.} & \\textbf{Student Name} & \\textbf{Date} & \\textbf{Ranking} & \\textbf{Number} \\\\\n")
                    file.write("\\hline\n")
                    file.write("\\endhead\n")

                    # Add rows of student data
                    for idx, (student, date, ranking, number) in enumerate(students, start=1):
                        file.write(f"{idx} & {student} & {date} & {ranking} & {number} \\\\\n")
                        file.write("\\hline\n")

                    file.write("\\end{longtable}\n")
                    file.write("\\vspace{1em}\n")  # Add spacing after each table

            file.write("\\end{document}\n")
        print(f"LaTeX document generated at: {tex_file}")
    except Exception as e:
        log_message(f"Error writing LaTeX file: {e}")


def generate_pdf(tex_file, output_dir):
    """
    Compiles the LaTeX file into a PDF using pdflatex.
    """
    try:
        print(f"Compiling {tex_file} into a PDF...")
        result = subprocess.run(
            ["pdflatex", "-output-directory", output_dir, tex_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            print(f"PDF successfully generated at {os.path.join(output_dir, 'lineage_document.pdf')}")
        else:
            print(f"PDF generation failed:\n{result.stdout}\n{result.stderr}")
    except FileNotFoundError:
        print("Error: 'pdflatex' is not installed or not found in the PATH.")
    except Exception as e:
        print(f"An error occurred during PDF generation: {e}")


if __name__ == "__main__":
    current_dir = os.getcwd()
    raw_data_dir = os.path.join(current_dir, "RAW Data")
    bio_dir = os.path.join(current_dir, "Bios")
    output_dir = os.path.dirname(current_dir)
    tex_file = os.path.join(output_dir, "lineage_document.tex")
    log_file = os.path.join(output_dir, "error_log.txt")

    if os.path.exists(log_file):
        os.remove(log_file)

    lineage = defaultdict(dict)
    bios = load_bios(bio_dir)
    parse_raw_data(raw_data_dir, lineage)

    print("Generating LaTeX document...")
    generate_latex(lineage, bios, tex_file, output_dir)

    print("Compiling LaTeX document to PDF...")
    generate_pdf(tex_file, output_dir)