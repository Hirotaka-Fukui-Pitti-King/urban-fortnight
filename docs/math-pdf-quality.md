# Mathematics quality gate for Quarto/Typst papers

Use a pair of standalone double-dollar lines for display mathematics. Inline mathematics uses paired single dollars on one line. Do not use a single standalone dollar line: Quarto/Pandoc will treat that as literal text even if Typst generates a PDF without error.

The CI has independent gates. Before rendering it parses every QMD with Pandoc AST, checks dollar delimiters, balanced math braces, no raw math TeX outside Math nodes, and compares inline/display math-node counts to the version-controlled paper/math-quality-manifest.json. Every newly added QMD must be added to the manifest. An intentional equation insertion/deletion requires a manifest change that reviewers can see.

After Quarto renders the PDFs, the gate extracts PDF text and requires (for the mathematical paper) an embedded math font, key mathematical symbols, minimum page and extracted-text counts, and no literal dollars or raw LaTeX commands. It also renders up to four math-rich pages to PNG and uploads them as a review artifact. This catches regression in rendering, but automated checks cannot guarantee aesthetic perfection. Inspect those pages before circulating a PDF.

Run locally from the repository root after installing Pandoc, Quarto, Poppler (pdftotext/pdfinfo/pdffonts/pdftoppm):
1. python -m unittest discover -s scripts/tests -p test_math_quality.py -v
2. python scripts/check_paper_math.py --source-check
3. quarto render paper/article.qmd --to academic-typst
4. quarto render slides/research-agenda.qmd --to clean-typst
5. python scripts/check_paper_math.py --pdf-check --preview-dir math-previews

The test suite deliberately corrupts dollar fences, braces, inline formulas, unparsed TeX and PDF math fonts, confirming that failures are rejected. Generated math-previews are for visual review, not a claim of automatic visual-proof correctness.

Never treat a successful compile alone as a successful mathematical PDF.
