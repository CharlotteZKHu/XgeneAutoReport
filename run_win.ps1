# --- Automated Report Generation Runner for Windows PowerShell ---
$MainScript = "main.py"

Write-Host "=========================================="
Write-Host " Starting Report Generator Setup Check... "
Write-Host "=========================================="
Write-Host ""

Write-Host "Please provide the paths to your data files."
Write-Host "You can drag and drop the file onto the PowerShell window to get its full path."
Write-Host ""

$demographics_path = Read-Host " > Enter path to DEMOGRAPHICS file"
$results_path      = Read-Host " > Enter path to LAB RESULTS file"

if ([string]::IsNullOrWhiteSpace($demographics_path) -or
    [string]::IsNullOrWhiteSpace($results_path)) {
    Write-Host ""
    Write-Host " > ERROR: Both file paths are required. Exiting."
    exit 1
}

# Convert any backslashes to forward slashes for Python compatibility
$demographics_path = $demographics_path -replace '\\', '/'
$results_path      = $results_path -replace '\\', '/'

Write-Host ""
Write-Host " > All checks passed. Starting the report generator..."
Write-Host ""

python "$MainScript" --demographics "$demographics_path" --results "$results_path"

Write-Host ""
Write-Host " > Process finished."
Write-Host "=========================================="