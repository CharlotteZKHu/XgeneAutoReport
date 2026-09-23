# Unified WH template (legacy WH templates 1–4)

All four uploaded `.tex` files differ only in whether two STI rows and two Candida rows appear in the TEST RESULTS table. All other source lines match.

| Crosswalk `Result Template` | Extra STI rows | Extra Candida rows |
| --- | --- | --- |
| `WH template 1` | none | none |
| `WH template 2` | none | Candida auris, Candida tropicalis |
| `WH template 3` | Haemophilus ducreyi, Treponema pallidum | none |
| `WH template 4` | Haemophilus ducreyi, Treponema pallidum | Candida auris, Candida tropicalis |

## Installation

1. Back up your project.
2. Copy `WH_template.tex` into the existing `templates/` directory. (It is the sole WH template needed.)
3. Replace your project-root `config.py`, `report_compiler.py`, `main.py`, `gui_app.py` with the supplied versions. Other panels and their templates do not need changes.
4. Leave your Excel Crosswalk unchanged. Its existing `WH template 1` through `WH template 4` names resolve automatically to `WH_template.tex` while preserving the original row combinations. `WH_template` selects variant 1 by default. Names with underscore/hyphen/space separators are also accepted.
5. Once you have validated output for all four variants in your local environment, archive the old `WH template 1.tex` through `WH template 4.tex` rather than keeping them as active templates.

**Note:** The `.tex` file by itself defaults to variant 1 when directly compiled. The updated Python compiler inserts the requested variant for Crosswalk-driven report generation. It continues generating named `.tex` and `.pdf` outputs as before.

**Validation:** Compiled all four merged variants using the sample patient data and temporary stand-in images. PDF text extracted from each merged report matched the corresponding original template exactly, and all four variants passed an end-to-end call to `compile_single_report`. The original images (CLIA/CAP icons and signatures) were not uploaded, so confirm final visual fidelity in your environment with your real `assets/` directory. No report interpretation rules, result values, medical text, or visual layout outside the two optional row groups were changed.
