import pandas as pd
import sys
from datetime import datetime

def validate_data(df):
    """
    Performs validation checks on the merged DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing merged patient and lab data.
    """
    print("\n--- Validating Data ---")
    
    # 1. Define columns that should contain dates
    date_columns = ['PatientDOB', 'DateCollected', 'DateReceived', 'ReportDate']
    today = datetime.now()
    
    # 2. Iterate through each row to check the dates
    for index, row in df.iterrows():
        for col in date_columns:
            if col in row and pd.notna(row[col]):
                try:
                    # Convert the cell to a datetime object for comparison
                    cell_date = pd.to_datetime(row[col])
                    if cell_date > today:
                        print(
                            f"  > WARNING: Future date found in row {index + 2} "
                            f"(Barcode: {row.get('Barcode', 'N/A')}, TestID: {row.get('TestID', 'N/A')}).\n"
                            f"    Column '{col}' has date {cell_date.strftime('%Y-%m-%d')}, which is after today."
                        )
                except (ValueError, TypeError):
                    # This handles cases where the date format is incorrect
                    print(
                        f"  > WARNING: Invalid date format in row {index + 2} "
                        f"(Barcode: {row.get('Barcode', 'N/A')}, TestID: {row.get('TestID', 'N/A')}).\n"
                        f"    Column '{col}' has value '{row[col]}'."
                    )
    
    print("Validation complete.")


def load_and_merge_data(demographics_path, results_path):
    """
    Loads patient demographics and lab results from Excel files and merges them.
    (This function remains the same as before)
    """
    print("--- Loading Data ---")
    try:
        demographics_df = pd.read_excel(demographics_path)
        results_df = pd.read_excel(results_path)
        print("Successfully loaded Excel files.")
    except FileNotFoundError as e:
        print(f"ERROR: Could not find a data file. {e}", file=sys.stderr)
        return None

    print("Merging datasets on 'Barcode'...")
    merged_df = pd.merge(results_df, demographics_df, on='Barcode', how='left')
    
    unmatched_results = merged_df[merged_df['PatientFirstName'].isnull()]
    if not unmatched_results.empty:
        print("\nWARNING: The following barcodes in lab_results.xlsx did not have a matching patient:", file=sys.stderr)
        for barcode in unmatched_results['Barcode']:
            print(f"- {barcode}", file=sys.stderr)
        print("These records will be skipped.\n", file=sys.stderr)
    
    merged_df.dropna(subset=['PatientFirstName'], inplace=True)

    return merged_df

