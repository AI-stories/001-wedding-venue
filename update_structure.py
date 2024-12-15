import shutil
from pathlib import Path

PATH = "data/raw/Southern California Wedding Venues"
OUTPUT_PATH = "venues"

Path(OUTPUT_PATH).mkdir(exist_ok=True)

pdf_files = Path(PATH).glob("*.pdf")
for pdf_path in pdf_files:
    print(pdf_path)
    pdf_name = pdf_path.stem

    venue_dir = Path(OUTPUT_PATH) / pdf_name
    venue_dir.mkdir(exist_ok=True)

    dest_path = venue_dir / pdf_path.name
    shutil.copy2(pdf_path, dest_path)
