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
