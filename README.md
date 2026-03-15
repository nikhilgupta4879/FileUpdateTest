# FileUpdateTest

Automates bill image file swaps and generates SQL remediation scripts based on
a spreadsheet configuration.

---

## Requirements

- **Python 3.11+**
- **openpyxl** (only third-party dependency)

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/nikhilgupta4879/FileUpdateTest.git
cd FileUpdateTest
```

### 2. Create and activate a virtual environment (recommended)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Project Structure

```
FileUpdateTest/
├── Config/
│   └── BillUpdateConfig03152026.xlsx   # Input: config spreadsheet
├── SourceCode/
│   ├── bill_config_processor.py        # Main script
│   └── WORKFLOW.md                     # Detailed workflow documentation
├── TestFiles/
│   ├── <companyCode>/bill/<date>/      # Current & archived bill images
│   ├── newImages/                      # Replacement source images
│   └── scripts/
│       ├── ResetCurrGuidToNull.txt     # Generated SQL output
│       └── UpdateTaskToPushImageAgain.txt  # Generated SQL output
└── requirements.txt
```

---

## Running the Script

From the project root:

```bash
python SourceCode/bill_config_processor.py
```

### Optional arguments

| Argument | Default | Description |
|---|---|---|
| `--base-path` | `TestFiles` | Root directory for bill image files |
| `--config-path` | `Config/BillUpdateConfig03152026.xlsx` | Path to the Excel config file |

```bash
python SourceCode/bill_config_processor.py \
    --base-path TestFiles \
    --config-path Config/BillUpdateConfig03152026.xlsx
```

---

## What it does

For each data row in the config spreadsheet (starting row 3):

1. **Archives** the current bill image by renaming it `<name>_toberenamed.<ext>`
2. **Copies** the new replacement image into the bill image directory
3. **Renames** the replacement to the canonical bill image name
4. **Appends** a SQL statement to `ResetCurrGuidToNull.txt` to null out the stale `externalRefGUID`
5. **Appends** a SQL statement to `UpdateTaskToPushImageAgain.txt` to reset the Task record to `Ready`

See `SourceCode/WORKFLOW.md` for the full step-by-step workflow.
