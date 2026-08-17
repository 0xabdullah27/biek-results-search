# BIEK Results Search & PDF Gazette Tools

Search, extract, and bulk-check **BIEK (Board of Intermediate Education Karachi) results** — HSC Part I & Part II, Intermediate (FSc/FA/ICOM) Pre-Medical, Pre-Engineering, Science General, Humanities & Commerce. Includes a **result gazette PDF parser** (roll number + marks extraction), a **bulk result checker** by roll number, and CSV export — for the 2025 and 2026 annual results.

**Features:**
- 🔎 Check BIEK results online by roll number (name, father's name, marks, grade)
- 📄 Extract roll numbers & marks from official **result gazette PDFs** (Pre-Medical `3xxxxx`/`4xxxxx`, Pre-Engineering `8xxxxx`, Science General `7xxxxx`)
- ⚡ Bulk search thousands of rolls with parallel workers + CSV export
- 🏫 Supports all groups: Pre-Medical, Pre-Engineering, Science General, Humanities, Commerce
- 🗄️ Official BIEK result API integration (`api.pksol.com/search`)

**Current setup: Regular Part II 2026** (`reg-p2-a-2026`).

> 📋 **Read [`PROGRESS.md`](PROGRESS.md) first** — it records the project's current
> status, all API/gazette research findings, and open next steps, so you don't
> have to re-search anything.

## Current Status (August 2026)

- **Science Pre-Medical Part-II 2026** — declared **31-07-2026** ✔
- **Science Pre-Engineering Part-II 2026** — declared **17-08-2026** ✔
- **Science General Part-II 2026** — **not yet announced** (no gazette on the board site)
- **Humanities / Economics / Special candidates Part-II** — declared

### Roll number patterns for Part II 2026
| Group | Pattern | Source gazette | Rolls extracted |
|---|---|---|---|
| Pre-Medical (PM) | `3xxxxx` (300006–390783) | `pdfs/pm_part2.pdf` | 14,207 → `rollNumbers/pm_rolls.txt` |
| Pre-Engineering (SE) | `8xxxxx` (800001–898101) | `pdfs/se_part2.pdf` | 9,913 → `rollNumbers/se_rolls.txt` |
| Science General (SG) | not yet published | — | — |

> Note: Part I 2025 used different patterns (PM `4xxxxx`, SG `7xxxxx`). The gazette parser matches any 6-digit roll followed by marks in parentheses, so it works for all groups/years.

### API status (api.pksol.com)
The official result portal (`biekresult.pksol.com`) posts to `https://api.pksol.com/search`. The API's
`/parameters` endpoint currently lists **only 2025 exams** (`reg-p1-a-2025`, `pvt-p1-a-2025`, `reg-p2-a-2025`),
and searches return `No data found` even for previously-working 2025 queries — **2026 Part II data has not
been loaded into the API yet**.

The scripts are already configured for `reg-p2-a-2026` (same `reg-{part}-{a|s}-{year}` convention), so once
pksol loads the 2026 data, searching will work without further changes. Until then, run the scripts to verify
against a known roll (`--roll-numbers 312204 --faculty sm`) — expect `No data found`.

## Project Structure

```
├── scripts/                 # Core scripts (Part II 2026)
│   ├── biek_scraper.py      # Sequential search (single rolls, files, CSV export)
│   ├── bulk_search_all.py   # Fast parallel bulk search (workers)
│   └── extract_rolls_from_pdf.py  # Extract roll numbers from result PDFs
├── pdfs/                    # Part II result PDFs (add yours here)
├── rollNumbers/             # Roll number lists (one per line)
├── results/                 # Search output CSVs
└── archive/                 # Old/unused material
    ├── kpk/                 # KPK board search scripts (experimental, endpoints not working)
    └── part1/               # Part I 2025 data: PDFs, roll numbers, results, utilities
```

## Core Scripts

### `biek_scraper.py`
Main result search script that queries the BIEK API to fetch student results.

**Features:**
- Search individual or multiple roll numbers
- Support for all faculties (Pre-Medical, Pre-Engineering, Science General, Humanities, Commerce)
- Automatic cross-faculty search capability
- CSV export functionality
- Configurable request delays to avoid rate limiting

**Usage:**
```bash
# Search specific roll numbers (Part II 2026 by default)
python scripts/biek_scraper.py --roll-numbers 439581 439582 --faculty sm --output results/pm_results.csv

# Search from a file
python scripts/biek_scraper.py --file rollNumbers/pm_rolls.txt --faculty sm --output results/pm_results.csv

# Search across all faculties automatically
python scripts/biek_scraper.py --file rollNumbers/sg_rolls.txt --all-faculties --output results/sg_results.csv
```

**Faculty Codes:**
- `sm` - Pre-Medical (Science Medical)
- `se` - Pre-Engineering (Science Engineering)
- `sg` - Science General
- `hmt` - Humanities
- `com` - Commerce

**Exam Type Codes** (`--exam-type`, default `reg-p2-a-2026`):
- `reg-p2-a-2026` - Regular Part II 2026
- `pri-p2-a-2026` - Private Part II 2026

---

### `bulk_search_all.py`
High-performance bulk search script with parallel processing and faculty filtering.

**Features:**
- Concurrent searching with configurable worker threads (default: 10, up to 20+)
- Support for searching from roll number file or numeric range
- Faculty filtering option to search specific faculty or all faculties
- Progress tracking with real-time updates and ETA
- Saves results incrementally to CSV
- Much faster than sequential search (15-20x faster with 20 workers)

**Usage:**
```bash
# Search SG rolls in SG faculty only (recommended - fast & specific)
python scripts/bulk_search_all.py --file rollNumbers/sg_rolls.txt --faculty sg --output results/sg_results.csv --workers 20

# Search PM rolls in SM (Pre-Medical) faculty only
python scripts/bulk_search_all.py --file rollNumbers/pm_rolls.txt --faculty sm --output results/pm_results.csv --workers 20

# Search across ALL faculties (slower but comprehensive)
python scripts/bulk_search_all.py --file rollNumbers/sg_rolls.txt --output results/sg_all_faculties.csv --workers 20

# Search by range with specific faculty
python scripts/bulk_search_all.py --start 700000 --end 700100 --faculty sg --output results/test.csv --workers 5
```

**Available Faculty Codes:**
- `sg` - Science General (fastest for SG rolls: 1 API call per roll)
- `sm` - Pre-Medical (fastest for PM rolls: 1 API call per roll)
- `se` - Pre-Engineering
- `hmt` - Humanities
- `com` - Commerce
- **Without `--faculty` flag**: Searches all 5 faculties (slower: 5 API calls per roll)

---

### `extract_rolls_from_pdf.py`
Extracts roll numbers from BIEK result PDF files.

**Features:**
- Extracts 6-digit roll numbers from PDFs
- Supports both Pre-Medical (4xxxxx) and Science General (7xxxxx) patterns
- Processes single PDFs or entire folders
- Progress tracking for large files
- Automatic deduplication and sorting

**Usage:**
```bash
# Extract from single PDF
python scripts/extract_rolls_from_pdf.py --pdf pdfs/sg_part2.pdf --output rollNumbers/sg_rolls.txt

# Extract from all PDFs in folder
python scripts/extract_rolls_from_pdf.py --folder pdfs --output rollNumbers/all_rolls.txt
```

## Workflow

### 1. Add Part II PDFs
Place Part II result PDFs (e.g., `pdfs/pm_part2.pdf`, `pdfs/sg_part2.pdf`) in the `pdfs/` folder.

### 2. Extract Roll Numbers from PDFs
```bash
python scripts/extract_rolls_from_pdf.py --pdf pdfs/pm_part2.pdf --output rollNumbers/pm_rolls.txt
python scripts/extract_rolls_from_pdf.py --pdf pdfs/sg_part2.pdf --output rollNumbers/sg_rolls.txt
```

### 3. Search Results
```bash
# Fast bulk search with specific faculty (recommended)
python scripts/bulk_search_all.py --file rollNumbers/sg_rolls.txt --faculty sg --output results/sg_results.csv --workers 20

# Sequential search from a file
python scripts/biek_scraper.py --file rollNumbers/pm_rolls.txt --faculty sm --output results/pm_results.csv

# Test with small sample first
python scripts/bulk_search_all.py --start 700001 --end 700050 --faculty sg --output results/test.csv --workers 10
```

## Requirements

Install dependencies:
```bash
uv add PyPDF2 requests
```

Or using pip:
```bash
pip install PyPDF2 requests
```

Run scripts with uv:
```bash
uv run scripts/biek_scraper.py ...
```

## API Information

**Endpoint:** `https://api.pksol.com/search`

**Request Format:**
```json
{
  "faculty": "sm",
  "value": "reg-p2-a-2026",
  "roll_no": "439581",
  "matric_roll_no": "439581"
}
```

**Response Format:**
```json
{
  "detail": {
    "roll_no": 439581,
    "applicant_name": "NAILA",
    "father_name": "MUHAMMAD AKRAM",
    "secured_total": 364,
    "grade": "Pass"
  },
  "result": {
    "theory": [],
    "practical": []
  }
}
```

## Archive

- **`archive/kpk/`** - KPK board search scripts. Experimental; API endpoints are placeholders that need manual discovery and are not functional.
- **`archive/part1/`** - Part I 2025 material: result PDFs, roll number lists, result CSVs, and the `check_duplicates.py` / `find_missing.py` utilities that were specific to the Part I SG data.

## Notes

- **Exam Type Code:** `reg-p2-a-2026` follows the `reg-{part}-{a|s}-{year}` convention used by the official portal (`a` = annual, `s` = supply). The API's `/parameters` endpoint returns the live list of codes — check it with `curl https://api.pksol.com/parameters`.
- **Rate Limiting:** Use appropriate delays between requests (default: 0.5 seconds in `biek_scraper.py`, 0.05 in `bulk_search_all.py`).
- **Faculty Codes:** Always use correct codes (`sm` for Pre-Medical, not `pm`).
- **Roll Number Patterns (Part II 2026):**
  - Pre-Medical: 6 digits starting with 3 (e.g., 312204)
  - Pre-Engineering: 6 digits starting with 8 (e.g., 804713)
  - Science General: not yet published
- **Error Handling:** Scripts handle API errors, timeouts, and invalid responses gracefully.

---

## License

Educational use only. Respect BIEK's terms of service and avoid excessive API requests.
