import pandas as pd
import sys
from datetime import datetime
import config # Import our config file

def _deduplicate_columns(columns):
    """Ensures all column names are unique by appending _1, _2, etc."""
    seen = {}
    new_columns = []
    for col in columns:
        # Handle empty/nan headers
        if pd.isna(col) or col == '':
            col = 'Unnamed' # Give a placeholder name

        if col not in seen:
            seen[col] = 1
            new_columns.append(col)
        else:
            count = seen[col]
            new_name = f"{col}_{count}"
            seen[col] += 1
            new_columns.append(new_name)
    return new_columns

def load_demographics(demographics_path):
    """Loads the patient demographics file."""
    print(f"--- Loading Demographics from {demographics_path} ---")
    try:
        df = pd.read_excel(demographics_path)
        return df
    except FileNotFoundError:
        print(f"ERROR: Patient demographics file not found at {demographics_path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ERROR: Failed to read demographics file. {e}", file=sys.stderr)
        return None

def load_crosswalk(results_path):
    """Loads the Crosswalk sheet from the lab results file."""
    print(f"--- Loading Crosswalk from {results_path} ---")
    try:
        # Load the crosswalk and set 'Panel' as the index for easy lookup
        crosswalk_df = pd.read_excel(results_path, sheet_name=config.CROSSWALK_SHEET_NAME)
        crosswalk_df.set_index('Panel', inplace=True)
        return crosswalk_df
    except FileNotFoundError:
        print(f"ERROR: Lab results file not found at {results_path}", file=sys.stderr)
        return None
    except KeyError:
        print(f"ERROR: The file at {results_path} does not contain a sheet named '{config.CROSSWALK_SHEET_NAME}'", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ERROR: Failed to read crosswalk. {e}", file=sys.stderr)
        return None

def load_all_results_sheets(results_path, crosswalk_df):
    """
    Loads all lab result sheets from the Excel file into a dictionary of DataFrames.
    It skips the Crosswalk sheet and handles the new complex header format.
    
    CRITICAL CHANGE: It now only loads sheets listed in the crosswalk.
    """
    print(f"--- Loading All Result Sheets from {results_path} ---")
    try:
        xls = pd.ExcelFile(results_path)
        all_available_sheets = xls.sheet_names
        
        # Get a unique list of sheet names we *actually* need to parse
        unique_sheets_to_load = crosswalk_df['Result Sheet'].unique()
        
        results_sheets = {}
        for sheet_name in unique_sheets_to_load:
            
            # Check if the required sheet even exists in the file
            if sheet_name not in all_available_sheets:
                print(f"  > ERROR: Crosswalk references sheet '{sheet_name}' but it's not in the Excel file. Skipping this sheet.", file=sys.stderr)
                continue
                
            print(f"  > Parsing required sheet: {sheet_name}")
            
            # This new format is complex. We must read it in parts.
            # header=None gets all data without assuming a header.
            raw_df = xls.parse(sheet_name, header=None)
            
            # 1. Get Pathogen Names (from Row 2, Column D onwards)
            # .iloc[1] = Row 2. [3:] = Column D onwards.
            # .fillna(method='ffill') will handle merged cells, just in case.
            pathogen_headers = raw_df.iloc[1, 3:].fillna(method='ffill').tolist()
            
            # 2. Get the 'Barcode' and 'Panel' headers (from Row 3)
            # .iloc[2] = Row 3. [1] = Column B, [2] = Column C
            barcode_header = raw_df.iloc[2, 1]
            panel_header = raw_df.iloc[2, 2]
            
            # 3. Create the full list of final column names
            #    (Filter out nans from headers before combining)
            clean_pathogen_headers = [h for h in pathogen_headers if pd.notna(h) and h != '']
            final_column_names = [barcode_header, panel_header] + clean_pathogen_headers
            
            # --- NEW FIX: Deduplicate column names ---
            final_column_names_unique = _deduplicate_columns(final_column_names)
            
            # 4. Get the actual data (from Row 4 onwards)
            # .iloc[3:] = Row 4 onwards.
            data_df = raw_df.iloc[3:]
            
            # 5. Select only the columns we need (Column B onwards)
            # and stop at the end of our defined headers
            num_cols = len(final_column_names_unique) # Use new unique list
            # .iloc[:, 1:num_cols+1] = All rows, from Column B to (B + num_cols)
            data_subset = data_df.iloc[:, 1:num_cols+1]
            
            # 6. Set the column names and reset the index
            data_subset.columns = final_column_names_unique # Use new unique list
            data_subset = data_subset.reset_index(drop=True)
            
            # 7. Drop any rows where the Barcode is empty (e.g., extra empty rows)
            data_subset = data_subset.dropna(subset=[barcode_header]) # Use the dynamic header name
            
            results_sheets[sheet_name] = data_subset

        if not results_sheets:
            print(f"WARNING: No result sheets found in {results_path} (besides Crosswalk).", file=sys.stderr)
            
        return results_sheets
        
    except FileNotFoundError:
        print(f"ERROR: Lab results file not found at {results_path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ERROR: Failed to read results sheets from {results_path}. {e}", file=sys.stderr)
        return None


def validate_data(df_row, row_index):
    """
    Performs validation checks on a single merged row (as a DataFrame).
    """
    # 1. Define columns that should contain dates
    # --- CHANGE: Removed 'ReportDate' as it will be overwritten ---
    date_columns = ['PatientDOB', 'DateCollected', 'DateReceived']
    today = datetime.now()
    
    # 2. Iterate through columns to check dates
    for col in date_columns:
        if col in df_row.columns and pd.notna(df_row.iloc[0][col]):
            try:
                # Convert the cell to a datetime object for comparison
                cell_date = pd.to_datetime(df_row.iloc[0][col])
                if cell_date > today:
                    print(
                        f"  > WARNING: Future date found in data row {row_index} "
                        f"(Barcode: {df_row.iloc[0].get('Barcode', 'N/A')}, TestID: {df_row.iloc[0].get('TestID', 'N/A')}).\n"
                        f"    Column '{col}' has date {cell_date.strftime('%Y-%m-%d')}, which is after today."
                    )
            except (ValueError, TypeError):
                # This handles cases where the date format is incorrect
                print(
                    f"  > WARNING: Invalid date format in data row {row_index} "
                    f"(Barcode: {df_row.iloc[0].get('Barcode', 'N/A')}, TestID: {df_row.iloc[0].get('TestID', 'N/A')}).\n"
                    f"    Column '{col}' has value '{df_row.iloc[0][col]}'."
                )