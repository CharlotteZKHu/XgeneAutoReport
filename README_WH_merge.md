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


## Customer-specific STI suppression (Glacier Womens Health and Wellness)

When BOTH demographics fields match (ignoring case and extra whitespace):

- Excel `Physician` -> `PhysicianName`: `Dena Geiger`
- Excel `FACILITIES` -> `PhysicianSpecialty`: `Glacier Womens Health and Wellness`

The unified WH report hides **all printed STI-related report sections**:

- the `STIs` row in TEST SUMMARY, including its detected/not detected/not tested status;
- the `STIs` category, all its organisms (including optional variant 3/4 rows), their results and descriptions;
- the `Virus (STI related)` category with HSV-1/HSV-2 and their results and descriptions.

The BV, AV, Group B strep, Candida, Vaginal flora, Test Control, all other summary rows, and original variant 1–4 Candida/expanded-STI behavior remain unchanged for other customers. Crosswalk and input Excel need no extra columns/changes. This affects PDF presentation only: lab-result data and injected LaTeX values remain intact; there is **no assertion that a hidden test was not performed or was negative**. The log notes when a WH report applies the rule. The compiler errors if the WH visibility marker is missing rather than risk emitting an unfiltered WH report.

If the actual Excel spelling differs (for example, `Women's` versus `Womens` or `Dr. Dena Geiger` versus `Dena Geiger`), update the match constants in `config.py` after confirming the source data. Non-WH report templates are not changed. Verify the reporting scope and revised PDF with the laboratory's authorized clinical reviewer before distribution.

**Regression test:** Four WH variants × designated/ordinary customer = eight PDF compilations passed with representative positive STI and HSV lab values, plus a check that nonmatching physician/facility combinations are not suppressed. PDF text was checked for absence/presence of category names, organism rows, and preservation of non-STI sections and Candida variant behavior. Temporary placeholder images were used instead of the lab's real assets.
