# generate_report.py

import pandas as pd
import subprocess
import os

def create_latex_report(patient_data, template_path, output_folder):
    """
    Generates and compiles a LaTeX report for a single patient.

    Args:
        patient_data (dict): A dictionary containing one patient's data.
        template_path (str): The file path to the master .tex template.
        output_folder (str): The folder to save the generated .tex and .pdf files.
    """
    print(f"--- Starting report for: {patient_data.get('PatientFirstName', 'N/A')} {patient_data.get('PatientLastName', 'N/A')} ---")

    # 1. Generate the string of \ValSet commands from the patient data
    # This block will be inserted into the LaTeX template.
    valset_definitions = []
    for key, value in patient_data.items():
        # Ensure values are strings and handle potential empty/NaN values from Excel
        # LaTeX is sensitive to special characters like #, $, %, &, etc.
        # We will escape them later if needed, but for this data it's okay.
        str_value = '' if pd.isna(value) else str(value)
        valset_definitions.append(f"\\ValSet{{{key}}}{{{str_value}}}")
    
    valset_string = "\n".join(valset_definitions)
    
    # 2. Read the master LaTeX template
    try:
        with open(template_path, 'r') as f:
            template_content = f.read()
    except FileNotFoundError:
        print(f"ERROR: Template file not found at '{template_path}'")
        return

    # 3. Replace the placeholder in the template with our \ValSet definitions
    # IMPORTANT: Your template must contain the line '%% -- DATA_INSERT_POINT -- %%'
    final_tex_content = template_content.replace('%% -- DATA_INSERT_POINT -- %%', valset_string)

    # 4. Define output file paths and save the new .tex file
    patient_name = f"{patient_data.get('PatientFirstName', 'Report')}_{patient_data.get('PatientLastName', 'Patient')}"
    output_tex_path = os.path.join(output_folder, f"Report_{patient_name}.tex")
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    with open(output_tex_path, 'w') as f:
        f.write(final_tex_content)
    
    print(f"Successfully created .tex file: {output_tex_path}")

    # 5. Compile the .tex file into a PDF using pdflatex
    # We run it twice to ensure all references (like page numbers) are correct.
    # The -output-directory flag places all auxiliary files (.log, .aux) in the output folder.
    for i in range(2): # Run twice
        process = subprocess.run(
            [
                'pdflatex',
                '-interaction=nonstopmode',
                '-output-directory', output_folder,
                output_tex_path
            ],
            capture_output=True, text=True
        )
        if process.returncode != 0:
            print(f"ERROR: LaTeX compilation failed on pass {i+1}.")
            print(process.stdout) # Print LaTeX log for debugging
            return

    print(f"✅ Successfully compiled PDF for {patient_name}!")
    print("--- Report generation complete ---\n")


if __name__ == '__main__':
    # --- This is a sample of what one row of data from your Excel file would look like ---
    # The keys MUST EXACTLY MATCH the names used in your LaTeX template.
    sample_patient_data = {
        'PatientFirstName': 'Charlotte',
        'PatientLastName': 'Yuki',
        'PatientDOB': '10/13/1985',
        'PatientSex': 'Female',
        'TestID': 'XG-987654',
        'Barcode': '100002',
        'PhysicianName': 'Dr. Susan Ray',
        'PhysicianSpecialty': 'Obstetrics Gynecology',
        'DateCollected': '10/01/2025',
        'DateReceived': '10/02/2025',
        'ReportDate': '10/13/2025',
        'Neisseria gonorrhoeae': '0',
        'Chlamydia trachomatis': '30.00',
        'Trichomonas vaginalis': '0',
        'Mycoplasma hominis': '35.00',
        'Mycoplasma genitalium': '15.00',
        'Haemophilus ducreyi': '0',
        'Treponema pallidum': '32.00',
        'Atopobium vaginae': '35.00',
        'BVAB2': '27.00',
        'Enterococcus faecalis': '27',
        'Gardnerella vaginalis': '25.00',
        'Megasphaera 1': '25.00',
        'Megasphaera 2': '0',
        'Mobiluncus mulieris': '0',
        'Prevotella bivia': '30.00',
        'Strep B/ S. agalactiae': '34.90',
        'Ureaplasma urealyticum': '0',
        'Candida albicans': '0',
        'Candida auris': '0',
        'Candida tropicalis': '0',
        'Candida krusei': '0',
        'Candida glabrata': '0',
        'HSV-1': '0',
        'HSV-2': '0',
        'Lactobacillus': '34',
        'Sample integrity control': '10'
    }

    # --- Configuration ---
    TEMPLATE_FILE = 'WH_template.tex'
    OUTPUT_FOLDER = 'generated_reports'

    # Run the report generation process
    create_latex_report(sample_patient_data, TEMPLATE_FILE, OUTPUT_FOLDER)