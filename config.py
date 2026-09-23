import os

# --- Project Root ---
# Finds the absolute path of the directory this file is in (which is the project root)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Input/Output Folders ---
DATA_DIR = os.path.join(PROJECT_DIR, 'data')
TEMPLATE_DIR = os.path.join(PROJECT_DIR, 'templates')
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'output')
ASSETS_DIR = os.path.join(PROJECT_DIR, 'assets') # Path for images

# --- File Names ---
# REMOVED: DEMOGRAPHICS_FILE - This will now be a command-line argument.
# REMOVED: RESULTS_FILE - This will also be a command-line argument.

# --- NEW: Crosswalk Configuration ---
CROSSWALK_SHEET_NAME = "Crosswalk"

# --- Data Type Definitions ---
# List of all column headers that should be treated as text.
# Any column NOT in this list will be treated as a numerical lab result.
# This controls both NaN filling ('' vs '0') and LaTeX sanitization.
TEXT_FIELDS = [
    'PatientFirstName',
    'PatientLastName',
    'PatientDOB',
    'PatientSex',
    'TestID',
    'Barcode',
    'PhysicianName',
    'PhysicianSpecialty',
    'DateCollected',
    'DateReceived',
    'ReportDate',
    'Panel',
    'SampleType'
]

# --- Date Formatting ---
# List of fields that should be formatted as MM/DD/YYYY
# This is a subset of TEXT_FIELDS.
DATE_FIELDS = [
    'PatientDOB',
    'DateCollected',
    'DateReceived',
    'ReportDate'
]

# --- NEW: Enhanced Date Validation Categories ---
# All date fields in the system (same as DATE_FIELDS for compatibility)
ALL_DATE_FIELDS = DATE_FIELDS

# Date fields that SHOULD be in the past (birthdate)
# These will only be checked for future dates, NOT for being old
HISTORICAL_DATE_FIELDS = [
    'PatientDOB'
]

# Date fields that should ideally be TODAY or very recent
# These will be checked for BOTH future dates AND old dates (not today)
CURRENT_DATE_FIELDS = [
    'DateCollected',
    'DateReceived', 
    'ReportDate'
]


# --- Unified WH template routing ---
# Keep legacy Crosswalk Result Template names; all four use one .tex file.
# Whitespace, hyphens, and underscores between words/numbers are accepted.
import re


def resolve_template(template_name):
    """Return (template_path, WH variant), with None for non-WH templates."""
    name = str(template_name).strip()
    if name.lower().endswith('.tex'):
        name = name[:-4]

    match = re.fullmatch(r'WH[\s_-]*template[\s_-]*([1-4])', name, flags=re.IGNORECASE)
    if match:
        return os.path.join(TEMPLATE_DIR, 'WH_template.tex'), int(match.group(1))
    if re.fullmatch(r'WH[\s_-]*template', name, flags=re.IGNORECASE):
        return os.path.join(TEMPLATE_DIR, 'WH_template.tex'), 1

    # Non-WH panels continue using the names in their Crosswalk unchanged.
    return os.path.join(TEMPLATE_DIR, f'{name}.tex'), None


# --- WH client-specific presentation rules ---
# Patient demographics mapping in data_handler.py:
#   Excel "Physician"  -> PhysicianName
#   Excel "FACILITIES" -> PhysicianSpecialty
# Match BOTH fields so other physicians or facilities keep standard WH reports.
WH_NO_STI_PHYSICIAN = "Dena Geiger"
WH_NO_STI_FACILITY = "Glacier Womens Health and Wellness"


def _normalized_customer_field(value):
    """Case-insensitive, whitespace-tolerant match without fuzzy name guessing."""
    return " ".join(str(value).split()).casefold()


def should_hide_wh_stis(report_data):
    """True only for the designated physician AND facility, for WH reports."""
    return (
        _normalized_customer_field(report_data.get("PhysicianName", ""))
        == _normalized_customer_field(WH_NO_STI_PHYSICIAN)
        and _normalized_customer_field(report_data.get("PhysicianSpecialty", ""))
        == _normalized_customer_field(WH_NO_STI_FACILITY)
    )
