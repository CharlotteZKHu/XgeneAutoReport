# Report Generator — Sub-1 Result Display Option

## What changed

A new checkbox is available on the Report Generation / Batch Configuration page:

**Round positive results below 1 up to 1 (minimum detected value = 1)**

The checkbox is **enabled by default**.

### When checked
Only numeric lab-result fields in the open interval `0 < value < 1` are displayed as `1` in generated reports.

Examples:
- `0` -> `0`
- `0.02` -> `1`
- `0.5` -> `1`
- `0.99` -> `1`
- `1` -> `1`
- `1.2` -> `1.2`

### When unchecked
Numeric lab results are displayed using their original values.

## Important behavior

- The source Excel data is not modified.
- Patient/demographic/date/text fields are not rounded.
- Non-numeric result strings such as `Detected`, `Pending`, etc. are unchanged.
- The rule is applied at report-rendering time only.
- The existing unified WH template routing remains supported.
- The existing Dena Geiger + Glacier Womens Health and Wellness STI/HSV hiding rule remains supported.

## Files to replace

Replace these files in the project root:
- `gui_app.py`
- `report_compiler.py`
- `config.py`
- `main.py`

The included `data_handler.py` is unchanged and is included for convenience/consistency.

Place:
- `templates/WH_template.tex`

inside the project's `templates/` folder.

## Command-line behavior

`main.py` has no GUI checkbox, so command-line report generation uses the new behavior by default (`0 < result < 1` -> `1`), matching the GUI's default checked state.
