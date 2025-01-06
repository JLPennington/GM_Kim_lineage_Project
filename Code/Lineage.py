import os
import subprocess
from collections import defaultdict
from datetime import datetime

def parse_date(date_str):
    """
    Parses a date string and returns it in YYYY-MM-DD format.
    Supports multiple input formats.
    """
    if not date_str:
        return "No Date Provided"

    # List of date formats to try
    formats = ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    print(f"Warning: Invalid date format '{date_str}'. Using placeholder.")
    return "Invalid Date"

def reformat_name(name):
    """
    Reformats a name to: Title Last Name, First Name Middle Name.
    Supports titles like Grand Master, Master, Mr., Ms., Mrs.
    Removes trailing commas or extra spaces.
    """
    name = name.strip().rstrip(",")  # Remove trailing commas and spaces
    name_parts = name.split()
    valid_titles = {"Grand Master", "Master", "Mr.", "Ms.", "Mrs."}

    if len(name_parts) < 2:
        return name  # Return as-is for single-word names

    # Check if the name starts with a valid title
    if " ".join(name_parts[:2]) in valid_titles:  # Handle "Grand Master"
        title = " ".join(name_parts[:2])
        rest = name_parts[2:]
    elif name_parts[0] in valid_titles:  # Handle single-word titles
        title = name_parts[0]
        rest = name_parts[1:]
    else:
        title = ""
        rest = name_parts

    # Format the name
    if rest and "," in rest[0]:  # Name is already in "Last, First" format
        return f"{title} {' '.join(rest)}".strip()
    elif rest:  # Reformat to "Title Last Name, First Middle"
        last_name = rest[-1]
        first_middle = " ".join(rest[:-1])
        return f"{title} {last_name}, {first_middle}".strip()
    else:
        return title.strip()


def load_bios(bio_dir):
    """
    Loads bios for teachers from the Bios subdirectory.
    """
    bios = {}
    if not os.path.exists(bio_dir):
        print(f"Error: Bios directory not found at {bio_dir}.")
        return bios

    print(f"Loading bios from directory: {bio_dir}")
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
                    print(f"Loaded bio for: {teacher_name}")
            except Exception as e:
                print(f"Error reading bio file {bio_path}: {e}")
    return bios


def parse_raw_data(raw_data_dir, lineage):
    """
    Parses files in the RAW Data directory and populates the lineage dictionary.
    """
    if not os.path.exists(raw_data_dir):
        print(f"Error: RAW Data directory not found at {raw_data_dir}.")
        return

    print(f"Processing RAW Data files from: {raw_data_dir}")
    for filename in os.listdir(raw_data_dir):
        file_path = os.path.join(raw_data_dir, filename)
        if not filename.endswith(".txt"):
            continue
        try:
            print(f"Processing file: {file_path}")
            with open(file_path, "r") as file:
                for line in file:
                    parts = [x.strip() for x in line.split(",")]
                    if len(parts) < 5:
                        print(f"Skipping malformed line in {filename}: {line.strip()}")
                        continue
                    teacher = reformat_name(parts[0])
                    address = parts[1]
                    student = parts[2]
                    date = parts[3]
                    ranking = parts[4]
                    number = parts[5] if len(parts) > 5 else ""

                    if teacher not in lineage:
                        lineage[teacher] = {}
                    if address not in lineage[teacher]:
                        lineage[teacher][address] = []
                    lineage[teacher][address].append((student, date, ranking, number))
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")


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
            print(f"PDF generation failed:\n{result.stderr}")
    except FileNotFoundError:
        print("Error: 'pdflatex' is not installed or not found in the PATH.")
    except Exception as e:
        print(f"An error occurred during PDF generation: {e}")


def generate_latex(lineage, bios, tex_file, output_dir):
    """
    Generates a LaTeX document with chapters for each teacher
    and sections for each physical address listing their students.
    """
    if not lineage:
        print("Error: No lineage data found. The LaTeX document will not be meaningful.")
        return

    try:
        with open(tex_file, "w") as file:
            # LaTeX document header
            file.write("\\documentclass{book}\n")
            file.write("\\usepackage[utf8]{inputenc}\n")
            file.write("\\usepackage{tabularx}\n")
            file.write("\\begin{document}\n")

            # Generate a chapter for each teacher
            for teacher, locations in lineage.items():
                teacher_clean = teacher.strip().rstrip(",")
                file.write(f"\\chapter*{{{teacher_clean}}}\n")

                if teacher_clean in bios:
                    bio_data = bios[teacher_clean]
                    hometown = bio_data.get("hometown", "Unknown hometown")
                    student_of = bio_data.get("student_of", "Unknown teacher")
                    nationality = bio_data.get("nationality", "Unknown nationality")
                    file.write(f"\\paragraph*{{}} {teacher_clean}, a {nationality} martial artist, is from {hometown} and was trained under {student_of}. \n")
                else:
                    print(f"Warning: Missing bio for teacher '{teacher_clean}'.")
                    file.write(f"\\paragraph*{{}} A biography for {teacher_clean} is currently unavailable.\n")

                for address, students in locations.items():
                    file.write(f"\\section*{{{address}}}\n")
                    file.write("\\begin{tabularx}{\\textwidth}{|c|X|X|X|X|}\n")
                    file.write("\\hline\n")
                    file.write("\\textbf{No.} & \\textbf{Student Name} & \\textbf{Date} & \\textbf{Ranking} & \\textbf{Number} \\\\\n")
                    file.write("\\hline\n")

                    for idx, (student, date, ranking, number) in enumerate(students, start=1):
                        file.write(f"{idx} & {student} & {date} & {ranking} & {number} \\\\\n")
                        file.write("\\hline\n")

                    file.write("\\end{tabularx}\n")

            file.write("\\end{document}\n")
        print(f"LaTeX document generated at: {tex_file}")
        generate_pdf(tex_file, output_dir)

    except Exception as e:
        print(f"Error writing LaTeX file: {e}")


if __name__ == "__main__":
    current_dir = os.getcwd()
    raw_data_dir = os.path.join(current_dir, "RAW Data")
    bio_dir = os.path.join(current_dir, "Bios")
    output_dir = os.path.dirname(current_dir)
    tex_file = os.path.join(output_dir, "lineage_document.tex")

    print(f"RAW Data Directory: {raw_data_dir}")
    print(f"Bios Directory: {bio_dir}")
    print(f"Output Directory: {output_dir}")

    lineage = defaultdict(dict)
    bios = load_bios(bio_dir)
    parse_raw_data(raw_data_dir, lineage)
    generate_latex(lineage, bios, tex_file, output_dir)