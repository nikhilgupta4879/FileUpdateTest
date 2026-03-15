# Bill Config Processor – Code Workflow

## Overview

`bill_config_processor.py` automates the replacement of bill image files and
generates the SQL remediation scripts needed to reset database state after a
bill image swap. It reads a single Excel configuration file, performs file
system operations for every configured record, and appends ready-to-execute
SQL statements to two output script files.

---

## Directory Layout

```
FileUpdateTest/                        ← Project root
│
├── Config/
│   └── BillUpdateConfig03152026.xlsx  ← Input: configuration workbook
│
├── SourceCode/
│   └── bill_config_processor.py       ← Main script
│
└── TestFiles/                         ← Base path for all image operations
    ├── <companyCode>/
    │   └── bill/
    │       └── <date>/
    │           └── <BillImageName>    ← Current bill images live here
    ├── newImages/
    │   └── <NewBillImageName>         ← Replacement images are sourced here
    └── scripts/
        ├── ResetCurrGuidToNull.txt    ← Output: GUID-reset SQL statements
        └── UpdateTaskToPushImageAgain.txt  ← Output: Task-reset SQL statements
```

---

## Configuration Workbook Structure

File: `Config/BillUpdateConfig03152026.xlsx`

| Column | Header           | Description                                      |
|--------|------------------|--------------------------------------------------|
| A      | S. No            | Sequential row number (row 3 onward = data)      |
| B      | CompanyCode      | Company identifier used in the Task SQL          |
| C      | ClaimNumber      | Claim reference (informational)                  |
| D      | BillNumber       | Bill reference (informational)                   |
| E      | BillImagePath    | Relative path to the current bill image folder   |
| F      | BillImageName    | File name of the current bill image              |
| G      | CurrentGUID      | GUID stored in the database for this image       |
| H      | ImageID          | `billImageId` primary key in `BillImage` table   |
| I      | taskId           | `taskId` in `Integration.dbo.Task`               |
| J      | NewBillImagePath | Relative path to the replacement image folder    |
| K      | NewBillImageName | File name of the replacement image               |

> Row 1 = headers, Row 2 = blank (ignored), data begins at Row 3.
> Rows without a value in **S. No** are skipped automatically.

---

## Processing Steps (per data row)

```
START
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 1 – Load Config                                    │
│  Read BillUpdateConfig03152026.xlsx from Config/        │
│  Parse header row (row 1), skip blank row 2             │
│  Collect all rows where S. No is non-empty              │
└───────────────────────────┬─────────────────────────────┘
                            │  for each row …
                            ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 2 – Resolve Paths                                  │
│  BillImagePath  → TestFiles/<path>/<BillImageName>      │
│  NewBillImagePath → TestFiles/<path>/<NewBillImageName> │
│  Script output  → TestFiles/scripts/                   │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 3 – Archive Current Bill Image                     │
│                                                         │
│  Rename:                                                │
│    <BillImagePath>/<BillImageName>                      │
│      →  <BillImagePath>/<stem>_toberenamed<ext>         │
│                                                         │
│  Example:                                               │
│    aic_curr_1.pdf  →  aic_curr_1_toberenamed.pdf        │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 4 – Copy New Image to Bill Image Directory         │
│                                                         │
│  Copy:                                                  │
│    <NewBillImagePath>/<NewBillImageName>                 │
│      →  <BillImagePath>/<NewBillImageName>              │
│                                                         │
│  Example:                                               │
│    TestFiles/newImages/aic_new_1.pdf                    │
│      →  TestFiles/aic/bill/03142026/aic_new_1.pdf       │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 5 – Rename New Image to Canonical Bill Image Name  │
│                                                         │
│  Rename:                                                │
│    <BillImagePath>/<NewBillImageName>                   │
│      →  <BillImagePath>/<BillImageName>                 │
│                                                         │
│  Example:                                               │
│    aic_new_1.pdf  →  aic_curr_1.pdf                     │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│ STEPS 6 & 7 – Generate & Append GUID-Reset SQL          │
│                                                         │
│  Template:                                              │
│    update Integration.bill.BillImage                    │
│    set externalRefGUID = null                           │
│    where billImageId = '<ImageID>'                      │
│    and externalRefGUID='<CurrentGUID>';                 │
│                                                         │
│  Appended to:                                           │
│    TestFiles/scripts/ResetCurrGuidToNull.txt            │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│ STEPS 8 & 9 – Generate & Append Task-Reset SQL          │
│                                                         │
│  Template:                                              │
│    update Integration.dbo.Task                          │
│    set taskStatus='Ready',                              │
│        processCounter=0,                                │
│        batchId=null                                     │
│    where taskId = '<taskId>'                            │
│    and companyCode='<CompanyCode>';                     │
│                                                         │
│  Appended to:                                           │
│    TestFiles/scripts/UpdateTaskToPushImageAgain.txt     │
└───────────────────────────┬─────────────────────────────┘
                            │  next row …
                            ▼
                  ┌─────────────────┐
                  │ Summary logged  │
                  │ Success / Error │
                  │ counts printed  │
                  └─────────────────┘
```

