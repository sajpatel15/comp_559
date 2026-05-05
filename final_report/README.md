# RouteDoodle Final Report

This folder contains the final report source, figures, references, and compiled PDF.

## Files

- `report.tex`: LaTeX source.
- `references.bib`: bibliography.
- `neurips_2020.sty`: LaTeX style file used by the report.
- `report.pdf`: compiled final report.
- `figures/pipeline.png`: system pipeline figure.
- `figures/app_both_row_long.png`: live app comparison screenshot used in the report.

## Build

From this folder:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error report.tex
```

Render pages for visual checks:

```bash
gs -q -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pngalpha -r120 -sOutputFile=rendered/page-%02d.png report.pdf
```

The report uses live app screenshots from `http://127.0.0.1:8765/` and notebook evidence from `../routedoodle_gnn_v2.ipynb`.
