import shutil
from pathlib import Path

src = Path("outputs/documents/stroke_rehab/partners")
dst = Path("outputs/documents/stroke/partners")
dst.mkdir(parents=True, exist_ok=True)

pairs = [
    ("6Network_Bedside_Assessment_stroke_rehab.docx", "6Network_Bedside_Assessment_stroke.docx"),
    ("Clinical_Exam_Checklist_Partners_stroke_rehab.docx", "Clinical_Exam_Checklist_Partners_stroke.docx"),
    ("Clinical_Handbook_Partners_stroke_rehab.docx", "Clinical_Handbook_Partners_stroke.docx"),
]

for src_name, dst_name in pairs:
    shutil.copy2(src / src_name, dst / dst_name)
    size = (dst / dst_name).stat().st_size
    print(f"Copied {dst_name}  ({size:,} bytes)")

print("Done")
