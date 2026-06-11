# LaTeX Generation → Overleaf

Deliverable is `.tex`, compiled on **Overleaf** (https://www.overleaf.com) → PDF. Templates in [templates/](../templates/) are self-contained (standard classes: `article`-based resume/CV, `moderncv` cover letter) so they compile on Overleaf with no custom `.cls` upload. Geometry is `textwidth=7.5in`, matching the char-budget tables below.

## Overleaf workflow
1. Generate the `.tex` into `output/<Company_Role>/`.
2. Tell the user: create a new Overleaf project → upload the `.tex` (and any `.bib`) → set compiler to **pdfLaTeX** → Recompile. Or run locally: `pdflatex -interaction=nonstopmode file.tex` (twice, for `\pageref{LastPage}`).
3. If `mhchem`/`fontawesome`/`moderncv` are missing locally, Overleaf has them preinstalled — prefer Overleaf.
4. Optionally compile locally to view the PDF for orphan/page-fill checks before handing off.

## Character limits (rendered chars — strip `\textbf{}`, `\textit{}`, `\ce{}`, `$..$` first; use `scripts/char_count.py`)

**Resume (10pt, textwidth 7.5in)**

| Variant | Target | HARD MAX | Orphan (last line ≥) | ~Words |
|---|---|---|---|---|
| 1L | 105–111 | 117 | — | ~13 |
| 2L | 189–205 | 218 | 78 | ~23–25 |

**CV (11pt, textwidth 7.5in)**

| Variant | Target | HARD MAX | Orphan (last line ≥) | ~Words |
|---|---|---|---|---|
| 1L | 88–93 | 101 | — | — |
| 2L | 168–182 | 190 | 65 | ~21–22 |
| 3L | 250–268 | 280 | 65 | ~31–32 |

**Aim for the target middle (≈200 for a 2L resume bullet), not the hard max.**

## The four discipline rules
1. **Bold-width penalty.** Bold renders wider. Resume effective limit/line = `119 − 0.5×bold_chars`; CV = `91 − 0.25×bold_chars`. 10 bold chars ≈ lose ~4 chars of capacity. Bold only 6–8 of the most JD-relevant terms per skills section.
2. **Orphan rule.** A multi-line bullet's last rendered line must fill ≥70% width (resume 2L ≥78, CV 2L/3L ≥65). A 3-word dangling last line looks broken — pad the content or tighten to one fewer line.
3. **Em-dash budget.** Max 2 `---` per document (see [ai-fingerprint.md](ai-fingerprint.md)). `~` in LaTeX is a non-breaking space — use `$\sim$` for "approximately."
4. **FIXED sections — never modify.** Education, internships, publications, honors/awards, the header block, and all `\vspace`/`\geometry`/class formatting are FIXED. Only generate into: Summary, Technical Skills, and Experience bullets/headers. Changing FIXED layout breaks the calibrated page budget.

## Page-fill budget
After filling FIXED content, compile and count rendered lines per page; remaining lines = your variable-bullet budget. Resume ≈ 20 variable bullets (all 2L). CV ≈ 19–21 bullets / ~45 rendered lines (2L/3L mix). **CV page-1 rule:** the first bullet of the first experience MUST be 2L — a 3L first bullet overflows page 1.

## LaTeX notation quick-ref
| Item | Correct | Wrong | Renders |
|---|---|---|---|
| Chemical formula | `\ce{H2O}` | `H2O`, `H$_2$O` | H₂O |
| Superscript | `R$^2$=0.99` | `R^2`, `R2` | R² |
| Greek | `$\alpha$-phase` | `alpha-phase` | α-phase |
| Approximately | `$\sim$64` | `~64` (non-breaking space!) | ~64 |
| Degrees | `$^\circ$C` | `^oC` | °C |

## Count before you compile
```bash
python3 scripts/char_count.py -f resume "\\textbf{DFT} analysis of \\ce{TiO2} surfaces"
python3 scripts/char_count.py -f cv output/Company_Role/file.tex   # all \item lines + total line count
```
Strips markup, reports rendered chars + variant + SHORT/OK/NEAR-MAX/OVER + bold/em-dash penalties.
