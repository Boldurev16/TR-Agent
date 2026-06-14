from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
source_folder = project_root / "docs-inbox"
target_folder = project_root / "docs-batches"
batch_size = 100

print("PDF batch maker")
print(f"Source folder: {source_folder}")
print(f"Target folder: {target_folder}")
print(f"Batch size: {batch_size}")

pdf_files = sorted(
    source_folder.glob("*.pdf"),
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)

print(f"PDF files found: {len(pdf_files)}")

if not pdf_files:
    print("No PDF files found. Put PDF files into docs-inbox first.")
    raise SystemExit

for index, pdf_file in enumerate(pdf_files):
    batch_number = index // batch_size + 1
    batch_folder = target_folder / f"batch-{batch_number:04d}"
    batch_folder.mkdir(parents=True, exist_ok=True)

    destination = batch_folder / pdf_file.name

    if destination.exists():
        print(f"Skipping existing file: {destination}")
        continue

    print(f"Copying {pdf_file} -> {destination}")
    destination.write_bytes(pdf_file.read_bytes())