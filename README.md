# BIEK Results Search & PDF Gazette Tools

Search, extract, and bulk-check **BIEK (Board of Intermediate Education Karachi) results** — HSC Part I & Part II, Intermediate (FSc/FA/ICOM) Pre-Medical, Pre-Engineering, Science General, Humanities & Commerce. Includes a **result gazette PDF parser** (roll number + marks extraction), a **bulk result checker** by roll number, and CSV export — for the 2025 and 2026 annual results.

**Features:**
- 🔎 Check BIEK results online by roll number (name, father's name, marks, grade)
- 📄 Extract roll numbers & marks from official **result gazette PDFs** (Pre-Medical `3xxxxx`, Pre-Engineering `8xxxxx`, Science General `6xxxxx`)
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
- **Science General Part-II 2026** — declared **27-08-2026** ✔
- **Humanities / Economics / Special candidates Part-II** — declared

### Roll number patterns for Part II 2026
| Group | Pattern | Source gazette | Rolls extracted |
|---|---|---|---|
| Pre-Medical (PM) | `3xxxxx` (300006–390783) | `pdfs/pm_part2.pdf` | 14,207 → `rollNumbers/pm_rolls.txt` |
| Pre-Engineering (SE) | `8xxxxx` (800001–898101) | `pdfs/se_part2.pdf` | 9,913 → `rollNumbers/se_rolls.txt` |
| Science General (SG) | `6xxxxx` (600001–699999) | `pdfs/sg_part2.pdf` | → `rollNumbers/sg_rolls.txt` |

> Note: Part I 2025 used different patterns (PM `4xxxxx`, SG `7xxxxx`). The gazette parser matches any 6-digit roll followed by marks in parentheses, so it works for all groups/years.

### API status (api.pksol.com)
The official result portal (`biekresult.pksol.com`) and the BIEK mobile app (`com.biek.edu.app`) both
use PKSOL's API. The API has recently changed its field format and is currently in a **transitional/broken state**:

| Field | Old format | New format |
|---|---|---|
| Exam code | `exam_code: "reg-p2-a-2026"` | `value: "reg-p2-a-2026"` |
| Faculty | *(not required)* | `faculty: "sg"` |

**Current issues (August 2026):**
- The `/parameters` endpoint only lists old 2025 exam codes
- The new format (`value`+`faculty`) accepts requests but returns `No data found`
- The old format (`exam_code`) throws a 500 error (`Undefined array key "faculty"`)
- The website dropdown only shows 2025 Supply options
- **However, the BIEK mobile app works** — it uses the same `value`+`faculty` format and has 2026 data loaded

> ⚠️ The app's API likely uses a different endpoint or authentication that isn't publicly documented.
> Once PKSOL updates the public web API, the scripts will work without changes.

**Verified working example** (from app screenshots):
```json
POST https://api.pksol.com/search
{"faculty":"sg","value":"reg-p2-a-2026","roll_no":"607192"}
→ Name: MUHAMMAD ABDULLAH, Marks: 582, Grade: C, PASS
```

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

**Request Format (new):**
```json
{
  "faculty": "sg",
  "value": "reg-p2-a-2026",
  "roll_no": "607192",
  "matric_roll_no": ""
}
```

**Response Format:**
```json
{
  "detail": {
    "roll_no": 607192,
    "applicant_name": "MUHAMMAD ABDULLAH",
    "father_name": "MUHAMMAD MOBIN QURESHI",
    "secured_total": 582,
    "grade": "C"
  },
  "result": {
    "theory": [],
    "practical": []
  }
}
```

**Faculty codes:**
- `sm` — Pre-Medical
- `se` — Pre-Engineering
- `sg` — Science General
- `hmt` — Humanities
- `com` — Commerce

**Exam type codes** (pattern: `reg-{part}-{a|s}-{year}`):
- `reg-p2-a-2026` — Regular Part II 2026 Annual
- `reg-p2-s-2026` — Regular Part II 2026 Supply
- `pvt-p2-a-2026` — Private Part II 2026 Annual

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
  - Science General: 6 digits starting with 6 (e.g., 607192)
- **Error Handling:** Scripts handle API errors, timeouts, and invalid responses gracefully.
- **PDF Gazettes:** All 3 Part II 2026 PDFs are in `pdfs/` — Pre-Medical, Pre-Engineering, and Science General.
- **BIEK App vs Web API:** The mobile app (`com.biek.edu.app`) uses the same `value`+`faculty` format but works while the public web API doesn't. The app may use a different API URL or require authentication.

---

## License

Educational use only. Respect BIEK's terms of service and avoid excessive API requests.
