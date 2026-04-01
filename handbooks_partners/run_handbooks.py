"""Run Partners Tier handbook generation for all 14 conditions."""
import sys
sys.path.insert(0, '.')
from handbooks_partners.base_generator import build_handbook
from handbooks_partners.cdata_1 import CDATA as C1
from handbooks_partners.cdata_2 import CDATA as C2
from handbooks_partners.cdata_3 import CDATA as C3

ALL_CONDITIONS = {**C1, **C2, **C3}

if __name__ == "__main__":
    for slug, cdata in ALL_CONDITIONS.items():
        print(f"Building: {slug}")
        build_handbook(cdata)
    print(f"\nAll {len(ALL_CONDITIONS)} Partners handbooks generated.")
