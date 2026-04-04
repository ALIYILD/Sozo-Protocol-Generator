"""
Phase 8 — Evidence Ingestion Preparation
extract_evidence_seeds.py

Reads key_references from excel_knowledge_dump.json, parses them into
structured records, deduplicates by (author, year), queries PubMed eSearch
for PMIDs, and writes scripts/evidence_seeds.json.

Usage:
    python scripts/extract_evidence_seeds.py
"""

import json
import re
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
KNOWLEDGE_DUMP = SCRIPT_DIR / "excel_knowledge_dump.json"
OUTPUT_FILE = SCRIPT_DIR / "evidence_seeds.json"

# ---------------------------------------------------------------------------
# Step 1: Parse references
# ---------------------------------------------------------------------------

# Matches a 4-digit year (1900–2099) that is surrounded by a word boundary
YEAR_RE = re.compile(r"\b((?:19|20)\d{2})\b")
# Matches content inside the FIRST set of parentheses
PAREN_RE = re.compile(r"\(([^)]+)\)")


def parse_fragment(raw: str, condition: str, modality: str, evidence_level: str) -> dict | None:
    """Parse a single semicolon-delimited reference fragment into a structured dict.

    Returns None if no 4-digit year can be found (non-parseable fragment).
    """
    raw = raw.strip()
    if not raw:
        return None

    # Find year
    year_match = YEAR_RE.search(raw)
    if not year_match:
        return None
    year = year_match.group(1)
    year_start = year_match.start()

    # Author = everything before the year, stripped of trailing punctuation/spaces
    author_raw = raw[:year_start].strip().rstrip(",(- ")
    # Take only the first "word" cluster as the author surname
    # (handles "O'Reardon", "Blumberger", multi-word like "van den Heuvel")
    author = author_raw.strip() if author_raw else ""

    # Journal = text inside parentheses (first occurrence after the year)
    after_year = raw[year_match.end():]
    paren_match = PAREN_RE.search(after_year)
    journal = paren_match.group(1).strip() if paren_match else ""

    # Clean up journal — drop pure n= or citation metadata fragments
    # e.g. "Adv Sci, n=35, 230 citations" → keep full, callers can filter
    # Remove leading/trailing commas
    journal = journal.strip(", ")

    return {
        "author": author,
        "year": year,
        "journal": journal,
        "raw": raw,
        "condition": condition,
        "modality": modality,
        "evidence_level": evidence_level,
    }


def parse_all_references(data: dict) -> list[dict]:
    """Walk all protocols and parse every semicolon-delimited reference."""
    records = []
    for modality, protocols in data.get("protocols", {}).items():
        for proto in protocols:
            condition = proto.get("condition", "")
            evidence_level = proto.get("evidence_level", "")
            raw_refs = proto.get("key_references", "")
            if not raw_refs:
                continue
            fragments = [f.strip() for f in raw_refs.split(";") if f.strip()]
            for frag in fragments:
                parsed = parse_fragment(frag, condition, modality, evidence_level)
                if parsed:
                    records.append(parsed)
    return records


# ---------------------------------------------------------------------------
# Step 2: Deduplicate by (author, year)
# ---------------------------------------------------------------------------

def deduplicate(records: list[dict]) -> list[dict]:
    """Group records by (author, year); merge conditions/modalities/journals."""
    groups: dict[tuple, dict] = {}

    for rec in records:
        key = (rec["author"].lower(), rec["year"])
        if key not in groups:
            groups[key] = {
                "author": rec["author"],
                "year": rec["year"],
                "journal": rec["journal"],
                "raw": rec["raw"],
                "pmid": None,
                "pmid_error": None,
                "conditions": [],
                "modalities": [],
                "evidence_levels": [],
            }
        entry = groups[key]

        # Prefer a non-empty journal
        if not entry["journal"] and rec["journal"]:
            entry["journal"] = rec["journal"]

        # Collect conditions / modalities / evidence_levels (deduplicated)
        cond_label = f"{rec['condition']} — {rec['modality']}" if rec["modality"] else rec["condition"]
        if cond_label not in entry["conditions"]:
            entry["conditions"].append(cond_label)
        if rec["modality"] not in entry["modalities"]:
            entry["modalities"].append(rec["modality"])
        if rec["evidence_level"] and rec["evidence_level"] not in entry["evidence_levels"]:
            entry["evidence_levels"].append(rec["evidence_level"])

    return list(groups.values())


