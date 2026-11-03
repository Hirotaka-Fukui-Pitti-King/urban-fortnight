# Research contribution and evidence rules

Before changing an academic paper, literature review, theory proof, or computational replication, read [the primary-source verification protocol](research/source_provenance/PROTOCOL.md) and update [the evidence registry](research/source_provenance/registry.json) for every new original-paper claim requiring verification.

**Do not claim original PDF access solely from a search hit, extracted PDF text, or a guessed/unavailable URL.** Preserve the access route, source version, any actual PDF bytes' SHA-256, visual page render evidence, equation identifier, and inspected implementation lines. If the PDF is unavailable, identify the source as *metadata only* or *indexed text only* and mark every affected equation/page claim *pending*. A reference landing page and a tested direct-download link are different artifacts.

Run the source audit and its deliberately failing counterexamples before any substantive research claim is promoted:

    python scripts/check_source_provenance.py
    python -m unittest discover -s scripts/tests -p test_source_provenance.py -v

The source gate is independent of Quarto/PDF typesetting checks and of Python equilibrium tests. Passing any one of these does not imply the others. If copyright prevents storing the original paper in this public repository, preserve the source in an authorized private location and refrain from claiming reproducible public visual verification unless reviewers can access the source.

**PR rule:** do not mark a source-based result as verified unless source provenance and the economics/calibration tests both pass. Keep unfixed doubts visible in the PR body and paper, and never invent rendered pages, original PDF checksums or successful URL status.
