#!/usr/bin/env python3
"""
SOZO Protocol Generator — Full Pipeline Runner

Generates all documents for all 15 conditions across both tiers,
using the template-driven approach OR the built-in document exporter.

Usage:
    PYTHONPATH=src python generate_all.py
    PYTHONPATH=src python generate_all.py --template path/to/template.docx
    PYTHONPATH=src python generate_all.py --conditions parkinsons,depression
    PYTHONPATH=src python generate_all.py --tier fellow
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))


def main():
    parser = argparse.ArgumentParser(description="SOZO Protocol Generator — Full Pipeline")
    parser.add_argument("--template", type=str, default=None, help="Path to Gold Standard DOCX template")
    parser.add_argument("--conditions", type=str, default=None, help="Comma-separated condition slugs (default: all)")
    parser.add_argument("--tier", type=str, default="both", choices=["fellow", "partners", "both"])
    parser.add_argument("--output-dir", type=str, default="outputs/documents/")
    parser.add_argument("--with-visuals", action="store_true", default=False)
    parser.add_argument("--with-qa", action="store_true", default=False)
    parser.add_argument("--with-manifests", action="store_true", default=False)
    args = parser.parse_args()

    from sozo_generator.conditions.registry import get_registry
    from sozo_generator.core.enums import Tier, DocumentType
    from sozo_generator.docx.exporter import DocumentExporter
    from sozo_generator.docx.renderer import DocumentRenderer

    registry = get_registry()
    all_slugs = registry.list_slugs()

    # Filter conditions
    if args.conditions:
        target_slugs = [s.strip() for s in args.conditions.split(",")]
        invalid = [s for s in target_slugs if s not in all_slugs]
        if invalid:
            print(f"WARNING: Unknown slugs: {', '.join(invalid)}")
        target_slugs = [s for s in target_slugs if s in all_slugs]
    else:
        target_slugs = all_slugs

    # Resolve tiers
    if args.tier == "both":
        tiers = [Tier.FELLOW, Tier.PARTNERS]
    else:
        tiers = [Tier(args.tier)]

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("SOZO Protocol Generator — Full Build")
    print("=" * 70)
    print(f"  Conditions:  {len(target_slugs)}")
    print(f"  Tiers:       {[t.value for t in tiers]}")
    print(f"  Output:      {output_dir}")
    print(f"  Template:    {args.template or '(built-in exporter)'}")
    print(f"  Visuals:     {args.with_visuals}")
    print(f"  QA:          {args.with_qa}")
    print("=" * 70)
    print()

    start_time = time.time()
    total_docs = 0
    total_errors = 0
    results = []

    if args.template:
        # ── Template-driven generation ──
        from sozo_generator.template.template_driven_generator import TemplateDrivenGenerator

        template_path = Path(args.template)
        if not template_path.exists():
            print(f"ERROR: Template not found: {template_path}")
            sys.exit(1)

        gen = TemplateDrivenGenerator(template_path)
        template_sections = gen.parse_template()
        print(f"Template parsed: {len(template_sections)} sections from {template_path.name}")
        print()

        renderer = DocumentRenderer(output_dir=str(output_dir))

        for i, slug in enumerate(target_slugs, 1):
            try:
                condition = registry.get(slug)
                condition_docs = 0

                for tier in tiers:
                    spec = gen.generate_for_condition(condition, tier)

                    # Build output path
                    cond_dir = output_dir / condition.slug.replace("_", " ").title().replace(" ", "_")
                    tier_dir = cond_dir / tier.value.capitalize()
                    tier_dir.mkdir(parents=True, exist_ok=True)
                    out_path = tier_dir / spec.output_filename

                    renderer.render(spec, out_path)
                    condition_docs += 1

                total_docs += condition_docs
                insufficient = sum(1 for s in spec.sections if s.is_placeholder)
                refs = len(spec.references)
                print(f"  [{i:2d}/{len(target_slugs)}] {condition.display_name:40s} | {condition_docs} docs | refs={refs} | insufficient={insufficient}")
                results.append((slug, condition_docs, 0, refs))

            except Exception as e:
                print(f"  [{i:2d}/{len(target_slugs)}] {slug:40s} | ERROR: {e}")
                total_errors += 1
                results.append((slug, 0, 1, 0))

    else:
        # ── Built-in document exporter ──
        for i, slug in enumerate(target_slugs, 1):
            try:
                condition = registry.get(slug)

                exporter = DocumentExporter(
                    output_dir=str(output_dir),
                    with_visuals=args.with_visuals,
                )
                outputs = exporter.export_condition(
                    condition=condition,
                    tiers=tiers,
                    doc_types=list(DocumentType),
                    with_visuals=args.with_visuals,
                )

                doc_count = len(outputs)
                total_docs += doc_count
                refs = len(condition.references) if condition.references else 0
                print(f"  [{i:2d}/{len(target_slugs)}] {condition.display_name:40s} | {doc_count:2d} docs | refs={refs}")
                results.append((slug, doc_count, 0, refs))

            except Exception as e:
                print(f"  [{i:2d}/{len(target_slugs)}] {slug:40s} | ERROR: {e}")
                total_errors += 1
                results.append((slug, 0, 1, 0))

    elapsed = time.time() - start_time

    # ── QA pass ──
    if args.with_qa:
        print()
        print("Running QA engine...")
        try:
            from sozo_generator.qa.engine import QAEngine
            engine = QAEngine()
            qa_total_blocks = 0
            qa_total_warnings = 0
            for slug in target_slugs:
                try:
                    condition = registry.get(slug)
                    report = engine.run_condition_qa(condition)
                    report.compute_counts()
                    status = "PASS" if report.passed else f"FAIL ({report.block_count} blocks)"
                    print(f"    {slug:20s} | {status} | {report.warning_count} warnings")
                    qa_total_blocks += report.block_count
                    qa_total_warnings += report.warning_count
                except Exception as e:
                    print(f"    {slug:20s} | QA ERROR: {e}")
            print(f"  QA Summary: {qa_total_blocks} blocks, {qa_total_warnings} warnings")
        except Exception as e:
            print(f"  QA engine error: {e}")

    # ── Manifest generation ──
    if args.with_manifests:
        print()
        print("Writing build manifests...")
        try:
            from sozo_generator.orchestration.versioning import ManifestWriter, create_build_id
            manifests_dir = Path("outputs/manifests/")
            writer = ManifestWriter(manifests_dir)
            for slug, doc_count, err_count, ref_count in results:
                if err_count > 0:
                    continue
                build_id = create_build_id(slug)
                # Collect output paths
                cond_dir = output_dir / slug.replace("_", " ").title().replace(" ", "_")
                doc_paths = {}
                for docx_file in cond_dir.rglob("*.docx"):
                    doc_paths[docx_file.stem] = docx_file
                if doc_paths:
                    manifest = writer.create_manifest(
                        build_id=build_id,
                        condition_slug=slug,
                        condition_name=slug.replace("_", " ").title(),
                        document_outputs=doc_paths,
                    )
                    writer.save_manifest(manifest)
            print(f"  Manifests written to {manifests_dir}")
        except Exception as e:
            print(f"  Manifest error: {e}")

    # ── Summary ──
    print()
    print("=" * 70)
    print(f"  Total documents:  {total_docs}")
    print(f"  Total errors:     {total_errors}")
    print(f"  Time:             {elapsed:.1f}s")
    print(f"  Output:           {output_dir}")
    print("=" * 70)

    if total_errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
