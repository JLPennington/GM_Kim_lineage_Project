import os
import random
import datetime
import pandas as pd
import logging
import re

# Configure Logging
logging.basicConfig(
    filename="tool.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Ensure the output directory exists

# Allowed titles for teachers
ALLOWED_TITLES = ["Grand Master", "Master", "Mr.", "Ms.", "Mrs."]

# Address abbreviations dictionary
ADDRESS_ABBREVIATIONS = {
    "St.": "Street",
    "St": "Street",
    "Ave.": "Avenue",
    "Ave": "Avenue",
    "Rd.": "Road",
    "Rd": "Road",
    "Blvd.": "Boulevard",
    "Blvd": "Boulevard",
    "Dr.": "Drive",
    "Dr": "Drive",
    "Ln.": "Lane",
    "Ln": "Lane",
    "Pl.": "Place",
    "Pl": "Place",
    "Ct.": "Court",
    "Ct": "Court",
    "Pkwy": "Parkway",
    "Hwy": "Highway",
}

# Helper Functions

def capitalize_field(value):
    """
    Capitalizes the input value properly if it's a string.
    Otherwise, returns the value as is.
    """
    if isinstance(value, str):
        return value.title()  # Capitalizes each word
    return value

def replace_address_abbreviations(address):
    """
    Replaces common abbreviations in addresses with their full forms.
    """
    if not isinstance(address, str):
        return address  # Return as is if the value is not a string
    for abbr, full in ADDRESS_ABBREVIATIONS.items():
        address = address.replace(abbr, full)
    return address

def validate_date(date_str):
    """
    Validates that a date string is in YYYY-MM-DD format.
    """
    if not re.match(r"\d{4}-\d{2}-\d{2}", date_str):
        raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD.")
    return date_str

def create_teacher_file(title, first_name, middle_name, last_name, hometown, mentor, nationality):
    """
    Create a Teacher Format file with the specified details.
    """
    filename = f"{OUTPUT_DIR}/{title}_{first_name}_{middle_name}_{last_name}.txt"
    with open(filename, "w") as f:
        f.write(f"Hometown: {capitalize_field(hometown)}\n")
        f.write(f"Student of: {capitalize_field(mentor)}\n")
        f.write(f"Nationality: {capitalize_field(nationality)}\n")
    logging.info(f"Teacher file created: {filename}")
    return filename

def create_student_file(records):
    """
    Create a Student Format file with a list of student records.
    """
    filename = f"{OUTPUT_DIR}/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w") as f:
        for record in records:
            f.write(" | ".join(record) + "\n")
    logging.info(f"Student file created: {filename}")
    return filename

def get_input(prompt):
    """
    Get user input with the option to exit anytime by typing "exit".
    """
    value = input(prompt)
    if value.lower() == "exit":
        print("Exiting...")
        logging.info("User exited the script.")
        exit(0)  # Terminate the script
    return value

def prompt_teacher_details():
    """
    Prompt the user interactively to provide teacher details for creating a Teacher Format file.
    Validates the title against the allowed list.
    """
    print("\nEnter teacher details:")
    
    # Validate title
    while True:
        title = get_input("Title (Grand Master, Master, Mr., Ms., Mrs.): ").title()
        if title in ALLOWED_TITLES:
            break
        else:
            print(f"Invalid title. Allowed titles are: {', '.join(ALLOWED_TITLES)}")
            logging.warning(f"Invalid title entered: {title}")
    
    first_name = get_input("First Name: ").title()
    middle_name = get_input("Middle Name: ").title()
    last_name = get_input("Last Name: ").title()
    hometown = get_input("Hometown (City, State): ")
    mentor = get_input("Mentor's Name: ")
    nationality = get_input("Nationality: ")
    return title, first_name, middle_name, last_name, hometown, mentor, nationality

def generate_random_data(num_teachers=5, num_students=20):
    """
    Generate random test data for teachers and students.
    Ensures every teacher referenced in student records has a corresponding teacher record.
    """
    teachers = []  # List of randomly generated teacher records
    students = []  # List of randomly generated student records

    # Generate random teacher records
    for _ in range(num_teachers):
        title = random.choice(ALLOWED_TITLES[:2])  # Use only "Grand Master" and "Master" for test data
        first_name = random.choice(["John", "Jane", "Alex", "Emily"])
        middle_name = random.choice(["A", "B", "C", "D"])
        last_name = random.choice(["Smith", "Doe", "Brown", "Johnson"])
        hometown = f"{random.choice(['Ironton', 'Columbus', 'Austin'])}, {random.choice(['Ohio', 'Texas'])}"
        mentor = random.choice(["Master Kim", "Master Lee", "Master Park"])
        nationality = random.choice(["American", "Korean", "Canadian"])
        teachers.append((title, first_name, middle_name, last_name, hometown, mentor, nationality))
    
    # Generate random student records
    for _ in range(num_students):
        teacher = random.choice(teachers)
        teacher_name = f"{teacher[0]} {teacher[1]} {teacher[2]} {teacher[3]}"
        address = replace_address_abbreviations(teacher[4])
        student_name = random.choice(["Chris", "Pat", "Jordan", "Taylor"])
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        rank = random.choice(["White", "Yellow", "Black"])
        number = str(random.randint(1, 100))
        students.append((teacher_name, address, capitalize_field(student_name), date, capitalize_field(rank), number))
    
    # Create teacher and student files
    teacher_files = [create_teacher_file(*teacher) for teacher in teachers]
    student_file = create_student_file(students)
    logging.info(f"Generated {len(teacher_files)} teacher files and 1 student file: {student_file}")
    return teacher_files, student_file

def main():
    """
    Command Line Interface for processing teacher and student data.
    """
    print("Command Line Tool for Data Processing")
    while True:
        print("\nChoose an option:")
        print("1. Process Student Data from Excel")
        print("2. Create Teacher Record")
        print("3. Generate Random Test Data")
        print("4. Exit")
        
        choice = get_input("Enter your choice: ")
        if choice == "1":
            # Process student data from an Excel file
            excel_file = get_input("Enter the path to the Excel file: ")
            try:
                df = pd.read_excel(excel_file)
                for field in ["Teacher Name", "Student Name", "Date", "Rank"]:
                    if df[field].isnull().any() or (df[field] == "").any():
                        raise ValueError(f"Missing critical data in field: {field}")
                records = [
                    (
                        capitalize_field(row["Teacher Name"]),
                        replace_address_abbreviations(row["Address"]) if row["Address"] else "Unknown Address",
                        capitalize_field(row["Student Name"]),
                        validate_date(row["Date"]),
                        capitalize_field(row["Rank"]),
                        str(row["Number"]) if pd.notna(row["Number"]) else "0"
                    )
                    for _, row in df.iterrows()
                ]
                filename = create_student_file(records)
                print(f"Student data processed and saved to {filename}")
            except Exception as e:
                print(f"Error: {e}")
                logging.error(f"Error processing Excel file: {e}")
        elif choice == "2":
            # Create a teacher record interactively
            teacher_details = prompt_teacher_details()
            filename = create_teacher_file(*teacher_details)
            print(f"Teacher record created and saved to {filename}")
        elif choice == "3":
            # Generate random test data
            num_teachers = int(get_input("Enter the number of teachers to generate: "))
            num_students = int(get_input("Enter the number of students to generate: "))
            teacher_files, student_file = generate_random_data(num_teachers, num_students)
            print(f"Generated {len(teacher_files)} teacher files and 1 student file: {student_file}")
        elif choice == "4":
            print("Exiting...")
            logging.info("User exited the script.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
