import os

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

def validate_line(line, line_number):
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

    return warnings, errors

def test_single_file(file_path):
    """
    Validates a single file in the RAW Data directory and prints warnings and errors.
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"\nTesting file: {file_path}\n")
    issues = {"warnings": 0, "errors": 0, "lines": []}

    try:
        with open(file_path, "r") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if line:
                    warnings, errors = validate_line(line, line_number)
                    if warnings or errors:
                        issues["lines"].append((line_number, line, warnings, errors))
                        issues["warnings"] += len(warnings)
                        issues["errors"] += len(errors)

        # Display results
        print(f"Summary of Issues:\n  Warnings: {issues['warnings']}\n  Errors: {issues['errors']}\n")
        if issues["lines"]:
            print("Detailed Issues:")
            for line_number, line, warnings, errors in issues["lines"]:
                print(f"  Line {line_number}: {line}")
                for warning in warnings:
                    print(f"    - Warning: {warning}")
                for error in errors:
                    print(f"    - Error: {error}")
        else:
            print("No issues found. File is valid.")

    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

if __name__ == "__main__":
    # Specify the file to test
    raw_data_dir = os.path.join(os.getcwd(), "RAW Data")
    file_name = input("Enter the name of the file to test (located in RAW Data): ").strip()
    file_path = os.path.join(raw_data_dir, file_name)

    # Test the file
    test_single_file(file_path)