"""Split 'Build your Technology Radar' sheet into 20-row XLSX batches by quadrant."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE = PROJECT_ROOT / "docs-inbox" / "Источник данных тех. радар.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "docs-inbox" / "tech-radar-batches"
SHEET = "Build your Technology Radar"
CHUNK_SIZE = 20

QUADRANTS = [
    "Технологии искусственного интеллекта",
    "Технологии цифровых двойников",
    "Технологии машинного зрения",
    "Технологии IoT и интернет вещей",
    "Технологии роботизации и полифункциональных роботов",
    "Технологии квантовых коммуникаций и гибридные квантовые вычисления",
    "Технологии блокчейн",
    "Технологии энергоэффективности и устойчивого развития",
    "Технологии импортозамещения и реновация",
    "Технологии новых материалов и химическая технология",
    "Технологии новых решений на основе палладия",
    "Технологии интеллектуальных систем управления производством",
    "Технологии промышленной автоматизации",
    "Технологии системы логистики",
    "Технологии кибербезопасности",
    "Технологии интеграционных решений и хранения данных",
    "Технологии AR\\VR для металлургии",
    "Технологии на основе больших яхыковых моделей",
    "Технологии систем на базе LLM RAG",
    "Технологии систем на базе агентной LLM",
    "Батарейные технологии",
    "Аддитивные технологии (3D-печать)",
    "Промышленная безопасность (цифровая)",
    "Биотехнологии",
]


def safe_filename(name: str) -> str:
    cleaned = name.replace("\\", "-").replace("/", "-")
    cleaned = re.sub(r'[<>:"|?*]', "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def main() -> None:
    df = pd.read_excel(SOURCE, sheet_name=SHEET)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    summary: list[tuple[str, int, int]] = []

    for quadrant in QUADRANTS:
        subset = df[df["quadrant"] == quadrant].reset_index(drop=True)
        row_count = len(subset)
        if row_count == 0:
            summary.append((quadrant, 0, 0))
            continue

        prefix = safe_filename(quadrant)
        file_count = 0

        for start in range(0, row_count, CHUNK_SIZE):
            chunk = subset.iloc[start : start + CHUNK_SIZE]
            file_count += 1
            out_name = f"{prefix}_{file_count:03d}.xlsx"
            out_path = OUTPUT_DIR / out_name
            chunk.to_excel(out_path, index=False, sheet_name=SHEET)

        summary.append((quadrant, row_count, file_count))

    print(f"Output: {OUTPUT_DIR}\n")
    print(f"{'Quadrant':<70} {'Rows':>6} {'Files':>6}")
    print("-" * 84)
    total_files = 0
    for quadrant, rows, files in summary:
        print(f"{quadrant:<70} {rows:>6} {files:>6}")
        total_files += files
    print("-" * 84)
    print(f"{'TOTAL':<70} {len(df):>6} {total_files:>6}")


if __name__ == "__main__":
    main()
