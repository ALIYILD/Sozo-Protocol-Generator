"""
Phase 8 — Evidence Ingestion
fetch_pubmed_abstracts.py

Reads evidence_seeds.json (produced by extract_evidence_seeds.py) and for
each entry that has a PMID, fetches the full abstract via PubMed eFetch,
parses the XML, and saves the results to scripts/pubmed_abstracts.json.

Run SEPARATELY (longer network operation — ~0.4 s per PMID):
    python scripts/fetch_pubmed_abstracts.py

Output: scripts/pubmed_abstracts.json
"""

import json
import time
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
SEEDS_FILE = SCRIPT_DIR / "evidence_seeds.json"
OUTPUT_FILE = SCRIPT_DIR / "pubmed_abstracts.json"

# ---------------------------------------------------------------------------
# PubMed eFetch
# ---------------------------------------------------------------------------
EFETCH_URL = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    "?db=pubmed&rettype=abstract&retmode=xml&id={pmid}"
)
RATE_SLEEP = 0.4  # seconds between requests


def fetch_xml(pmid: str) -> str | None:
    """Fetch PubMed XML for a single PMID. Returns raw XML string or None."""
    url = EFETCH_URL.format(pmid=pmid)
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        print(f"    HTTP {e.code} for PMID {pmid}")
    except urllib.error.URLError as e:
        print(f"    URLError for PMID {pmid}: {e.reason}")
    except Exception as e:  # noqa: BLE001
        print(f"    Error fetching PMID {pmid}: {e}")
    return None


def parse_pubmed_xml(xml_text: str) -> dict:
    """Parse a PubMed eFetch XML response into a structured dict."""
    result = {
        "title": "",
        "abstract": "",
        "authors": [],
        "journal": "",
        "pub_year": "",
    }
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        result["parse_error"] = str(e)
        return result

    article = root.find(".//PubmedArticle/MedlineCitation/Article")
    if article is None:
        return result

    # Title
    title_el = article.find("ArticleTitle")
    if title_el is not None:
        # ET itertext handles nested formatting tags (e.g. <i>, <sup>)
        result["title"] = "".join(title_el.itertext()).strip()

    # Abstract — may be structured (multiple AbstractText with Label)
    abstract_parts = []
    for ab in article.findall(".//AbstractText"):
        label = ab.get("Label")
        text = "".join(ab.itertext()).strip()
        if label:
            abstract_parts.append(f"{label}: {text}")
        else:
            abstract_parts.append(text)
    result["abstract"] = "\n".join(abstract_parts)

    # Authors
    authors = []
    for author_el in article.findall(".//AuthorList/Author"):
        last = author_el.findtext("LastName", "")
        fore = author_el.findtext("ForeName", "")
        name = f"{last} {fore}".strip()
        if name:
            authors.append(name)
    result["authors"] = authors

    # Journal
    journal_el = article.find(".//Journal/Title")
    if journal_el is not None:
        result["journal"] = journal_el.text or ""
    else:
        # Fallback: ISOAbbreviation
        iso_el = article.find(".//Journal/ISOAbbreviation")
        if iso_el is not None:
            result["journal"] = iso_el.text or ""

    # Publication year
    year_el = article.find(".//Journal/JournalIssue/PubDate/Year")
    if year_el is not None:
        result["pub_year"] = year_el.text or ""
    else:
        # MedlineDate fallback  e.g. "2018 Jan-Feb"
        medline_el = article.find(".//Journal/JournalIssue/PubDate/MedlineDate")
        if medline_el is not None and medline_el.text:
            result["pub_year"] = medline_el.text[:4]

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not SEEDS_FILE.exists():
        raise FileNotFoundError(
            f"{SEEDS_FILE} not found. Run extract_evidence_seeds.py first."
        )

    print(f"Loading {SEEDS_FILE} ...")
    with open(SEEDS_FILE, encoding="utf-8") as fh:
        seeds = json.load(fh)

    papers = seeds.get("papers", [])
    pmid_papers = [(p["pmid"], p) for p in papers if p.get("pmid")]
    print(f"Found {len(pmid_papers)} papers with PMIDs (of {len(papers)} total).")

    # Load existing output if present (allows resuming)
    abstracts: dict = {}
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, encoding="utf-8") as fh:
            abstracts = json.load(fh)
        print(f"Resuming: {len(abstracts)} abstracts already cached.")

    total = len(pmid_papers)
    fetched = 0
    for i, (pmid, paper) in enumerate(pmid_papers, 1):
        if pmid in abstracts:
            print(f"  [{i:>3}/{total}] PMID {pmid} — already cached, skipping.")
            continue

        print(f"  [{i:>3}/{total}] Fetching PMID {pmid} ({paper['author']} {paper['year']}) ...",
              end=" ", flush=True)
        xml_text = fetch_xml(pmid)
        if xml_text:
            parsed = parse_pubmed_xml(xml_text)
            abstracts[pmid] = parsed
            fetched += 1
            print(f"OK — \"{parsed['title'][:60]}...\"" if len(parsed["title"]) > 60
                  else f"OK — \"{parsed['title']}\"")
        else:
            abstracts[pmid] = {"error": "fetch_failed"}
            print("FAILED")

        time.sleep(RATE_SLEEP)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        json.dump(abstracts, fh, indent=2, ensure_ascii=False)

    print()
    print("PubMed Abstract Fetch Complete")
    print("==============================")
    print(f"Newly fetched: {fetched}")
    print(f"Total cached:  {len(abstracts)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
