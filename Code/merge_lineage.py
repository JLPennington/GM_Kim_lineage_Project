import os
import datetime
import logging
from tqdm import tqdm

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

def read_txt_files_from_directory(directory):
    """Read all .txt files from the specified directory and return their contents."""
    data = []
    file_paths = []
    try:
        if not os.path.exists(directory):
            logging.error(f"Directory not found: {directory}")
            return data, file_paths

        for filename in os.listdir(directory):
            if filename.endswith(".txt"):
                file_path = os.path.join(directory, filename)
                file_paths.append(file_path)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data.extend(line.strip() for line in file)
    except Exception as e:
        logging.error(f"Error reading files: {e}")
    return data, file_paths

def remove_duplicates(data):
    """Remove duplicate entries from the data."""
    return list(set(data))

def save_to_file(data, directory):
    """Save the deduplicated data to a new file with a date-time formatted name."""
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(directory, f"merged_{timestamp}.txt")

        with open(output_file, 'w', encoding='utf-8') as file:
            file.writelines(f"{line}\n" for line in data)

        logging.info(f"Merged file saved as: {output_file}")
    except Exception as e:
        logging.error(f"Error saving file: {e}")

def delete_original_files(file_paths):
    """Delete the original files that were processed."""
    try:
        for file_path in tqdm(file_paths, desc="Deleting files"):
            os.remove(file_path)
        logging.info("Original files deleted.")
    except Exception as e:
        logging.error(f"Error deleting files: {e}")

def main():
    """Main function to execute the merging process."""
    setup_logging()

    raw_data_directory = "RAW Data"

    logging.info("Reading files from directory...")
    data, file_paths = read_txt_files_from_directory(raw_data_directory)

    if not data:
        logging.warning("No records found to process.")
        return

    logging.info(f"Total records before processing: {len(data)}")

    logging.info("Removing duplicate entries...")
    unique_data = remove_duplicates(data)

    logging.info(f"Total records after processing: {len(unique_data)}")

    logging.info("Saving merged data...")
    save_to_file(unique_data, raw_data_directory)

    logging.info("Deleting original files...")
    delete_original_files(file_paths)

if __name__ == "__main__":
    main()