# ---------------------------------------------------------------------------
# Step 3: PubMed eSearch PMID lookup
# ---------------------------------------------------------------------------

ESEARCH_BASE = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    "?db=pubmed&retmax=1&retmode=json&term={query}"
)
RATE_SLEEP = 0.4  # seconds between requests (≤3 req/sec)


def build_query(author: str, year: str) -> str:
    """Build an eSearch query term for author + year."""
    # PubMed author search: last-name[au]
    # Use only the first token of the author string for robustness
    au_token = author.split()[0] if author.split() else author
    # URL-encode
    term = f"{au_token}[au] {year}[dp]"
    return urllib.parse.quote(term)


def fetch_pmid(author: str, year: str) -> tuple[str | None, str | None]:
    """Query PubMed eSearch. Returns (pmid_or_None, error_or_None)."""
    if not author or not year:
        return None, "missing author or year"
    url = ESEARCH_BASE.format(query=build_query(author, year))
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        id_list = payload.get("esearchresult", {}).get("idlist", [])
        if id_list:
            return id_list[0], None
        return None, None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return None, f"URLError: {e.reason}"
    except Exception as e:  # noqa: BLE001
        return None, f"Error: {e}"


def resolve_pmids(papers: list[dict]) -> list[dict]:
    """Mutate each paper dict in-place, adding pmid and pmid_error fields."""
    total = len(papers)
    for i, paper in enumerate(papers, 1):
        author = paper["author"]
        year = paper["year"]
        print(f"  [{i:>3}/{total}] Looking up: {author} {year} ...", end=" ", flush=True)
        pmid, err = fetch_pmid(author, year)
        paper["pmid"] = pmid
        paper["pmid_error"] = err
        if pmid:
            print(f"PMID={pmid}")
        elif err:
            print(f"null ({err})")
        else:
            print("null (not found)")
        time.sleep(RATE_SLEEP)
    return papers


# ---------------------------------------------------------------------------
# Step 4: Output JSON
# ---------------------------------------------------------------------------

def build_output(papers: list[dict], total_fragments: int) -> dict:
    pmids_found = sum(1 for p in papers if p.get("pmid"))
    return {
        "generated_at": date.today().isoformat(),
        "total_refs_parsed": total_fragments,
        "unique_papers": len(papers),
        "pmids_found": pmids_found,
        "papers": [
            {
                "author": p["author"],
                "year": p["year"],
                "journal": p["journal"],
                "raw": p["raw"],
                "pmid": p["pmid"],
                "pmid_error": p["pmid_error"],
                "conditions": p["conditions"],
                "modalities": p["modalities"],
                "evidence_levels": p["evidence_levels"],
            }
            for p in papers
        ],
    }


def print_summary(output: dict) -> None:
    n = output["unique_papers"]
    found = output["pmids_found"]
    pct = (found / n * 100) if n else 0
    print()
    print("Evidence Seeds Extraction Complete")
    print("===================================")
    print(f"Total reference fragments parsed: {output['total_refs_parsed']}")
    print(f"Unique papers identified:          {n}")
    print(f"PMIDs resolved:                    {found} / {n} ({pct:.1f}%)")
    print(f"Output: {OUTPUT_FILE}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print(f"Loading {KNOWLEDGE_DUMP} ...")
    with open(KNOWLEDGE_DUMP, encoding="utf-8") as fh:
        data = json.load(fh)

    print("Parsing references ...")
    records = parse_all_references(data)
    print(f"  {len(records)} fragments parsed across all modalities.")

    print("Deduplicating ...")
    papers = deduplicate(records)
    print(f"  {len(papers)} unique (author, year) pairs identified.")

    print("Querying PubMed eSearch for PMIDs ...")
    papers = resolve_pmids(papers)

    output = build_output(papers, len(records))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, ensure_ascii=False)

    print_summary(output)


if __name__ == "__main__":
    main()
