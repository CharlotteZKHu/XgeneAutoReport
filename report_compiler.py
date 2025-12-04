import subprocess
import os
import pandas as pd
import sys
import re 
import config 
from datetime import datetime

# --- CONFIGURATION ---
# Use a list of tuples to GUARANTEE replacement order.
# Backslash MUST be escaped first to solve the \textbackslash{} bug.
LATEX_SPECIAL_CHARS = [
    ('\\', r'\textbackslash{}'), 
    ('&', r'\&'),
    ('%', r'\%'),
    ('$', r'\$'),
    ('#', r'\#'),
    ('_', r'\_'),
    ('{', r'\{'),
    ('}', r'\}'),
    ('~', r'\textasciitilde{}'),
    ('^', r'\textasciicircum{}'),
]

def _sanitize_for_filename(text_string):
    """
    Removes spaces, slashes, and other risky characters for a filename.
    Used to generate safe PDF file names.
    """
    if not isinstance(text_string, str):
        text_string = str(text_string)
    
    # Replace spaces with nothing
    text_string = text_string.replace(' ', '')
    # Remove any character that is not a letter, number, hyphen, or underscore
    text_string = re.sub(r'[^\w\-_]', '', text_string)
    return text_string

def _validate_record_integrity(report_data):
    """
    Checks for data issues and prints warnings to the console.
    The GUI will detect the 'WARNING' keyword and color it red.
    """
    warnings = []
    today = datetime.now()
    
    # 1. Check Dates (Future Check)
    # We loop through all known date fields to ensure they aren't in the future.
    for field in config.DATE_FIELDS:
        val = report_data.get(field)
        # Check if value exists and is not empty string
        if pd.notna(val) and str(val).strip() != '':
            try:
                # Handle both datetime objects and strings
                if isinstance(val, (datetime, pd.Timestamp)):
                    date_val = val
                else:
                    date_val = pd.to_datetime(val)
                
                if date_val > today:
                     # Added emoji back
                     warnings.append(f"  > ❗ WARNING: Future date detected in '{field}': {date_val.strftime('%m/%d/%Y')}")
            except Exception:
                # If date parsing fails, we ignore it here (it might just be empty or weird text)
                pass

    # 2. Check Missing Values (Required Text Fields)
    # We assume all text fields defined in config are mandatory (except ReportDate).
    for field in config.TEXT_FIELDS:
        # Skip ReportDate because we auto-fill it later if it's missing
        if field == 'ReportDate': 
            continue 
        
        val = report_data.get(field)
        # Check for NaN, None, or empty string (after stripping whitespace)
        if pd.isna(val) or str(val).strip() == '':
            # Added emoji back
            warnings.append(f"  > ❗ WARNING: Missing value for variable '{field}'")
    
    # Print all warnings found so the user can see them
    if warnings:
        for w in warnings:
            print(w)

