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

def validate_line(line, line_number, file_path, issues):
    """
    Validates a single line from the input file.
    Checks for the required number of fields and valid formatting.
    """
    parts = [x.strip() for x in line.split(",")]
    warnings = []
    errors = []

    # Check if teacher name (with title) is provided
    if len(parts) < 1 or not parts[0]:
        errors.append("Missing teacher name (with title).")

    # Check if student name is provided
    if len(parts) < 3 or not parts[2]:
        errors.append("Missing student name.")

    # Check if student rank is provided
    if len(parts) < 5 or not parts[4]:
        errors.append("Missing student rank.")

    # Log warnings for optional fields
    if len(parts) < 2 or not parts[1]:
        warnings.append("Missing teacher address.")
    if len(parts) < 4 or not parts[3]:
        warnings.append("Missing date.")
    if len(parts) < 6 or not (len(parts) > 5 and parts[5]):
        warnings.append("Missing student number.")

    # Log issues
    if warnings or errors:
        issues[file_path]["lines"].append((line_number, line, warnings, errors))
        issues[file_path]["warnings"] += len(warnings)
        issues[file_path]["errors"] += len(errors)

    return len(errors) == 0  # Return True if no errors, False otherwise

def parse_teacher_student_file(file_path, lineage, issues):
    """
    Parses a single file and adds its data to the lineage dictionary.
    """
    try:
        with open(file_path, "r") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if line:
                    # Validate the line
                    if validate_line(line, line_number, file_path, issues):
                        # Parse each line into attributes
                        parts = [x.strip() for x in line.split(",")]
                        teacher = reformat_name(parts[0])  # Reformat teacher name
                        address = parts[1] if len(parts) > 1 else ""  # Optional address
                        student = parts[2]
                        date = parts[3] if len(parts) > 3 else ""  # Optional date
                        ranking = parts[4]  # Mandatory
                        number = parts[5] if len(parts) > 5 else ""  # Optional number

                        # Append student details under the teacher
                        if teacher not in lineage:
                            lineage[teacher] = {"address": address, "students": []}
                        lineage[teacher]["students"].append((student, date, ranking, number))
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

def generate_summary(issues):
    """
    Generates a summary of warnings and errors for all files.
    """
    print("\nSummary of Issues:")
    for file_path, details in issues.items():
        print(f"File: {file_path}")
        print(f"  Warnings: {details['warnings']}")
        print(f"  Errors: {details['errors']}")
    print("\nRun the script again with '--details' to view detailed information.")

def generate_details(issues):
    """
    Generates detailed information about warnings and errors for all files.
    """
    print("\nDetailed Issues:")
    for file_path, details in issues.items():
        print(f"\nFile: {file_path}")
        for line_number, line, warnings, errors in details["lines"]:
            print(f"  Line {line_number}: {line}")
            for warning in warnings:
                print(f"    - Warning: {warning}")
            for error in errors:
                print(f"    - Error: {error}")

def generate_latex(lineage, output_path):
    """
    Generates a LaTeX document with chapters for each teacher
    and tables listing their students with attributes.
    """
    try:
        with open(output_path, "w") as file:
            # LaTeX document header
            file.write("\\documentclass{book}\n")
            file.write("\\usepackage[utf8]{inputenc}\n")
            file.write("\\usepackage{tabularx}\n")  # Add tabularx for balanced tables
            file.write("\\begin{document}\n")

            # Generate a chapter for each teacher
            for teacher, data in lineage.items():
                address = data["address"]
                students = data["students"]

                # Teacher chapter heading includes address (if available)
                if address:
                    file.write(f"\\chapter*{{{teacher} ({address})}}\n")
                else:
                    file.write(f"\\chapter*{{{teacher}}}\n")

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
                file.write("\\newpage\n")  # Page break after each chapter

            # LaTeX document footer
            file.write("\\end{document}\n")
        print(f"LaTeX document generated at: {output_path}")
    except Exception as e:
        print(f"Error writing LaTeX file: {e}")

if __name__ == "__main__":
    # Define the RAW Data directory in the same location as the script
    raw_data_dir = os.path.join(os.getcwd(), "RAW Data")
    output_file = os.path.join(os.path.dirname(os.getcwd()), "lineage_document.tex")  # Output one level above script

    # Track issues
    issues = defaultdict(lambda: {"warnings": 0, "errors": 0, "lines": []})
    lineage = defaultdict(dict)

    # Check if the RAW Data directory exists
    if not os.path.exists(raw_data_dir):
        print(f"RAW Data directory not found: {raw_data_dir}")
    else:
        # Process all files in the RAW Data directory
        for filename in os.listdir(raw_data_dir):
            if filename.startswith("."):  # Ignore hidden files
                continue
            file_path = os.path.join(raw_data_dir, filename)
            if os.path.isfile(file_path):  # Ensure it's a file
                parse_teacher_student_file(file_path, lineage, issues)

        # Generate summary and optionally details
        generate_summary(issues)
        if input("\nDo you want to view detailed issues? (y/n): ").strip().lower() == "y":
            generate_details(issues)

        # Generate LaTeX regardless of warnings, but skip rows with errors
        generate_latex(lineage, output_file)
        print("\nOutput file generated. Review warnings in the summary for missing optional data.")