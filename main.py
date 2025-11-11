import config
import data_handler
import report_compiler
import os
import sys
import pandas as pd
import argparse # <-- Import the argparse library

def main():
    """Main function to orchestrate the report generation process."""
    
    # --- NEW: Set up command-line argument parsing ---
    parser = argparse.ArgumentParser(description="Automated Patient Report Generator (Multi-Panel)")
    parser.add_argument(
        '-d', '--demographics', 
        help="Path to the patient demographics Excel file.", 
        required=True
    )
    parser.add_argument(
        '-r', '--results', 
        help="Path to the lab results Excel file (containing the Crosswalk).", 
        required=True
    )
    args = parser.parse_args()
    # --- End of new argument parsing ---

    print("=============================================")
    print("   Automated Patient Report Generator (Multi-Panel)")
    print("=============================================")
    
    # Step 1: Load all necessary data (using paths from 'args')
    demographics_df = data_handler.load_demographics(args.demographics)
    crosswalk_df = data_handler.load_crosswalk(args.results)
    
    # CRITICAL CHANGE: Pass the crosswalk_df to the sheet loader.
    # This tells the loader *which* sheets to parse, avoiding junk sheets.
    results_sheets_dict = data_handler.load_all_results_sheets(args.results, crosswalk_df)

    if demographics_df is None or crosswalk_df is None or not results_sheets_dict:
        print("ERROR: Failed to load critical data. Exiting.", file=sys.stderr)
        return

    print("\n--- Starting Report Generation Process ---")
    
    success_count = 0
    failure_count = 0
    total_reports_to_generate = 0

    # Step 2: Iterate through each PATIENT in the demographics file
    for _, patient_row in demographics_df.iterrows():
        patient_barcode = patient_row['Barcode']
        patient_panel = patient_row['Panel'] # This is the Panel name, e.g., "WHP"
        
        # Step 3: Use the Crosswalk to find the correct template and sheet
        try:
            crosswalk_entry = crosswalk_df.loc[patient_panel]
            template_name = crosswalk_entry['Result Template']
            result_sheet_name = crosswalk_entry['Result Sheet'] # This is the sheet, e.g., "WH" or "UTI"
        except KeyError:
            print(f"  > ERROR: Panel '{patient_panel}' for Barcode '{patient_barcode}' not found in Crosswalk. Skipping patient.", file=sys.stderr)
            failure_count += 1
            continue

        # Construct the full path to the required .tex template
        template_path = os.path.join(config.TEMPLATE_DIR, f"{template_name}.tex")
        if not os.path.exists(template_path):
            print(f"  > ERROR: Template file not found: {template_path}. Skipping patient.", file=sys.stderr)
            failure_count += 1
            continue

        # Step 4: Get the correct results DataFrame (e.g., the 'WH' sheet)
        if result_sheet_name not in results_sheets_dict:
            print(f"  > ERROR: Result Sheet '{result_sheet_name}' (from Crosswalk) not found in Excel file. Skipping patient.", file=sys.stderr)
            failure_count += 1
            continue
        
        results_df = results_sheets_dict[result_sheet_name]

        # Step 5: Find all results for this patient in that sheet
        patient_results_df = results_df[results_df['Barcode'] == patient_barcode]

        if patient_results_df.empty:
            print(f"  > INFO: No results found for Barcode '{patient_barcode}' in sheet '{result_sheet_name}'.")
            continue
            
        total_reports_to_generate += len(patient_results_df)

        # Step 6: Iterate through each LAB RESULT for that patient
        for result_index, result_row in patient_results_df.iterrows():
            
            # Merge patient info + one lab result
            # Need to convert rows to DataFrames for a clean merge
            patient_df_row = pd.DataFrame([patient_row])
            result_df_row = pd.DataFrame([result_row])
            
            # Merge on Barcode, dropping duplicate columns from the patient info
            merged_record_df = pd.merge(result_df_row, patient_df_row.drop(columns=['Panel']), on='Barcode', how='left')

            # Step 7: Validate the single, merged record
            data_handler.validate_data(merged_record_df, f"{result_sheet_name} row {result_index + 2}")
            
            # Convert the single-row DataFrame back to a dictionary for compilation
            record_dict = merged_record_df.to_dict('records')[0]
            
            # Step 8: Compile the report
            # --- UPDATED: Pass patient_panel and result_sheet_name ---
            success = report_compiler.compile_single_report(
                record_dict, 
                template_path,
                config.OUTPUT_DIR,
                patient_panel,      # e.g., "WHP" or "WIP-CPP+WHP"
                result_sheet_name   # e.g., "WH" or "UTI"
            )
            if success:
                success_count += 1
            else:
                failure_count += 1
            print("-" * 45)

    # Step 9: Print a final summary
    print("=============================================")
    print("      Report Generation Summary")
    print(f"  Total reports found to generate: {total_reports_to_generate}")
    print(f"  Successfully generated: {success_count} reports")
    if failure_count > 0:
        print(f"  Failed to generate:   {failure_count} reports (see errors above)")
    print("=============================================")

if __name__ == '__main__':
    main()