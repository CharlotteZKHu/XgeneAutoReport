import config
import data_handler
import report_compiler

def main():
    """Main function to orchestrate the report generation process."""
    print("=============================================")
    print("   Automated Patient Report Generator")
    print("=============================================")
    
    # Step 1: Load and merge the data
    merged_data = data_handler.load_and_merge_data(
        config.DEMOGRAPHICS_FILE, 
        config.RESULTS_FILE
    )

    if merged_data is None or merged_data.empty:
        print("No data to process. Exiting.")
        return
        
    # Step 2: Validate the merged data
    data_handler.validate_data(merged_data)

    print(f"\nFound {len(merged_data)} total reports to generate.\n")
    
    # Step 3: Iterate through records and compile a report for each
    records = merged_data.to_dict(orient='records')
    success_count = 0
    failure_count = 0
    
    for record in records:
        success = report_compiler.compile_single_report(
            record, 
            config.LATEX_TEMPLATE, 
            config.OUTPUT_DIR
        )
        if success:
            success_count += 1
        else:
            failure_count += 1
        print("-" * 45)

    # Step 4: Print a final summary
    print("=============================================")
    print("      Report Generation Summary")
    print(f"  Successfully generated: {success_count} reports")
    if failure_count > 0:
        print(f"  Failed to generate:   {failure_count} reports")
    print("=============================================")

if __name__ == '__main__':
    main()

