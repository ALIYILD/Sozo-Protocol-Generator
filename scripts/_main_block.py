

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
ALL_CONDITIONS = [
    DEPRESSION, ANXIETY, ADHD, ALZHEIMERS,
    STROKE, TBI, CHRONIC_PAIN, PTSD, OCD,
    MS, ASD, LONG_COVID, TINNITUS, INSOMNIA,
]

if __name__ == "__main__":
    print("SOZO 6-Network Bedside Assessment — Partners Tier")
    print("=" * 55)
    errors = []
    for cond in ALL_CONDITIONS:
        slug = cond["slug"]
        short = cond["short"]
        print(f"\n[{short}] generating...")
        # Validate test counts
        for net, key, expected in [
            ("DMN","dmn_tests",7),("CEN","cen_tests",7),("SN","sn_tests",7),
            ("SMN","smn_tests",8),("Limbic","limbic_tests",7),("Attention","attn_tests",8),
        ]:
            actual = len(cond[key])
            if actual != expected:
                msg = f"  ⚠ {short} {net}: expected {expected} tests, got {actual}"
                print(msg); errors.append(msg)
        try:
            out = build_document(cond)
        except Exception as e:
            msg = f"  ✗ {short}: {e}"
            print(msg); errors.append(msg)

    print("\n" + "=" * 55)
    if errors:
        print(f"Completed with {len(errors)} warnings:")
        for e in errors: print(f"  {e}")
    else:
        print(f"All {len(ALL_CONDITIONS)} documents generated successfully.")
    print(f"\nOutput: {OUTPUT_BASE}")
