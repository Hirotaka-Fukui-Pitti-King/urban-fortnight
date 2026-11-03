# Mandatory original-source verification and citation protocol

Never equate a bibliographic entry, guessed or archived URL, PDF search-index text,
or citation from an earlier chat with the acquisition and visual inspection of an
original PDF.

The reproducibility ledger is registry.json. A claim has a required evidence tier:
metadata, indexed_text, pdf_bytes, pdf_pages_rendered, or equations_crosschecked.
The checker and its negative tests fail when a lower tier is labeled as verified.

A PDF may only be described as obtained if the original bytes are accessible,
are checked as a PDF, and have a reproducible SHA-256 and version identification.
The relevant pages must also be rendered and visually inspected before page
labels, equation signs, subscripts, tables, or detailed proof steps are called
verified. Every equation review records equation ID, page, inspection date and
responsible reviewer, with checksummed evidence available to the verification
environment. PDF typesetting validation and research-source validation are
two separate CI gates.

Do not put a proprietary/copyrighted source into a public repository without
permission. Use an authorized private source archive if needed; CI must report
that it cannot independently certify visual access unless the evidence bytes
are genuinely available to the CI job. Source URLs may expire. A DOI landing
page is NOT a working downloadable PDF URL. Failures are recorded, not hidden.

Current corrective action on 2026-11-03:
The Molico--Zhang 2005 manuscript has web-indexed PDF text, but binary
download and original page screenshot requests failed. The user's Wayback
URL was inaccessible. RePEc's publisher metadata is readable, but a linked
full PDF is not confirmed directly retrievable. Exact (1)-(14) equation and
page-number claims remain PENDING visual inspection. The Python pilot is a
provisional model adaptation, not visually verified source-faithful replication.
Foley (1994) and Gallegati et al. (2006) have no independently inspectable
source bytes or page-image hashes in this audit either.

Research output must distinguish source facts, text extracts, a proposed
model interpretation, and separately executed numerical tests. Even when
all provenance checks pass, human interpretation and actual economics
tests are still required. A code or PDF build passing is NOT evidence
of source fidelity.
