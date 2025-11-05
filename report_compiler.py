import subprocess
import os
import pandas as pd
import sys
import config  # Import the configuration file
from datetime import datetime # Import datetime for type checking

# Use a list of tuples to GUARANTEE replacement order.
# Backslash MUST be escaped first to solve the \textbackslash{} bug.
LATEX_SPECIAL_CHARS = [
    ('\\', r'\textbackslash{}'), # Must be first!
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

def generate_valset_string(report_data):
    """
    Creates the LaTeX \ValSet string from a dictionary of data
    with improved sanitization, date formatting, and NaN handling.
    """
    definitions = []
    
    # --- NEW LOGIC: Overwrite ReportDate with today's date ---
    # This ensures the report is always dated as "today".
    report_data['ReportDate'] = datetime.now()
    # --- End of new logic ---

    for key, value in report_data.items():
        
        # 1. Handle NaN (empty) values first
        if pd.isna(value):
            if key in config.TEXT_FIELDS:
                str_value = ''  # Empty string for text/info fields
            else:
                str_value = '0' # '0' for all other (lab result) fields
        
        # 2. Handle non-NaN (existing) values
        else:
            # --- UPDATED LOGIC: Check for date formatting ---
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
            # --- NEW FIX: Handle non-numeric lab results ---
            # This is a lab result. Only sanitize if it's not a pure number.
            try:
                # Try to convert to float. If it works, it's a number.
                float(str_value)
                # It's a number, do not sanitize.
            except ValueError:
                # It's not a number (e.g., 'Detected', '10^5', 'Pending')
                # We MUST sanitize it.
                for char, escaped_char in LATEX_SPECIAL_CHARS:
                    str_value = str_value.replace(char, escaped_char)

        definitions.append(f"\\ValSet{{{key}}}{{{str_value}}}")
        
    return "\n".join(definitions)

def compile_single_report(report_data, template_path, output_folder):
    """
    Generates and compiles a single LaTeX report.
    (This function remains unchanged from before)
    """
    patient_name = f"{report_data.get('PatientFirstName', 'Report')}_{report_data.get('PatientLastName', 'Patient')}"
    test_id = report_data.get('TestID', 'UnknownTest')
    print(f"--- Processing: {patient_name} (Test ID: {test_id}) ---")

    # 1. Prepare LaTeX content
    valset_string = generate_valset_string(report_data)
    with open(template_path, 'r') as f:
        template_content = f.read()
    final_tex_content = template_content.replace('%% -- DATA_INSERT_POINT -- %%', valset_string)

    # 2. Save the temporary .tex file
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    base_filename = f"Report_{patient_name}_{test_id}"
    output_tex_path = os.path.join(output_folder, f"{base_filename}.tex")
    
    with open(output_tex_path, 'w') as f:
        f.write(final_tex_content)
    print(f"  > Generated .tex file: {os.path.basename(output_tex_path)}")

    # 3. Compile the PDF using pdflatex
    for i in range(2):
        cmd = ["pdflatex", "-interaction=nonstopmode", f"-jobname={base_filename}", f"-output-directory={output_folder}", output_tex_path]
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        if process.returncode != 0:
            print(f"  > ERROR: LaTeX compilation failed on run {i+1}.", file=sys.stderr)
            print(f"  > See log file for details: {os.path.join(output_folder, f'{base_filename}.log')}", file=sys.stderr)
            return False

    print(f"  > ✅ Successfully compiled PDF!")
    return True