import os
from collections import defaultdict

def reformat_name(name):
    """
    Reformats a name to: Title Last Name, First Name Middle Name.
    Supports titles like Grand Master, Master, Mr., Ms., Mrs.
    """
    name_parts = name.split()
    valid_titles = {"Grand Master", "Master", "Mr.", "Ms.", "Mrs."}

    if len(name_parts) < 2:
        return name.strip()  # Return as-is for single-word names

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
    Loads bios for teachers from the Bios subdirectory and parses them into structured data.
    Logs warnings for missing bios.
    """
    bios = {}
    if not os.path.exists(bio_dir):
        print(f"Bios directory not found: {bio_dir}")
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
                print(f"Error reading bio file {bio_path}: {e}")
    return bios

def parse_teacher_student_file(file_path, lineage, issues):
    """
    Parses a single file and adds its data to the lineage dictionary.
    """
    try:
        with open(file_path, "r") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if line:
                    parts = [x.strip() for x in line.split(",")]
                    teacher = reformat_name(parts[0])  # Reformat teacher name
                    address = parts[1] if len(parts) > 1 else ""  # Optional address
                    student = parts[2]
                    date = parts[3] if len(parts) > 3 else ""  # Optional date
                    ranking = parts[4]  # Mandatory
                    number = parts[5] if len(parts) > 5 else ""  # Optional number

                    # Append student details under the teacher and address
                    if teacher not in lineage:
                        lineage[teacher] = {}
                    if address not in lineage[teacher]:
                        lineage[teacher][address] = []
                    lineage[teacher][address].append((student, date, ranking, number))
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

def generate_latex(lineage, bios, output_path):
    """
    Generates a LaTeX document with chapters for each teacher
    and sections for each physical address listing their students.
    """
    try:
        with open(output_path, "w") as file:
            # LaTeX document header
            file.write("\\documentclass{book}\n")
            file.write("\\usepackage[utf8]{inputenc}\n")
            file.write("\\usepackage{tabularx}\n")
            file.write("\\begin{document}\n")

            # Generate a chapter for each teacher
            for teacher, locations in lineage.items():
                # Teacher chapter heading
                file.write(f"\\chapter*{{{teacher}}}\n")

                # Generate the paragraph based on bio data
                if teacher in bios:
                    bio_data = bios[teacher]
                    hometown = bio_data.get("hometown", "Unknown hometown")
                    student_of = bio_data.get("student_of", "Unknown teacher")
                    nationality = bio_data.get("nationality", "Unknown nationality")
                    file.write(f"\\paragraph*{{}} {teacher}, a {nationality} martial artist, is from {hometown} and was trained under {student_of}. \n")
                else:
                    print(f"Warning: Missing bio for teacher '{teacher}'.")
                    file.write(f"\\paragraph*{{}} A biography for {teacher} is currently unavailable.\n")

                # Add sections for each physical address
                for address, students in locations.items():
                    # Section for the physical address
                    if address:
                        file.write(f"\\section*{{{address}}}\n")
                    else:
                        file.write("\\section*{Unknown Address}\n")

                    # Table of students
                    file.write("\\begin{tabularx}{\\textwidth}{|c|X|X|X|X|}\n")
                    file.write("\\hline\n")
                    file.write("\\textbf{No.} & \\textbf{Student Name} & \\textbf{Date} & \\textbf{Ranking} & \\textbf{Number} \\\\\n")
                    file.write("\\hline\n")

                    # Add each student as a row with numbering
                    for idx, (student, date, ranking, number) in enumerate(students, start=1):
                        file.write(f"{idx} & {student} & {date} & {ranking} & {number} \\\\\n")
                        file.write("\\hline\n")

                    file.write("\\end{tabularx}\n")

            # LaTeX document footer
            file.write("\\end{document}\n")
        print(f"LaTeX document generated at: {output_path}")
    except Exception as e:
        print(f"Error writing LaTeX file: {e}")

if __name__ == "__main__":
    # Define directories and output file
    raw_data_dir = os.path.join(os.getcwd(), "RAW Data")
    bio_dir = os.path.join(os.getcwd(), "Bios")
    output_file = os.path.join(os.path.dirname(os.getcwd()), "lineage_document.tex")

    # Load teacher bios
    bios = load_bios(bio_dir)

    # Track issues
    lineage = defaultdict(dict)

    # Process all files in the RAW Data directory
    if not os.path.exists(raw_data_dir):
        print(f"RAW Data directory not found: {raw_data_dir}")
    else:
        for filename in os.listdir(raw_data_dir):
            if filename.startswith("."):  # Ignore hidden files
                continue
            file_path = os.path.join(raw_data_dir, filename)
            if os.path.isfile(file_path):  # Ensure it's a file
                parse_teacher_student_file(file_path, lineage, {})

        # Generate LaTeX document
        generate_latex(lineage, bios, output_file)
        print("\nOutput file generated.")