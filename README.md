# dbt Core Learning Journey (DuckDB)

A hands-on, 4-week roadmap to learn **dbt Core** using **DuckDB** as the warehouse (no cloud account or server needed).

| Week | Topic | Status |
|---|---|---|
| 1 | Setup, `profiles.yml`, project structure, first models, `ref()` | Done |
| 2 | Sources, seeds, staging models, marts, Jinja | Done |
| 3 | Tests, documentation, source freshness | Upcoming |
| 4 | Incremental models, snapshots, macros, packages, capstone | Upcoming |

---

## Tech stack
- Python 3.9+
- dbt-core
- dbt-duckdb (adapter)
- DuckDB (file-based database)

---

## Repo structure

```
dbt_learning/
├── README.md
├── .gitignore
├── requirements.txt
└── my_first_project/
    ├── dbt_project.yml        # project config and folder-level defaults
    ├── load_raw.py            # loads raw CSVs into DuckDB (simulates EL)
    ├── inspect_db.py          # helper to view tables and data in DuckDB
    ├── data/                  # raw CSVs (outside dbt)
    │   ├── customers.csv
    │   └── orders.csv
    ├── models/
    │   ├── staging/           # 1:1 with sources, light cleaning (views)
    │   │   ├── sources.yml
    │   │   ├── stg_customers.sql
    │   │   └── stg_orders.sql
    │   └── marts/             # business-ready models (tables)
    │       ├── fct_orders.sql
    │       └── customer_order_counts.sql
    ├── seeds/
    │   └── status_labels.csv
    ├── macros/
    ├── snapshots/
    ├── tests/
    └── analyses/
```

Not committed (see `.gitignore`): `target/`, `logs/`, `*.duckdb`, `.venv/`, `profiles.yml`.

---

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url>
cd dbt_learning

python -m venv .venv

# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
dbt --version
```

`requirements.txt`:
```
dbt-core
dbt-duckdb
```

### 3. Create `profiles.yml`

`profiles.yml` holds connection details and is **not committed**. Create it at:
- Windows: `C:\Users\<you>\.dbt\profiles.yml`
- Mac/Linux: `~/.dbt/profiles.yml`

```yaml
my_first_project:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: dev.duckdb
      threads: 4
    prod:
      type: duckdb
      path: prod.duckdb
      threads: 8
```

The profile name must match `profile:` in `dbt_project.yml`.

### 4. Test the connection

```bash
cd my_first_project
dbt debug
```

Expect "All checks passed" and "Connection test: OK".

### 5. Load raw data into DuckDB

```bash
python load_raw.py
```

This creates the `raw.customers` and `raw.orders` tables inside `dev.duckdb`.

### 6. Build the project

```bash
dbt seed      # load seeds/status_labels.csv
dbt run       # build staging views and mart tables
```

### 7. Inspect the data

```bash
python inspect_db.py
```

`inspect_db.py`:
```python
import duckdb

con = duckdb.connect('dev.duckdb')

print(con.sql("show all tables"))
print(con.sql("""
    select table_schema, table_name, table_type
    from information_schema.tables
    where table_schema in ('raw', 'main')
"""))
print(con.sql("select * from fct_orders"))

con.close()
```

> DuckDB allows only one writer at a time. Make sure no script or DuckDB shell has `dev.duckdb` open when you run `dbt run`.

---

## Week 1: Setup and fundamentals

**Covered**
- dbt does the **T** in ELT (transforms data already in the warehouse)
- `profiles.yml` (profile, target, outputs, threads) vs `dbt_project.yml`
- Project folder structure
- Models, `ref()` and the DAG
- Materializations: view, table, incremental, ephemeral
- Compiled SQL in `target/compiled/` vs executed SQL in `target/run/`

**Commands**
```bash
dbt debug                        # check connection and setup
dbt compile                      # Jinja -> plain SQL, no execution
dbt run                          # build all models
dbt run --select my_model        # build one model
dbt docs generate && dbt docs serve
```

**Key config**
```sql
{{ config(materialized='table') }}
```

---

## Week 2: Sources, staging and marts

**Covered**
- Raw data loaded with `load_raw.py` (simulates Fivetran/Airbyte)
- **Sources** declared in `sources.yml` and used with `source('raw', 'orders')`
- **Staging models**: one per source table, light cleaning only (rename, cast, simple derived columns)
- **Mart**: `fct_orders` joins staging models using `ref()` and the import CTE pattern
- Folder-level materializations in `dbt_project.yml`
- **Jinja**: `{{ }}` expressions, `{% %}` logic, `{# #}` comments, a `for` loop in `customer_order_counts.sql`
- **Seeds** for small static lookup data (`status_labels.csv`)

**Folder-level materializations**
```yaml
models:
  my_first_project:
    staging:
      +materialized: view
    marts:
      +materialized: table
```

**Source declaration**
```yaml
version: 2

sources:
  - name: raw
    schema: raw
    tables:
      - name: customers
      - name: orders
```

**DAG**
```
raw.customers -> stg_customers --+
                                 +--> fct_orders
raw.orders    -> stg_orders   ---+
```

**`source()` vs `ref()`**
| Function | Use for |
|---|---|
| `source('raw', 'orders')` | Raw tables dbt did not build |
| `ref('stg_orders')` | Models or seeds dbt built |

**Node selection**
```bash
dbt run --select stg_orders+     # model and everything downstream
dbt run --select +fct_orders     # model and everything upstream
```

---

## Week 3: Testing and documentation (upcoming)
- Generic tests: `unique`, `not_null`, `accepted_values`, `relationships`
- Singular tests (custom SQL)
- Source freshness
- `dbt test`, `dbt build`, `dbt docs`

## Week 4: Intermediate skills and capstone (upcoming)
- Incremental models
- Snapshots (SCD Type 2)
- Macros and packages (`dbt_utils`)
- Environments and node selection
- Capstone project

---

## Quick command cheat sheet

| Command | Purpose |
|---|---|
| `dbt debug` | Verify connection and config |
| `dbt seed` | Load CSVs from `seeds/` |
| `dbt compile` | Generate compiled SQL |
| `dbt run` | Build models |
| `dbt test` | Run tests (Week 3) |
| `dbt build` | Seed + run + test in DAG order |
| `dbt docs generate` / `dbt docs serve` | Build and view documentation |

---

## Common errors

| Error | Cause |
|---|---|
| Could not find profile | Profile name mismatch between `dbt_project.yml` and `profiles.yml` |
| Database is locked | Another process has `dev.duckdb` open |
| Source not found | Name in `source()` does not match `sources.yml` |
| Schema `raw` not found | `load_raw.py` was not run first |
| YAML error | Tabs used instead of spaces |