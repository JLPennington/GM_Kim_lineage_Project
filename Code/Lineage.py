import os
import subprocess
from collections import defaultdict


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


def generate_pdf(tex_file, output_dir):
    """
    Compiles the LaTeX file into a PDF using pdflatex.
    Returns a success flag and an error message if any.
    """
    try:
        print(f"Compiling {tex_file} into a PDF...")
        # Run pdflatex command
        result = subprocess.run(
            ["pdflatex", "-output-directory", output_dir, tex_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Check for errors during compilation
        if result.returncode == 0:
            print(f"PDF successfully generated at {os.path.join(output_dir, 'lineage_document.pdf')}")
            return True, None
        else:
            return False, result.stderr
    except FileNotFoundError:
        return False, "'pdflatex' is not installed or not found in the PATH."
    except Exception as e:
        return False, str(e)


def generate_latex(lineage, bios, tex_file, output_dir):
    """
    Generates a LaTeX document with chapters for each teacher
    and sections for each physical address listing their students.
    """
    try:
        with open(tex_file, "w") as file:
            # LaTeX document header
            file.write("\\documentclass{book}\n")
            file.write("\\usepackage[utf8]{inputenc}\n")
            file.write("\\usepackage{tabularx}\n")
            file.write("\\begin{document}\n")

            # Generate a chapter for each teacher
            for teacher, locations in lineage.items():
                teacher_clean = teacher.strip().rstrip(",")  # Clean up teacher name
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
                    if address:
                        file.write(f"\\section*{{{address}}}\n")
                    else:
                        file.write("\\section*{Unknown Address}\n")

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

        # Compile LaTeX to PDF
        pdf_success, pdf_error = generate_pdf(tex_file, output_dir)
        if not pdf_success:
            print(f"PDF generation failed: {pdf_error}")
            print("The LaTeX file was successfully generated and can be compiled manually.")

    except Exception as e:
        print(f"Error writing LaTeX file: {e}")


if __name__ == "__main__":
    raw_data_dir = os.path.join(os.getcwd(), "RAW Data")
    bio_dir = os.path.join(os.getcwd(), "Bios")
    output_dir = os.path.dirname(os.getcwd())
    tex_file = os.path.join(output_dir, "lineage_document.tex")

    # Sample lineage and bios for testing
    lineage = defaultdict(dict)  # Populate as needed
    bios = {}  # Populate as needed

    # Generate LaTeX and PDF
    generate_latex(lineage, bios, tex_file, output_dir)