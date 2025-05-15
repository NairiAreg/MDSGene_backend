import pandas as pd
import os


def process_csv_to_excel(csv_filename, excel_filename):
    """
    Process data from a CSV file and add it to an Excel file according to specified rules.
    Removes duplicates both within the CSV file and checks against existing Excel records.

    The function performs the following transformations:
    - Variant: gene (protein)
    - hg19: chr{hg19}>{ref_alt}
    - snp_name: protein
    - locus: gene
    - submitter_email: joanne.trinh@uni-luebeck.de

    Args:
        csv_filename (str): Path to the CSV file to process
        excel_filename (str): Path to the Excel file to update
    """
    # Check if files exist
    if not os.path.exists(csv_filename):
        print(f"Error: CSV file '{csv_filename}' not found.")
        return

    if not os.path.exists(excel_filename):
        print(f"Error: Excel file '{excel_filename}' not found.")
        return

    try:
        # Read the CSV file
        print(f"Reading CSV file: {csv_filename}")
        csv_data = pd.read_csv(csv_filename)
        original_csv_count = len(csv_data)
        print(f"Found {original_csv_count} rows in the CSV file.")

        # Check for duplicates within the CSV file
        print("Checking for duplicates within the CSV file...")
        # Define columns to check for duplicates in the CSV
        csv_key_columns = ['gene', 'protein', 'hg19', 'ref_alt']

        # Count total rows before deduplication
        before_dedup = len(csv_data)

        # Remove duplicates within CSV data
        csv_data = csv_data.drop_duplicates(subset=csv_key_columns, keep='first')

        # Count rows after deduplication
        after_dedup = len(csv_data)
        internal_duplicates = before_dedup - after_dedup

        if internal_duplicates > 0:
            print(f"Removed {internal_duplicates} duplicate records from the CSV file.")
        else:
            print("No duplicate records found within the CSV file.")

        # Read the Excel file
        print(f"Reading Excel file: {excel_filename}")
        excel_data = pd.read_excel(excel_filename)

        # Create a new DataFrame with the transformed data
        new_data = pd.DataFrame()

        # Apply the transformation rules
        new_data['Variant'] = csv_data['gene'] + ' (' + csv_data['protein'] + ')'

        # For hg19 field, ensure it starts with 'chr', followed by the hg19 value, then '>' and ref_alt
        new_data['hg19'] = csv_data['hg19'].apply(lambda x: f"chr{x}") + '>' + csv_data['ref_alt']

        # Set the other fields as specified
        new_data['snp_name'] = csv_data['protein']
        new_data['locus'] = csv_data['gene']
        new_data['submitter_email'] = 'joanne.trinh@uni-luebeck.de'

        # Add any other columns from the Excel template that might be required
        for col in excel_data.columns:
            if col not in new_data.columns:
                new_data[col] = ''

        # Initialize counters for statistics
        total_records = len(new_data)
        added_records = 0
        duplicate_records = 0

        # Create a list to store only unique records
        unique_records = []

        # Check for duplicates based on key fields
        key_fields = ['Variant', 'hg19', 'snp_name', 'locus']

        # Convert existing Excel data to a set of tuples for faster lookup
        existing_records = set()
        for _, row in excel_data.iterrows():
            # Create a tuple of values for the key fields
            record_tuple = tuple(row[field] for field in key_fields if field in row)
            existing_records.add(record_tuple)

        # Check each new record
        for _, row in new_data.iterrows():
            # Create a tuple of values for the key fields
            record_tuple = tuple(row[field] for field in key_fields)

            # Check if this record already exists in Excel
            if record_tuple in existing_records:
                duplicate_records += 1
                print(f"Skipping duplicate record: {row['Variant']}")
            else:
                unique_records.append(row)
                added_records += 1
                # Add this record to existing_records to prevent duplicates if the same record appears multiple times
                existing_records.add(record_tuple)

        # If there are unique records to add
        if unique_records:
            # Convert the list of unique records to a DataFrame
            unique_data = pd.DataFrame(unique_records)

            # Combine the existing Excel data with the unique data
            result_data = pd.concat([excel_data, unique_data], ignore_index=True)

            # Save the updated data back to the Excel file
            print(f"Saving updated data to Excel file: {excel_filename}")
            result_data.to_excel(excel_filename, index=False)

            print(f"Successfully updated Excel file with {added_records} new records from {csv_filename}")
        else:
            print("No new records to add. Excel file remains unchanged.")

        # Print comprehensive statistics
        print(f"\nSummary:")
        print(f"Total records in original CSV: {original_csv_count}")
        print(f"Duplicate records within CSV: {internal_duplicates}")
        print(f"Unique records in CSV after internal deduplication: {total_records}")
        print(f"New records added to Excel: {added_records}")
        print(f"Records already in Excel (skipped): {duplicate_records}")

    except Exception as e:
        print(f"Error processing files: {str(e)}")


def main():
    """
    Main function to run the program, asking for the CSV filename and processing it.
    """
    print("CSV to Excel Processor (Full Duplicate Check)")
    print("--------------------------------------------")

    # Ask for the CSV filename
    csv_filename = input("Enter the CSV filename to process: ")

    # Default Excel filename (can be changed if needed)
    excel_filename = "excel-output\Ignacio_variant_list 1.xlsx"

    # Process the file
    process_csv_to_excel(csv_filename, excel_filename)


if __name__ == "__main__":
    main()