
# **Lineage Processing Script**

This project is designed to document the lineage of martial artists trained under **Grand Master Kim**. It organizes and validates teacher-student data, ensuring a professional and systematic representation of the lineage in a structured LaTeX document.

By leveraging this script, martial artists' heritage and training records can be preserved with clarity and accuracy. This project supports the vision of maintaining the legacy of Grand Master Kim and the students he has trained.

---

## **Features**
- Validates input data for missing critical fields.
- Supports teacher titles: **Grand Master**, **Master**, **Mr.**, **Ms.**, **Mrs.**.
- Generates a LaTeX file that organizes data by teacher chapters.
- Automatically balances tables for a professional document layout.
- Provides clear summary and detailed logs for warnings and errors in input data.

---

## **Requirements**

### **Software**
1. **Python 3.8 or higher**
   - Install Python from [python.org](https://www.python.org/downloads/).

2. **LaTeX Distribution**
   - A LaTeX compiler is required to process the `.tex` file into a PDF. Examples include:
     - **TeX Live** (Linux, macOS, Windows)
     - **MikTeX** (Windows)
     - **MacTeX** (macOS)
   - Install from [TeX Live](https://www.tug.org/texlive/) or [MikTeX](https://miktex.org/).

### **Python Libraries**
No additional Python libraries are required. The script uses Python's standard library.

---

## **Setup**

### **1. Directory Structure**
Ensure the following directory structure:
```
project_root/
│
├── Code/
│   ├── Lineage.py        # The main script
│   └── RAW Data/         # Directory for input text files
│       ├── file1.txt     # Example input file
│       ├── file2.txt
│       └── file3.txt
└── lineage_document.tex  # Output file (generated in the top-level directory)
```

- Place the `Lineage.py` script inside the `Code/` directory.
- Place all input text files in the `RAW Data/` subdirectory.

### **2. Input File Format**
Each input file should have one entry per line with the following fields, separated by commas:
```
<teacher name>, <teacher address>, <student name>, <date>, <ranking>, <student number>
```

#### **Mandatory Fields**:
- `<teacher name>`: Must include a title (e.g., "Grand Master Kim").
- `<student name>`: Student's full name.
- `<ranking>`: Student's rank.

#### **Optional Fields**:
- `<teacher address>`: Teacher's physical address.
- `<date>`: Date of Rank (format: `YYYY-MM-DD`).
- `<student number>`: Dan number

#### **Example Input**:
```plaintext
Grand Master Kim, 123 Training Blvd, Student A, 2025-01-01, Black Belt, 12345
Master Lee, 456 Martial Rd, Student B, 2025-02-01, Brown Belt
Mr. Smith, 789 Combat Ave, Student C, , Instructor, 67890

```

---

## **Usage**

### **1. Run the Script**
Navigate to the `Code/` directory and run the script:
```bash
python3 Lineage.py
```

### **2. Script Output**
- **Validation Summary**: The script will display a summary of warnings and errors in the input data.
- **Detailed Logs**: If requested, the script provides a detailed breakdown of issues by file and line number.
- **LaTeX File**: The script generates a `lineage_document.tex` file in the top-level directory.

### **3. Process the LaTeX File**
To generate a PDF document from the `.tex` file:
1. Open a terminal or command prompt.
2. Navigate to the directory containing `lineage_document.tex`.
3. Run the following command:
   ```bash
   pdflatex lineage_document.tex
   ```
4. The PDF will be generated in the same directory.

---

## **Error Handling**
### **Critical Errors**
The script will exclude rows with the following issues:
1. Missing **teacher name (with title)**.
2. Missing **student name**.
3. Missing **ranking**.

### **Warnings**
The script logs warnings for missing optional fields such as:
- Teacher address
- Date
- Student number

Warnings do not prevent the generation of the output file.

---

## **Contributing**
1. Fork the repository and create your branch:
   ```bash
   git checkout -b feature/YourFeature
   ```
2. Commit your changes:
   ```bash
   git commit -m "Add YourFeature"
   ```
3. Push to the branch:
   ```bash
   git push
   ```
4. Open a pull request.

---

## **License**
This project is licensed under the MIT License. See `LICENSE` for more details.

---

## **Contact**
For questions or support, please reach out to **[Your Contact Info]**.

