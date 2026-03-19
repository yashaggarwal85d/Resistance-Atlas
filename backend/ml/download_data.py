"""
Download BV-BRC AMR training data.
Called by: make download-data

Downloads genome metadata + AST phenotypes from BV-BRC public API.
Saves to data/raw/ relative to project root.

BV-BRC AMR data format:
  - genome_amr.tsv: genome_id, antibiotic, resistant_phenotype (S/R/I)
  - genome sequences downloadable via genome_id

Runtime: 10-30 minutes depending on connection. ~2GB total.
"""

import urllib.request
import urllib.error
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"

BV_BRC_AMR_URL = (
    "https://www.bv-brc.org/api/genome_amr/"
    "?http_accept=text/tsv"
    "&http_download=true"
    "&limit(100000)"
    "&in(antibiotic,(ampicillin,ciprofloxacin,gentamicin,"
    "tetracycline,trimethoprim,chloramphenicol,meropenem,colistin))"
    "&eq(resistant_phenotype,Resistant)"
    "&select(genome_id,genome_name,antibiotic,resistant_phenotype,laboratory_typing_method)"
)

BV_BRC_SUSCEPTIBLE_URL = (
    "https://www.bv-brc.org/api/genome_amr/"
    "?http_accept=text/tsv"
    "&http_download=true"
    "&limit(100000)"
    "&in(antibiotic,(ampicillin,ciprofloxacin,gentamicin,"
    "tetracycline,trimethoprim,chloramphenicol,meropenem,colistin))"
    "&eq(resistant_phenotype,Susceptible)"
    "&select(genome_id,genome_name,antibiotic,resistant_phenotype,laboratory_typing_method)"
)


def download_file(url: str, dest: Path, label: str) -> None:
    """Download a file with progress reporting."""
    print(f"  Downloading {label}...")
    try:
        with urllib.request.urlopen(url, timeout=120) as response:
            total = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 65536
            with open(dest, "wb") as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = int(downloaded / total * 100)
                        print(f"\r  {label}: {pct}%", end="", flush=True)
        print(f"\r  {label}: done ({downloaded / 1024 / 1024:.1f} MB)    ")
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"Could not download {label}: {e}\n"
            "BV-BRC may be temporarily unavailable. Try again later."
        )


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    resistant_path = DATA_DIR / "amr_resistant.tsv"
    susceptible_path = DATA_DIR / "amr_susceptible.tsv"

    print("ResistanceAtlas — BV-BRC data download")
    print("=" * 42)
    print(f"Saving to: {DATA_DIR}")
    print()

    download_file(BV_BRC_AMR_URL, resistant_path, "Resistant phenotypes")
    download_file(BV_BRC_SUSCEPTIBLE_URL, susceptible_path, "Susceptible phenotypes")

    r_lines = len(resistant_path.read_text().splitlines()) - 1
    s_lines = len(susceptible_path.read_text().splitlines()) - 1
    print()
    print(f"Downloaded {r_lines:,} resistant records")
    print(f"Downloaded {s_lines:,} susceptible records")
    print()
    print("Next step: run 'make train-model'")


if __name__ == "__main__":
    main()
