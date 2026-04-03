#!/usr/bin/env python3
"""
SOZO Protocol Generator — Window Conditions Document Generator

Generates FELLOW + PARTNERS protocol documents for all new Window conditions:
  Window 2: home_tdcs_mdd_anxiety
  Window 3: neuroonica_combo
  Window 4: tvns
  Window 5: ces_alphastem

Usage:
    PYTHONPATH=src python generate_window_conditions.py
    PYTHONPATH=src python generate_window_conditions.py --conditions neuroonica_combo,tvns
    PYTHONPATH=src python generate_window_conditions.py --tier fellow
    PYTHONPATH=src python generate_window_conditions.py --validate-only
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

WINDOW_SLUGS = [
    "home_tdcs_mdd_anxiety",   # Window 2
    "neuroonica_combo",         # Window 3
    "tvns",                     # Window 4
    "ces_alphastem",            # Window 5
]

WINDOW_META = {
    "home_tdcs_mdd_anxiety": {
        "window": 2,
        "display": "Home-Based tDCS — MDD + Comorbid Anxiety",
        "modality": "tDCS",
        "delivery": "home",
    },
    "neuroonica_combo": {
        "window": 3,
        "display": "Neuroonica tDCS + Neurofeedback Combination",
        "modality": "tDCS + NFB",
        "delivery": "clinic",
    },
    "tvns": {
        "window": 4,
        "display": "tVNS — Transcutaneous Vagus Nerve Stimulation",
        "modality": "tVNS",
        "delivery": "home + clinic",
    },
    "ces_alphastem": {
        "window": 5,
        "display": "Alpha-Stim CES — Anxiety, Insomnia & Comorbid Depression",
        "modality": "CES",
        "delivery": "home",
    },
}


def validate_conditions() -> dict[str, bool]:
    """Validate all window conditions load correctly from registry."""
    from sozo_generator.conditions.registry import get_registry
    registry = get_registry()
    results = {}
    for slug in WINDOW_SLUGS:
        try:
            schema = registry.get(slug)
            n_protocols = len(schema.protocols)
            n_phenotypes = len(schema.phenotypes)
            print(f"  [OK] {slug}: {n_protocols} protocols, {n_phenotypes} phenotypes")
            results[slug] = True
        except Exception as e:
            print(f"  [FAIL] {slug}: {e}")
            results[slug] = False
    return results


def generate_documents(
    slugs: list[str],
    tiers: list,
    output_dir: Path,
) -> dict[str, list[Path]]:
    """Generate DOCX documents for all specified window conditions and tiers."""
    from sozo_generator.conditions.registry import get_registry
    from sozo_generator.core.enums import Tier, DocumentType
    from sozo_generator.docx.exporter import DocumentExporter

    registry = get_registry()
    generated: dict[str, list[Path]] = {}

    for slug in slugs:
        generated[slug] = []
        meta = WINDOW_META.get(slug, {})
        window_num = meta.get("window", "?")
        print(f"\n{'='*60}")
        print(f"Window {window_num}: {meta.get('display', slug)}")
        print(f"  Modality: {meta.get('modality', '?')} | Delivery: {meta.get('delivery', '?')}")
        print(f"{'='*60}")

        try:
            schema = registry.get(slug)
        except Exception as e:
            print(f"  ERROR loading schema: {e}")
            continue

        slug_dir = output_dir / slug
        slug_dir.mkdir(parents=True, exist_ok=True)

        exporter = DocumentExporter(schema)

        for tier in tiers:
            tier_dir = slug_dir / tier.value
            tier_dir.mkdir(parents=True, exist_ok=True)

            doc_types = [
                DocumentType.EVIDENCE_BASED_PROTOCOL,
                DocumentType.CLINICAL_EXAM,
                DocumentType.PHENOTYPE_CLASSIFICATION,
                DocumentType.RESPONDER_TRACKING,
            ]

            for doc_type in doc_types:
                try:
                    filename = f"{tier.value.upper()}_{doc_type.value.upper()}_{slug.upper()}.docx"
                    filepath = tier_dir / filename
                    doc = exporter.export(doc_type=doc_type, tier=tier)
                    doc.save(str(filepath))
                    print(f"  [OK] {filename}")
                    generated[slug].append(filepath)
                except Exception as e:
                    print(f"  [SKIP] {doc_type.value} / {tier.value}: {e}")

    return generated


def print_summary(generated: dict[str, list[Path]], output_dir: Path) -> None:
    """Print generation summary."""
    total = sum(len(v) for v in generated.values())
    print(f"\n{'='*60}")
    print(f"GENERATION COMPLETE — {total} documents")
    print(f"Output: {output_dir.resolve()}")
    print(f"{'='*60}")
    for slug, files in generated.items():
        meta = WINDOW_META.get(slug, {})
        print(f"  Window {meta.get('window','?')}: {slug} — {len(files)} docs")


def main():
    parser = argparse.ArgumentParser(
        description="SOZO Window Conditions Document Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_window_conditions.py
  python generate_window_conditions.py --conditions neuroonica_combo
  python generate_window_conditions.py --tier fellow
  python generate_window_conditions.py --validate-only
        """,
    )
    parser.add_argument(
        "--conditions",
        type=str,
        default=None,
        help=f"Comma-separated slugs (default: all). Options: {', '.join(WINDOW_SLUGS)}",
    )
    parser.add_argument(
        "--tier",
        type=str,
        default="both",
        choices=["fellow", "partners", "both"],
        help="Document tier to generate (default: both)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs/documents/",
        help="Output directory (default: outputs/documents/)",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        default=False,
        help="Only validate schemas load — do not generate documents",
    )
    args = parser.parse_args()

    print("\nSOZO Window Conditions Generator")
    print("=" * 60)
    print("Validating condition schemas...")
    results = validate_conditions()

    if args.validate_only:
        ok = sum(results.values())
        print(f"\nValidation: {ok}/{len(results)} passed")
        sys.exit(0 if ok == len(results) else 1)

    failed = [s for s, ok in results.items() if not ok]
    if failed:
        print(f"\nWARNING: {len(failed)} conditions failed validation: {', '.join(failed)}")
        print("Proceeding with valid conditions only.")

    # Resolve target slugs
    if args.conditions:
        target_slugs = [s.strip() for s in args.conditions.split(",")]
        unknown = [s for s in target_slugs if s not in WINDOW_SLUGS]
        if unknown:
            print(f"WARNING: Unknown slugs: {', '.join(unknown)}")
        target_slugs = [s for s in target_slugs if s in WINDOW_SLUGS and results.get(s, False)]
    else:
        target_slugs = [s for s in WINDOW_SLUGS if results.get(s, False)]

    if not target_slugs:
        print("No valid conditions to generate. Exiting.")
        sys.exit(1)

    # Resolve tiers
    from sozo_generator.core.enums import Tier
    if args.tier == "both":
        tiers = [Tier.FELLOW, Tier.PARTNERS]
    else:
        tiers = [Tier(args.tier)]

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nGenerating {len(target_slugs)} conditions × {len(tiers)} tier(s)...")
    t0 = time.time()
    generated = generate_documents(target_slugs, tiers, output_dir)
    elapsed = time.time() - t0

    print_summary(generated, output_dir)
    print(f"Time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
