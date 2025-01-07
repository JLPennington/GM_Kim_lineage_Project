import os
from collections import defaultdict
from datetime import datetime


def reformat_name(name):
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


def generate_latex(lineage, bios, tex_file, output_dir, intro_dir, license_file):
    try:
        with open(tex_file, "w") as file:
            print("Starting LaTeX generation...")
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
            file.write("{\\large \\today}\\par\n")
            file.write("\\end{titlepage}\n")
            
            # License Page
            file.write("\\clearpage\n")
            file.write("\\pagestyle{empty}\n")
            file.write("\\chapter*{Copyright and License}\n")
            if os.path.exists(license_file):
                with open(license_file, "r") as license_f:
                    license_text = license_f.read()
                formatted_license = (
                    "\\textbf{License}\n\n"
                    "This work is licensed under the \\textbf{Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)} license.\n\n"
                    "\\textbf{Permissions:}\n"
                    "\\begin{itemize}\n"
                    "\\item \\textbf{Share} — copy and redistribute the material in any medium or format.\n"
                    "\\item \\textbf{Adapt} — remix, transform, and build upon the material for any purpose, even commercially.\n"
                    "\\end{itemize}\n\n"
                    "\\textbf{Terms:}\n"
                    "\\begin{itemize}\n"
                    "\\item \\textbf{Attribution} — You must give appropriate credit, provide a link to the license, "
                    "and indicate if changes were made. You may do so in any reasonable manner, but not in any way "
                    "that suggests the licensor endorses you or your use.\n"
                    "\\item \\textbf{ShareAlike} — If you remix, transform, or build upon the material, "
                    "you must distribute your contributions under the same license as the original.\n"
                    "\\end{itemize}\n\n"
                    "For more details, visit \\textit{https://creativecommons.org/licenses/by-sa/4.0/}.\n"
                )
                file.write(formatted_license)
            else:
                log_message(f"Warning: License file not found at {license_file}.")
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
                log_message(f"Warning: Introduction file not found at {intro_file}.")
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
                print(f"Processing teacher: {teacher}")
                teacher_clean = teacher.strip().rstrip(",")
                file.write(f"\\chapter{{{teacher_clean}}}\n")
                for address, students in locations.items():
                    print(f"Writing student table for address: {address}")
                    file.write(f"\\section*{{{address}}}\n")
                    file.write("\\begin{longtable}{|c|p{4cm}|p{2.5cm}|p{2.5cm}|p{2.5cm}|}\n")
                    file.write("\\hline\n")
                    file.write("\\textbf{No.} & \\textbf{Student Name} & \\textbf{Date} & \\textbf{Ranking} & \\textbf{Number} \\\\\n")
                    file.write("\\hline\n")
                    file.write("\\endhead\n")
                    for idx, (student, date, ranking, number) in enumerate(students, start=1):
                        file.write(f"{idx} & {student} & {date} & {ranking} & {number} \\\\\n")
                        file.write("\\hline\n")
                    file.write("\\end{longtable}\n")
            file.write("\\end{document}\n")
            print("Completed LaTeX document generation.")
    except Exception as e:
        log_message(f"Error writing LaTeX file: {e}")


if __name__ == "__main__":
    current_dir = os.getcwd()
    raw_data_dir = os.path.join(current_dir, "RAW Data")
    bio_dir = os.path.join(current_dir, "Bios")
    intro_dir = os.path.join(current_dir, "Introduction")
    output_dir = os.path.dirname(current_dir)
    tex_file = os.path.join(output_dir, "lineage_document.tex")
    log_file = os.path.join(output_dir, "error_log.txt")
    license_file = os.path.join(os.path.dirname(current_dir), "LICENSE")

    if os.path.exists(log_file):
        os.remove(log_file)

    lineage = defaultdict(dict)
    bios = load_bios(bio_dir)

    if not os.path.exists(raw_data_dir):
        log_message(f"RAW Data directory not found: {raw_data_dir}")
    if not os.path.exists(bio_dir):
        log_message(f"Bios directory not found: {bio_dir}")
    if not os.path.exists(intro_dir):
        log_message(f"Introduction directory not found: {intro_dir}")
    if not os.path.exists(license_file):
        log_message(f"License file not found: {license_file}")

    parse_raw_data(raw_data_dir, lineage)

    print("Generating LaTeX document...")
    generate_latex(lineage, bios, tex_file, output_dir, intro_dir, license_file)

    print(f"LaTeX document generated at: {tex_file}")
    print(f"Error log can be found at: {log_file}")
