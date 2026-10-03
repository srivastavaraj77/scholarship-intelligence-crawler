"""
CLI utility to export database scholarship records to JSON or CSV.
"""
import sys
import json
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import export_all_json, export_all_csv


def main():
    parser = argparse.ArgumentParser(description="Export Scholarship Intelligence Data")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Export format")
    parser.add_argument("--output", default=None, help="Output file path")
    args = parser.parse_args()

    if args.format == "json":
        data = export_all_json()
        out_path = args.output or "scholarships_export.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Exported {len(data)} scholarship records to {out_path}")
    else:
        csv_str = export_all_csv()
        out_path = args.output or "scholarships_export.csv"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(csv_str)
        print(f"✅ Exported scholarship records to {out_path}")


if __name__ == "__main__":
    main()
