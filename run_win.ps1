# --- Automated Report Generation Runner (PowerShell) ---
# This script assumes you have a Python environment (like conda or system)
# with the required packages installed.

# --- Configuration ---
$MAIN_SCRIPT = "main.py"

# --- Main Logic ---
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Starting Report Generator " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# # 1. Check for Python
# if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
#     Write-Host " > ERROR: Python is not installed or not in PATH." -ForegroundColor Red
#     exit 1
# }

# # 2. Install/Check dependencies in the current environment
# Write-Host " > Checking/installing dependencies from requirements.txt..."
# pip install -r requirements.txt --quiet
# if ($LASTEXITCODE -ne 0) {
#     Write-Host " > ERROR: Failed to install dependencies. Please check your pip." -ForegroundColor Red
#     exit 1
# }

# --- Interactive Input ---
Write-Host ""
Write-Host "Please provide the paths to your data files."
Write-Host "You can drag and drop the file onto the terminal to get its full path."
Write-Host ""

# Prompt for the demographics file path
$demographics_path = Read-Host " > Enter path to DEMOGRAPHICS file"

# Prompt for the lab results file path
$results_path = Read-Host " > Enter path to LAB RESULTS file"

# Remove surrounding quotes if present (Windows often adds them when drag-dropping)
$demographics_path = $demographics_path.Trim('"')
$results_path = $results_path.Trim('"')

# Check if inputs are empty
if ([string]::IsNullOrWhiteSpace($demographics_path) -or [string]::IsNullOrWhiteSpace($results_path)) {
    Write-Host ""
    Write-Host " > ERROR: Both file paths are required. Exiting." -ForegroundColor Red
    exit 1
}

# --- End of new input section ---

# 3. Run the main Python script
Write-Host ""
Write-Host " > All checks passed. Starting the report generator..." -ForegroundColor Green
Write-Host ""

# Pass the collected paths as arguments to the main script
# Using & to invoke python with proper argument handling
& python $MAIN_SCRIPT --demographics "$demographics_path" --results "$results_path"

# --- UPDATED: Optional Copy Step ---
Write-Host ""
Write-Host " > Report generation process finished." -ForegroundColor Green
Write-Host ""

$copy_path = Read-Host " > (Optional) Enter a destination path to COPY the PDFs to (or press Enter to skip)"

if (-not [string]::IsNullOrWhiteSpace($copy_path)) {
    # Remove surrounding quotes if present
    $copy_path = $copy_path.Trim('"')
    
    Write-Host " > Copying all *.pdf files from 'output' to '$copy_path'..." -ForegroundColor Yellow
    
    # Check if output directory exists
    if (-not (Test-Path "output")) {
        Write-Host " > ERROR: 'output' directory not found." -ForegroundColor Red
    }
    else {
        # Create destination directory if it doesn't exist
        if (-not (Test-Path $copy_path)) {
            New-Item -Path $copy_path -ItemType Directory -Force | Out-Null
        }
        
        # Copy all PDF files recursively, preserving directory structure
        try {
            Get-ChildItem -Path "output" -Filter "*.pdf" -Recurse | ForEach-Object {
                $relativePath = $_.FullName.Substring((Get-Location).Path.Length + 8)  # +8 for "\output\"
                $destinationPath = Join-Path $copy_path $relativePath
                $destinationDir = Split-Path $destinationPath -Parent
                
                # Create directory structure if it doesn't exist
                if (-not (Test-Path $destinationDir)) {
                    New-Item -Path $destinationDir -ItemType Directory -Force | Out-Null
                }
                
                # Copy the file
                Copy-Item -Path $_.FullName -Destination $destinationPath -Force
            }
            Write-Host " > Successfully copied PDF files." -ForegroundColor Green
        }
        catch {
            Write-Host " > ERROR: Failed to copy files. $_" -ForegroundColor Red
        }
    }
}
else {
    Write-Host " > Skipping copy step."
}

# --- End of updated copy step ---

# 4. Finish
Write-Host ""
Write-Host " > Process finished." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")