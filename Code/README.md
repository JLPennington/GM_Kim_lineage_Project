# README: Lineage Document Generator

## Overview
This Python script generates a LaTeX document containing the lineage of martial artists. It is designed to process teacher and student information, create a structured LaTeX document, and compile it into a PDF with an index for easy reference.

### Key Features:
1. Processes teacher and student data.
2. Generates a LaTeX document with:
   - A title page.
   - License and introduction sections.
   - Chapters for each teacher, including their bios.
   - Tables listing student information, sorted and indexed.
3. Dynamically formats bios with correct grammar (e.g., "a" vs. "an").
4. Compiles the LaTeX document and index multiple times to ensure proper formatting.

---

## Script Functions

### **1. `escape_latex_special_characters(text)`**
- Escapes special LaTeX characters (e.g., `&`, `%`, `$`) to avoid errors during compilation.
- **Args**:
  - `text` (str): The input string.
- **Returns**:
  - Escaped string suitable for LaTeX.

### **2. `format_student_name(name)`**
- Formats student names as "Last name, First name Middle name".
- **Args**:
  - `name` (str): Full name of the student.
- **Returns**:
  - A formatted string in the desired name order.

### **3. `generate_latex_preamble(file, title, author)`**
- Writes the LaTeX document preamble, including title, author, and metadata.
- **Args**:
  - `file` (file object): The LaTeX file being written.
  - `title` (str): The title of the document.
  - `author` (str): The author of the document.

### **4. `generate_license_section(file)`**
- Writes a hardcoded license section into the LaTeX document.
- **Args**:
  - `file` (file object): The LaTeX file being written.

### **5. `generate_introduction_section(file)`**
- Writes a hardcoded introduction section into the LaTeX document.
- **Args**:
  - `file` (file object): The LaTeX file being written.

### **6. `generate_teacher_section(file, teacher, bio, lineage, is_first_chapter)`**
- Generates a chapter for each teacher, including their bio and lineage details.
- **Args**:
  - `file` (file object): The LaTeX file being written.
  - `teacher` (str): Name of the teacher.
  - `bio` (dict): Teacher's bio details (`hometown`, `student_of`, `nationality`).
  - `lineage` (dict): Lineage information.
  - `is_first_chapter` (bool): Indicates if the chapter is the first (adds a hardcoded bio).

### **7. `generate_student_table(file, address, students)`**
- Generates a LaTeX table for students under a specific teacher and address.
- Students are:
  - Sorted alphabetically.
  - Indexed in the LaTeX document.
- **Args**:
  - `file` (file object): The LaTeX file being written.
  - `address` (str): Address associated with the students.
  - `students` (list): List of student details.

### **8. `generate_latex(lineage, bios, tex_file, log_file)`**
- Main function to generate the complete LaTeX document.
- Adds preamble, license, introduction, and content (teachers and students).
- **Args**:
  - `lineage` (dict): Lineage data structured by teachers and their students.
  - `bios` (dict): Bio information for teachers.
  - `tex_file` (str): Path to save the LaTeX file.
  - `log_file` (str): Path to the log file.

### **9. `compile_latex(tex_file, output_dir)`**
- Compiles the LaTeX document and generates the index.
- Runs the compilation process twice to ensure everything is processed correctly.
- **Args**:
  - `tex_file` (str): Path to the LaTeX file to compile.
  - `output_dir` (str): Directory for the compiled PDF output.

---

## How to Use the Script

1. **Prepare Input Data**:
   - Organize teacher and student data in a format suitable for the script.
   - Ensure bios include keys: `hometown`, `student_of`, and `nationality`.

2. **Run the Script**:
   - Modify the script's main logic to load your data into `lineage` and `bios` dictionaries.
   - Call `generate_latex` with appropriate arguments.
   - Use `compile_latex` to compile the LaTeX document into a PDF.

3. **Output**:
   - The compiled PDF will include:
     - Title, license, and introduction sections.
     - Chapters for each teacher with bios and student tables.
     - An index for quick reference.

---

## Example Workflow

```python
lineage = {
    "Grand Master Jordan Brown": {
        "Houston Dojang": [
            ("Elliot Parker", "2025-01-01", "Black Belt", "123"),
            ("Annie Lee", "2024-12-15", "Red Belt", "124"),
        ]
    }
}

bios = {
    "Grand Master Jordan Brown": {
        "hometown": "Houston, TX",
        "student_of": "Grand Master Kim",
        "nationality": "American"
    }
}

generate_latex(lineage, bios, "lineage_document.tex", "error_log.txt")
compile_latex("lineage_document.tex", "output/")
```

---

## Requirements
- Python 3.6+
- LaTeX installed (with `pdflatex` and `makeindex` available).

---

## Notes
- Ensure LaTeX paths are configured correctly if running in a restricted environment.
- Test the script with sample data before processing large datasets to verify formatting.

---

## Troubleshooting
- **Missing Index Entries**:
  - Verify that student names are being added to the index with `\index` commands.
- **LaTeX Compilation Errors**:
  - Ensure all special characters are properly escaped.
  - Check the `log_file` for details.