def generate_valset_string(report_data):
    """
    Creates the LaTeX \ValSet string from a dictionary of data
    with improved sanitization, date formatting, and NaN handling.
    """
    definitions = []
    
    # --- LOGIC: Conditional ReportDate ---
    # If the ReportDate is missing in the Excel file, default to Today.
    current_date_val = report_data.get('ReportDate')
    is_empty = pd.isna(current_date_val) or (isinstance(current_date_val, str) and not current_date_val.strip())

    if is_empty:
        report_data['ReportDate'] = datetime.now()

    for key, value in report_data.items():
        
        # --- LOGIC: Robust Empty Check ---
        # Check if value is NaN OR an empty string (after stripping whitespace)
        is_val_empty = pd.isna(value) or (str(value).strip() == "")
        
        # 1. Handle Empty Values
        if is_val_empty:
            if key in config.TEXT_FIELDS:
                str_value = ''  # Empty string for text/info fields
            else:
                str_value = '0' # '0' for all other (lab result) fields (prevents LaTeX crash)
        
        # 2. Handle Existing Values
        else:
            # --- Check for date formatting ---
            if key in config.DATE_FIELDS and isinstance(value, (datetime, pd.Timestamp)):
                # Format as MM/DD/YYYY
                str_value = value.strftime('%m/%d/%Y')
            else:
                # Just convert to string as before
                str_value = str(value)
        
        # 3. Apply LaTeX sanitization
        if key in config.TEXT_FIELDS:
            # This is a known text field, sanitize it.
            for char, escaped_char in LATEX_SPECIAL_CHARS:
                str_value = str_value.replace(char, escaped_char)
        else:
            # --- Handle non-numeric lab results ---
            # This is a lab result. Only sanitize if it's not a pure number.
            try:
                # Try to convert to float. If it works, it's a number.
                float(str_value)
                # It's a number, do not sanitize.
            except ValueError:
                # It's not a number (e.g., 'Detected', '10^5', 'Pending')
                # We MUST sanitize it so chars like '^' don't break LaTeX.
                for char, escaped_char in LATEX_SPECIAL_CHARS:
                    str_value = str_value.replace(char, escaped_char)

        definitions.append(f"\\ValSet{{{key}}}{{{str_value}}}")
        
    return "\n".join(definitions)

def compile_single_report(report_data, template_path, base_output_folder, panel_name, result_sheet_name):
    """
    Generates and compiles a single LaTeX report.
    """
    
    # --- 1. Create New Filename ---
    test_id = _sanitize_for_filename(report_data.get('TestID', 'UnknownTestID'))
    panel = _sanitize_for_filename(panel_name) # Use the master panel name
    fname = _sanitize_for_filename(report_data.get('PatientFirstName', 'NoFirstName'))
    lname = _sanitize_for_filename(report_data.get('PatientLastName', 'NoLastName'))
    patient_name = f"{fname}{lname}"
    
    # Format: XG12345_WHP_JaneDoe_Report
    base_filename = f"{test_id}_{panel}_{patient_name}_Report"

    print(f"--- Processing: {patient_name} (Test ID: {test_id}) ---")
    
    # --- Run Integrity Checks Here ---
    # This will print warnings directly below the "Processing..." line
    _validate_record_integrity(report_data)

    # --- 2. Create New Output Subfolder ---
    # We organize by the Result Sheet name (e.g., "WH", "UTI")
    panel_output_folder = os.path.join(base_output_folder, result_sheet_name)
    if not os.path.exists(panel_output_folder):
        os.makedirs(panel_output_folder)

    # 3. Prepare LaTeX content
    valset_string = generate_valset_string(report_data)
    with open(template_path, 'r') as f:
        template_content = f.read()
    final_tex_content = template_content.replace('%% -- DATA_INSERT_POINT -- %%', valset_string)

    # 4. Save the temporary .tex file (in the new subfolder)
    output_tex_path = os.path.join(panel_output_folder, f"{base_filename}.tex")
    
    with open(output_tex_path, 'w') as f:
        f.write(final_tex_content)
    print(f"  > Generated .tex file: {os.path.basename(output_tex_path)}")

    # --- WINDOWS CONSOLE SUPPRESSION ---
    # This ensures pdflatex doesn't pop up black windows on Windows OS
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    # -----------------------------------

    # 5. Compile the PDF using pdflatex
    for i in range(2):
        cmd = [
            "pdflatex", 
            "-interaction=nonstopmode", 
            f"-jobname={base_filename}", 
            f"-output-directory={panel_output_folder}", # Tell pdflatex where to put files
            output_tex_path
        ]
        # Pass startupinfo to hide the window
        process = subprocess.run(cmd, capture_output=True, text=True, startupinfo=startupinfo)
        
        if process.returncode != 0:
            print(f"  > ERROR: LaTeX compilation failed on run {i+1}.", file=sys.stderr)
            print(f"  > See log file for details: {os.path.join(panel_output_folder, f'{base_filename}.log')}", file=sys.stderr)
            return False

    # Added emoji back
    print(f"  > ✅ SUCCESS: PDF compiled") 
    return True