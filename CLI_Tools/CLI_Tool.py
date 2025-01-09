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
EXCEL_DIR = "excel_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Ensure output directory exists
os.makedirs(EXCEL_DIR, exist_ok=True)  # Ensure Excel directory exists

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

# Random data pools for names and addresses
FIRST_NAMES = ["John", "Jane", "Alex", "Emily", "Chris", "Jordan", "Taylor", "Morgan"]
MIDDLE_NAMES = ["A.", "B.", "C.", "D.", "E.", "F.", "G.", "H."]
LAST_NAMES = ["Smith", "Johnson", "Brown", "Williams", "Jones", "Davis", "Garcia", "Martinez"]
CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio"]
STATES = ["NY", "CA", "IL", "TX", "AZ", "PA", "FL", "OH", "GA", "NC"]
STREET_NAMES = ["Main", "Oak", "Pine", "Maple", "Cedar", "Elm", "Washington", "Lincoln"]

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

def generate_random_address():
    """
    Generates a random U.S. address with a street number, street name, city, state, and zip code.
    """
    street_number = random.randint(100, 9999)
    street_name = f"{random.choice(STREET_NAMES)} {random.choice(['St.', 'Ave.', 'Rd.', 'Blvd.', 'Dr.', 'Ln.'])}"
    city = random.choice(CITIES)
    state = random.choice(STATES)
    zip_code = f"{random.randint(10000, 99999)}"
    address = f"{street_number} {replace_address_abbreviations(street_name)}, {city}, {state} {zip_code}"
    return address

def generate_random_city_state():
    """
    Generates a random city and state for use in teacher records.
    """
    city = random.choice(CITIES)
    state = random.choice(STATES)
    return f"{city}, {state}"

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

def list_excel_files(directory):
    """
    Lists all Excel files in the specified directory.
    """
    files = [f for f in os.listdir(directory) if f.endswith(".xlsx")]
    if not files:
        print(f"No Excel files found in directory: {directory}")
        logging.info(f"No Excel files found in directory: {directory}")
        return []
    print(f"Excel files available in {directory}:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    return files

def process_all_excel_files(directory):
    """
    Processes all Excel files in the specified directory.
    After processing, prompts the user to delete the files.
    """
    files = list_excel_files(directory)
    if not files:
        return  # No files to process

    processed_files = []  # Keep track of successfully processed files

    for file_name in files:
        file_path = os.path.join(directory, file_name)
        try:
            df = pd.read_excel(file_path)

            # Validate required fields
            required_fields = ["Teacher Name", "Address", "Student Name", "Date", "Rank", "Number"]
            for field in required_fields:
                if field not in df.columns:
                    raise ValueError(f"Missing required column: {field}")
                if df[field].isnull().any() or (df[field] == "").any():
                    raise ValueError(f"Missing data in column: {field}")

            # Process the data into "Student Format"
            records = [
                (
                    capitalize_field(row["Teacher Name"]),
                    replace_address_abbreviations(row["Address"]),
                    capitalize_field(row["Student Name"]),
                    str(row["Date"]),
                    capitalize_field(row["Rank"]),
                    str(row["Number"])
                )
                for _, row in df.iterrows()
            ]

            # Save the processed records to a file
            filename = create_student_file(records)
            print(f"Processed {file_name} and saved to {filename}")
            logging.info(f"Processed {file_name} and saved to {filename}")
            processed_files.append(file_path)

        except Exception as e:
            print(f"Error processing file {file_name}: {e}")
            logging.error(f"Error processing file {file_name}: {e}")

    # Prompt to delete processed files
    if processed_files:
        delete_prompt = get_input("Do you want to delete the processed Excel files? (yes/no): ").lower()
        if delete_prompt == "yes":
            for file_path in processed_files:
                os.remove(file_path)
                print(f"Deleted {file_path}")
                logging.info(f"Deleted {file_path}")
        else:
            print("Processed files were not deleted.")
            logging.info("Processed files were not deleted.")

def get_input(prompt):
    """
    Get user input with the option to exit anytime by typing "exit".
    """
    value = input(prompt)
    if value.lower() == "exit":
        print("Exiting...")
        logging.info("User exited the script.")
        exit(0)  # Terminate the script immediately
    return value

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
        first_name = random.choice(FIRST_NAMES)
        middle_name = random.choice(MIDDLE_NAMES)
        last_name = random.choice(LAST_NAMES)
        hometown = generate_random_city_state()  # Use city and state only for teachers
        mentor = random.choice(["Grand Master Kim", "Grand Master Lee", "Grand Master Park"])
        nationality = random.choice(["American", "Korean", "Canadian"])
        teachers.append((title, first_name, middle_name, last_name, hometown, mentor, nationality))
    
    # Generate random student records
    for _ in range(num_students):
        teacher = random.choice(teachers)
        teacher_name = f"{teacher[0]} {teacher[1]} {teacher[2]} {teacher[3]}"
        address = generate_random_address()  # Full address for students
        student_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
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
        
        choice = get_input("Enter your choice: ").lower()
        if choice == "1":
            print(f"Excel files must be located in the directory: {EXCEL_DIR}")
            process_all_excel_files(EXCEL_DIR)
        elif choice == "2":
            print("Feature under development.")
        elif choice == "3":
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
