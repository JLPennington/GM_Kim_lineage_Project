
# Lineage Documentation Tool

## Purpose
This project aims to document the lineage of Grand Master Kim and other instructors, their locations, and their students over time. The resulting document is a well-structured LaTeX file that includes information about instructors, their bios, addresses, and detailed student lists.

## Features
- Parses raw data files containing information about instructors, students, and addresses.
- Generates a LaTeX document organized by instructor, with:
  - Chapters for each instructor.
  - Sections for each physical address.
  - Student lists displayed in well-formatted tables.
- Includes instructor bios with data points such as:
  - Hometown
  - Teacher under whom they trained
  - Nationality
- Handles missing or malformed data with detailed error reporting:
  - Logs missing or malformed instructor bios.
  - Logs missing student data fields like names, dates, rankings, or numbers.

## Requirements
1. **Python 3.x**:
   - Ensure Python 3 is installed on your system.
   - Required libraries: None (uses built-in Python libraries).
2. **LaTeX**:
   - A LaTeX distribution such as TeX Live or MikTeX is needed to compile the `.tex` file.
3. **Directory Structure**:
   - `RAW Data/`: Contains the raw input files for parsing.
   - `Bios/`: Contains bios for instructors as `.txt` files.
   - Output LaTeX file will be saved in the parent directory.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repository-name.git
   cd your-repository-name
   ```

2. Place your raw data files in the `RAW Data/` directory.
3. Place your instructor bios in the `Bios/` directory, formatted as `.txt` files.

## Input File Formats
### Raw Data Files
Each line in a raw data file should contain:
```
Instructor Name, Address, Student Name, Date, Ranking, Number
```
Example:
```
Grand Master Kim, 123 Martial Way, Student A, 2025-01-01, Black Belt, 12345
Master Lee, 456 Combat St, Student B, 2025-02-15, Brown Belt
```

### Instructor Bios
Each bio file in the `Bios/` directory should be named after the instructor (e.g., `Grand Master Kim.txt`) and contain:
```
Hometown: Seoul, South Korea
Student of: Master Lee
Nationality: Korean
```

## Usage
1. Run the main script:
   ```bash
   python3 Lineage.py
   ```

2. The script will:
   - Parse all files in the `RAW Data/` directory.
   - Check for missing or malformed data.
   - Generate a LaTeX file (`lineage_document.tex`) in the parent directory.

3. To compile the `.tex` file into a PDF:
   ```bash
   pdflatex lineage_document.tex
   ```

## Error Handling
The script identifies and logs the following issues:
- **Instructor Bios**:
  - Missing bio files for instructors.
  - Malformed or incomplete bio data.
- **Student Data**:
  - Missing or malformed fields, such as:
    - Instructor name
    - Student name
    - Ranking (mandatory)
    - Date or number (optional)

### Example Error Summary
After processing, the script provides a summary of issues:
```
Summary of Issues:
File: RAW Data/file1.txt
  Warnings: 2
  Errors: 1
File: RAW Data/file2.txt
  Warnings: 3
  Errors: 0
```

Run the script again for detailed information on each issue.

## Output Example
The generated LaTeX document includes:
1. **Chapters for Instructors**:
   - Bio paragraph (if available).
2. **Sections for Addresses**:
   - Tables listing students associated with each address.

### Example Chapter
```
\chapter*{Grand Master Kim}

\paragraph*{} Grand Master Kim, a Korean martial artist, is from Seoul, South Korea and was trained under Master Lee.

\section*{123 Martial Way, Seoul, South Korea}
egin{tabularx}{	extwidth}{|c|X|X|X|X|}
\hline
	extbf{No.} & 	extbf{Student Name} & 	extbf{Date} & 	extbf{Ranking} & 	extbf{Number} \
\hline
1 & Student A & 2025-01-01 & Black Belt & 12345 \
\hline
\end{tabularx}
```

## Contributing
Contributions are welcome! If you have suggestions for improvements or encounter issues, feel free to open an issue or submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