---

## File State After Successful Run

For each processed row the directory `<BillImagePath>` will contain:

| File                                  | Description                              |
|---------------------------------------|------------------------------------------|
| `<BillImageName>`                     | The new replacement image (active)       |
| `<stem>_toberenamed<ext>`             | The original image (archived/renamed)    |

---

## SQL Output Files

### `TestFiles/scripts/ResetCurrGuidToNull.txt`

Resets `externalRefGUID` to `NULL` in `Integration.bill.BillImage` for each
swapped image. This breaks the stale GUID link so the image can be
re-associated correctly on the next processing cycle.

```sql
update Integration.bill.BillImage set externalRefGUID = null where billImageId = '1000001' and externalRefGUID='9b945784-366a-4432-b7d2-303a203675dd';
update Integration.bill.BillImage set externalRefGUID = null where billImageId = '1000019' and externalRefGUID='c0fb04c2-a0c9-4893-b02a-e8e1897c35fb';
...
```

### `TestFiles/scripts/UpdateTaskToPushImageAgain.txt`

Resets the corresponding Task record to `Ready` status so the workflow engine
will re-queue and re-push the newly swapped image.

```sql
update Integration.dbo.Task set taskStatus='Ready',processCounter=0,batchId=null where taskId = '6000111' and companyCode='AIC';
update Integration.dbo.Task set taskStatus='Ready',processCounter=0,batchId=null where taskId = '6000211' and companyCode='BOG';
...
```

---

## Running the Script

### Prerequisites

```bash
pip install openpyxl
```

### Default execution (from project root)

```bash
python SourceCode/bill_config_processor.py
```

### Custom paths

```bash
python SourceCode/bill_config_processor.py \
    --base-path  /absolute/path/to/TestFiles \
    --config-path /absolute/path/to/Config/BillUpdateConfig03152026.xlsx
```

### Command-line help

```bash
python SourceCode/bill_config_processor.py --help
```

---

## Error Handling

| Scenario                           | Behaviour                                     |
|------------------------------------|-----------------------------------------------|
| Config file not found              | Script exits immediately with an error        |
| Source file missing (Step 3)       | Warning logged; row processing continues      |
| New image file missing (Step 4)    | Warning logged; row processing continues      |
| Any unexpected exception per row   | Error logged; processing continues for next row |
| SQL script directory missing       | Automatically created if absent               |

---

## Logging

All activity is written to `stdout` in the format:

```
YYYY-MM-DD HH:MM:SS  LEVEL     Message
```

A final summary line reports total rows processed and any error count:

```
2026-03-15 10:00:05  INFO      === Completed: 4 row(s) processed, 0 error(s) ===
```
