
# CLI Tools for Processing Student and Teacher Data

This project provides a Command Line Interface (CLI) tool to process Excel files containing student data, generate teacher and student records, and manage the data efficiently. The tool includes robust features for handling multiple Excel files, generating random test data, and maintaining a clean workflow.

---

## Table of Contents
1. [Instructions on Use](#instructions-on-use)
2. [Explanation of the Script](#explanation-of-the-script)

---

## Instructions on Use

### Prerequisites
1. **Python**: Ensure Python 3.6 or higher is installed on your system.
2. **Required Python Libraries**:
   - Install the dependencies by running:
     ```bash
     pip install pandas openpyxl
     ```

### Setup
1. Clone this repository or download the script files.
2. Ensure the following directory structure exists:
   ```
   project_directory/
   ├── script.py
   ├── output/
   └── excel_files/
   ```
   - `script.py`: The main Python script.
   - `output/`: Directory where generated records are saved.
   - `excel_files/`: Directory for storing Excel files to be processed.

3. Place your `.xlsx` files containing student data in the `excel_files` directory.

### Running the Script
1. Navigate to the directory containing `script.py`:
   ```bash
   cd project_directory
   ```

2. Run the script:
   ```bash
   python script.py
   ```

3. Follow the on-screen prompts to interact with the tool.

### Options
When you run the script, you'll see the following options:

#### 1. Process Student Data from Excel
- Processes all `.xlsx` files in the `excel_files` directory.
- After processing, prompts you to delete the Excel files.
- Outputs processed student data to text files in the `output/` directory.

#### 2. Create Teacher Record
- This feature is under development.

#### 3. Generate Random Test Data
- Generates random teacher and student records.
- Prompts you to specify the number of teachers and students to generate.
- Outputs records to the `output/` directory.

#### 4. Exit
- Exits the script at any time.

---

## Explanation of the Script

### Purpose
The script is designed to streamline the management of student and teacher data. It processes Excel files, generates formatted records, and automates tasks for efficiency.

### Key Features
1. **Processing Excel Files**:
   - Automatically processes all Excel files in the `excel_files` directory.
   - Validates required fields: `Teacher Name`, `Address`, `Student Name`, `Date`, `Rank`, and `Number`.
   - Outputs processed records in the format:
     ```
     Teacher Name | Address | Student Name | Date | Rank | Number
     ```

2. **Random Data Generation**:
   - Creates realistic teacher and student records for testing.
   - Teachers are assigned a city and state for their hometowns.
   - Students have full U.S. addresses.

3. **Post-Processing Workflow**:
   - After processing files, prompts the user to delete the processed Excel files to keep the workspace clean.

### How It Works
1. **Directories**:
   - `excel_files/`: Stores Excel files for processing.
   - `output/`: Saves generated or processed records as text files.

2. **Validation**:
   - Ensures all required columns exist in Excel files.
   - Checks for missing data and handles errors gracefully.

3. **Helper Functions**:
   - **`capitalize_field`**: Formats strings (e.g., names, ranks) for consistency.
   - **`replace_address_abbreviations`**: Expands address abbreviations (e.g., `St.` → `Street`).
   - **`generate_random_address`**: Creates realistic U.S. addresses for students.
   - **`generate_random_city_state`**: Generates city and state pairs for teacher hometowns.

4. **Logging**:
   - All operations are logged to `tool.log` for debugging and tracking.

---

### Example Workflow
1. Place the following Excel file in the `excel_files/` directory:

   **Sample File: `students.xlsx`**
   | Teacher Name   | Address             | Student Name | Date       | Rank   | Number |
   |----------------|---------------------|--------------|------------|--------|--------|
   | Grand Master A | 123 Main Street, NY | John Smith   | 2023-01-01 | Black  | 1      |
   | Master B       | 456 Pine Ave, CA    | Jane Doe     | 2023-01-02 | Yellow | 2      |
   | Mr. C          | 789 Elm Blvd, TX    | Chris Johnson| 2023-01-03 | White  | 3      |

2. Run the script and select **Option 1**:
   ```plaintext
   Choose an option:
   1. Process Student Data from Excel
   2. Create Teacher Record
   3. Generate Random Test Data
   4. Exit
   Enter your choice: 1
   ```

3. Processed records will be saved to the `output/` directory:
   ```plaintext
   Processed students.xlsx and saved to output/20250109_142345.txt
   ```

4. When prompted:
   ```plaintext
   Do you want to delete the processed Excel files? (yes/no):
   ```
   - Type `yes` to delete the Excel files.
   - Type `no` to keep them.

---

### Notes
- Ensure the `excel_files/` directory contains valid `.xlsx` files before processing.
- For best results, use properly formatted data as shown in the example above.
- If you encounter issues, check `tool.log` for details.

---

Feel free to modify or extend the script for your specific needs!
