# dbt-Core Learning Journey (DuckDB)

A hands-on, 4-week roadmap to learn **dbt Core** using **DuckDB** as the warehouse (no cloud account or server needed). Each week has its own folder, so the repo shows how the project grew.

| Week | Topic | Folder | Status |
|---|---|---|---|
| 1 | Setup, `profiles.yml`, project structure, models, `ref()` | `week_1_and_2/` (foundation) | Done |
| 2 | Sources, seeds, staging, marts, Jinja | `week_1_and_2/` | Done |
| 3 | Tests, source freshness, documentation | `week_3/` | Done |
| 4 | Incremental, snapshots, macros, packages, environments | `week_4/` | Done |

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
│
├── week_1_and_2/                          # Weeks 1-2: setup, sources, staging, marts
│   ├── dbt_project.yml
│   ├── load_raw.py                  # loads raw CSVs into DuckDB
│   ├── inspect_db.py                # view tables and data
│   ├── data/
│   │   ├── customers.csv
│   │   └── orders.csv
│   ├── models/
│   │   ├── staging/
│   │   │   ├── sources.yml
│   │   │   ├── stg_customers.sql
│   │   │   └── stg_orders.sql
│   │   └── marts/
│   │       ├── fct_orders.sql
│   │       └── customer_order_counts.sql
│   └── seeds/
│       └── status_labels.csv
│
├── week_3/                          # Week 2 project + tests, freshness, docs
│   ├── dbt_project.yml
│   ├── load_raw.py
│   ├── inspect_db.py
│   ├── data/
│   ├── models/
│   │   ├── docs.md                  # reusable doc blocks
│   │   ├── staging/
│   │   │   ├── sources.yml          # + source tests and freshness
│   │   │   ├── schema.yml           # + generic tests and descriptions
│   │   │   ├── stg_customers.sql
│   │   │   └── stg_orders.sql
│   │   └── marts/
│   │       ├── schema.yml           # + mart tests and descriptions
│   │       ├── fct_orders.sql
│   │       └── customer_order_counts.sql
│   ├── seeds/
│   │   └── status_labels.csv
│   └── tests/
│       └── assert_amount_not_negative.sql   # singular test
│
└── week_4/                          # Week 3 project + incremental, snapshots, macros, packages
    ├── dbt_project.yml              # + tags
    ├── packages.yml                 # dbt_utils (restored with dbt deps)
    ├── load_raw.py                  # now accepts a database name
    ├── inspect_db.py
    ├── data/
    ├── macros/
    │   └── cents_to_dollars.sql     # reusable macro
    ├── models/
    │   ├── docs.md
    │   ├── staging/
    │   │   ├── sources.yml
    │   │   ├── schema.yml           # + dbt_utils.accepted_range test
    │   │   ├── stg_customers.sql
    │   │   └── stg_orders.sql       # uses cents_to_dollars()
    │   └── marts/
    │       ├── schema.yml
    │       ├── fct_orders.sql       # now incremental, with surrogate key
    │       └── customer_order_counts.sql
    ├── seeds/
    │   └── status_labels.csv
    ├── snapshots/
    │   └── customers_snapshot.yml   # SCD Type 2 history
    └── tests/
        └── assert_amount_not_negative.sql
```

Not committed (see `.gitignore`): `target/`, `logs/`, `dbt_packages/`, `*.duckdb`, `.venv/`, `profiles.yml`.

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

### 3. Create `profiles.yml` (not committed)

Location:
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

The profile name must match `profile:` in `dbt_project.yml`. Both week folders keep `profile: 'my_first_project'`, so this one file works for all of them. The `path` is relative to where you run dbt, so each week gets its own database file.

### 4. Run a week's project

```bash
cd week_3                 # or week_2
dbt debug                 # expect "Connection test: OK"
python load_raw.py        # load raw CSVs into DuckDB
dbt seed                  # load seeds
dbt build                 # seed + run + test in DAG order (use dbt run in week_2)
python inspect_db.py      # look at the data
```

> DuckDB allows only one writer at a time. Make sure no script or shell has the `.duckdb` file open when you run dbt.

---

## Week 1: Setup and fundamentals

**Theory**
- dbt does the **T** in ELT. It transforms data that is already in the warehouse.
- A **model** is one `.sql` file with one `SELECT`. dbt wraps it in `CREATE VIEW/TABLE`.
- `ref()` links models and builds the **DAG** (dependency order).
- `profiles.yml` holds connection details (outside Git). `dbt_project.yml` holds project settings.

**Materializations**
| Type | Meaning |
|---|---|
| `view` | Saved query, runs when read (default) |
| `table` | Results stored physically |
| `incremental` | Adds only new rows (Week 4) |
| `ephemeral` | Inlined as a CTE, never built |

```sql
{{ config(materialized='table') }}
```

**The `target/` folder**
| Folder | Contains |
|---|---|
| `models/` | Your SQL + Jinja |
| `target/compiled/` | Jinja resolved into plain SQL |
| `target/run/` | Final SQL executed, including `CREATE` wrapper |

**Commands**
```bash
dbt debug                        # check connection and setup
dbt compile                      # Jinja -> plain SQL, no execution
dbt run                          # build all models
dbt run --select my_model        # build one model
```

---

## Week 2: Sources, staging and marts

**Theory**
- Raw data is loaded outside dbt (Fivetran, Airbyte, or `load_raw.py` here).
- **Sources** declare raw tables and are used with `source()`. Models and seeds dbt builds are used with `ref()`.
- **Staging**: one model per source table, light cleaning only (rename, cast). No joins.
- **Marts**: joins and business logic, built from staging with `ref()`.
- **Seeds**: small static CSVs (lookup tables), loaded with `dbt seed`.
- **Jinja**: `{{ }}` output, `{% %}` logic, `{# #}` comments.

**DAG**
```
raw.customers -> stg_customers --+
                                 +--> fct_orders
raw.orders    -> stg_orders   ---+
```

**Sources**
```yaml
version: 2

sources:
  - name: raw
    schema: raw
    tables:
      - name: customers
      - name: orders
```

**Staging model**
```sql
select
    id as customer_id,
    first_name || ' ' || last_name as full_name,
    email
from {{ source('raw', 'customers') }}
```

**Mart with import CTEs**
```sql
with orders as (
    select * from {{ ref('stg_orders') }}
),
customers as (
    select * from {{ ref('stg_customers') }}
)

select orders.*, customers.full_name, customers.email
from orders
left join customers using (customer_id)
```

**Folder-level materializations**
```yaml
models:
  my_first_project:
    staging:
      +materialized: view
    marts:
      +materialized: table
```

**Jinja loop**
```sql
{% set statuses = ['placed', 'shipped', 'completed', 'returned'] %}

select
    customer_id,
    {% for s in statuses %}
    sum(case when status = '{{ s }}' then 1 else 0 end) as {{ s }}_orders
    {%- if not loop.last %},{% endif %}
    {% endfor %}
from {{ ref('stg_orders') }}
group by 1
```

**Node selection**
```bash
dbt run --select stg_orders+     # model and everything downstream
dbt run --select +fct_orders     # model and everything upstream
```

---

## Week 3: Testing, freshness and documentation

**Theory**
- A dbt **test** is a query that returns **bad rows**. Zero rows means pass.
- **Generic tests** are declared in YAML: `unique`, `not_null`, `accepted_values`, `relationships`.
- **Singular tests** are custom SQL files in `tests/`.
- **Source freshness** checks how recent raw data is (`warn_after` and `error_after`).
- `dbt build` runs everything in DAG order and **skips downstream models when an upstream test fails**, so bad data never reaches marts.
- Documentation lives next to the code (descriptions and doc blocks) and powers the docs site and lineage graph.

**Generic tests (`models/staging/schema.yml`)**
```yaml
version: 2

models:
  - name: stg_orders
    description: One row per order, cleaned from raw.orders.
    columns:
      - name: order_id
        data_tests:
          - unique
          - not_null
      - name: customer_id
        data_tests:
          - not_null
          - relationships:
              to: ref('stg_customers')
              field: customer_id
      - name: status
        description: "{{ doc('order_status') }}"
        data_tests:
          - accepted_values:
              values: ['placed', 'shipped', 'completed', 'returned']
```

| Test | Fails when |
|---|---|
| `unique` | A value appears more than once |
| `not_null` | A value is null |
| `accepted_values` | A value is outside the list |
| `relationships` | A foreign key has no parent row (orphan) |

**Singular test (`tests/assert_amount_not_negative.sql`)**
```sql
select order_id, amount
from {{ ref('stg_orders') }}
where amount < 0
```

**Source tests and freshness (`models/staging/sources.yml`)**
```yaml
sources:
  - name: raw
    schema: raw
    tables:
      - name: orders
        loaded_at_field: "cast(order_date as timestamp)"
        freshness:
          warn_after: {count: 30, period: day}
          error_after: {count: 365, period: day}
        columns:
          - name: id
            data_tests:
              - unique
              - not_null
```

**Severity (warn instead of fail)**
```yaml
- accepted_values:
    values: ['placed', 'shipped', 'completed', 'returned']
    config:
      severity: warn
```

**Doc block (`models/docs.md`)**
```markdown
{% docs order_status %}
The current state of an order: placed, shipped, completed or returned.
{% enddocs %}
```

**Commands**
```bash
dbt test                                 # all tests
dbt test --select stg_orders             # one model
dbt test --select source:raw             # source tests only
dbt test --select test_type:singular     # singular tests only
dbt test --select stg_orders --store-failures   # save failing rows in the DB
dbt source freshness                     # check raw data freshness
dbt build                                # seed + run + test in DAG order
dbt docs generate
dbt docs serve --port 8081               # lineage graph and model docs
```

**Breaking data on purpose (practice)**

Adding a duplicate order id, an orphan customer id, an unknown status and a negative amount to `data/orders.csv` should trigger the `unique`, `relationships`, `accepted_values` and singular tests. Read the output (`Got N results, configured to fail if != 0`), inspect the compiled test SQL in `target/compiled/`, then remove the bad rows.

---

## Week 4: Incremental models, snapshots, macros, packages and environments

**Theory**
| Concept | What it is | Why it matters |
|---|---|---|
| **Incremental model** | A table that processes only new or changed rows on each run | Saves time and cost on large data |
| **Snapshot** | Records how a row changes over time (SCD Type 2) | Keeps history that raw data overwrites |
| **Macro** | A reusable Jinja function | Removes copy-pasted SQL |
| **Package** | A shared dbt project (macros, tests, models) | Reuses community code like `dbt_utils` |
| **Target / environment** | dev vs prod connection and settings | Safe development before production |

**Setup for this week**
```bash
# from dbt_learning/
cp -r week_3 week_4          # Windows: xcopy week_3 week_4 /E /I
cd week_4
# delete the copied target/ folder and dev.duckdb, then:
python load_raw.py
dbt deps                     # installs packages from packages.yml
dbt build
```

**`load_raw.py` (accepts an optional database name)**
```python
import sys
import duckdb

db = sys.argv[1] if len(sys.argv) > 1 else 'dev.duckdb'
con = duckdb.connect(db)
con.sql("create schema if not exists raw")
con.sql("create or replace table raw.customers as select * from read_csv_auto('data/customers.csv')")
con.sql("create or replace table raw.orders as select * from read_csv_auto('data/orders.csv')")
print(f"Loaded raw data into {db}")
print(con.sql("select count(*) as orders from raw.orders"))
con.close()
```
```bash
python load_raw.py                 # loads dev.duckdb
python load_raw.py prod.duckdb     # loads prod.duckdb (needed before --target prod)
```

**Macro (`macros/cents_to_dollars.sql`)**
```sql
{% macro cents_to_dollars(column_name, scale=2) %}
    round({{ column_name }} / 100.0, {{ scale }})
{% endmacro %}
```
```sql
-- used in stg_orders.sql
{{ cents_to_dollars('amount_cents') }} as amount
```
Compiles to `round(amount_cents / 100.0, 2)`. Check it with `dbt compile --select stg_orders`.

**Package (`packages.yml`)**
```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: [">=1.1.0", "<2.0.0"]
```
```bash
dbt deps
```
```sql
-- surrogate key in fct_orders
{{ dbt_utils.generate_surrogate_key(['orders.order_id', 'orders.customer_id']) }} as order_key,
```
```yaml
# package test in models/staging/schema.yml
- name: amount
  data_tests:
    - dbt_utils.accepted_range:
        min_value: 0
```
If dbt warns about test arguments, use the one-line form: `- dbt_utils.accepted_range: {arguments: {min_value: 0}}`.

**Incremental model (`models/marts/fct_orders.sql`)**
```sql
{{
    config(
        materialized='incremental',
        unique_key='order_id'
    )
}}

with orders as (
    select * from {{ ref('stg_orders') }}

    {% if is_incremental() %}
    where order_date >= (select max(order_date) from {{ this }})
    {% endif %}
),

customers as (
    select * from {{ ref('stg_customers') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['orders.order_id', 'orders.customer_id']) }} as order_key,
    orders.order_id,
    orders.order_date,
    orders.status,
    orders.amount,
    customers.customer_id,
    customers.full_name,
    customers.email
from orders
left join customers
    on orders.customer_id = customers.customer_id
```

| Piece | Meaning |
|---|---|
| `materialized='incremental'` | First run builds the full table, later runs process only new rows |
| `is_incremental()` | True only when the table exists and `--full-refresh` was not used |
| `{{ this }}` | The model's own existing table |
| `unique_key` | Matching rows are updated instead of duplicated |
| `>=` filter | Reprocesses the latest date so same-day late arrivals are not missed |

**Incremental pitfalls**
- **Late-arriving data:** rows with an old date that arrive later are missed. Use a lookback window or filter on a load timestamp.
- **Changed old rows:** a date filter misses updates to old rows. An `updated_at` column is the correct filter.
- **Logic changes** only apply to new rows. Rebuild with `--full-refresh`.
- Always set a `unique_key` unless the data is append-only.

**Snapshot (`snapshots/customers_snapshot.yml`)**
```yaml
snapshots:
  - name: customers_snapshot
    relation: source('raw', 'customers')
    config:
      schema: snapshots
      unique_key: id
      strategy: check
      check_cols: [first_name, last_name, email]
```
This is the YAML style for dbt 1.9 and later. Older versions use a `{% snapshot %}` Jinja block with `target_schema`.

```bash
dbt snapshot                 # take a snapshot
# change a customer in data/customers.csv, then:
python load_raw.py
dbt snapshot                 # a new row is added for the changed customer
```

| Column | Meaning |
|---|---|
| `dbt_valid_from` | When this version became active |
| `dbt_valid_to` | When it was replaced (`NULL` means current) |

- **`check` strategy:** compares the listed columns. **`timestamp` strategy:** uses an `updated_at` column (cheaper, preferred when reliable).
- Snapshots only capture changes that exist when they run, so run them regularly.

**Environments (dev vs prod)**
```bash
python load_raw.py prod.duckdb
dbt build --target prod      # builds into prod.duckdb
dbt build                    # builds into dev.duckdb (default target)
```
```sql
{% if target.name == 'dev' %}
limit 100
{% endif %}
```
Common pattern: dev builds a small sample for speed, prod builds everything.

**Tags and node selection (`dbt_project.yml`)**
```yaml
models:
  my_first_project:
    staging:
      +materialized: view
      +tags: ['staging']
    marts:
      +materialized: table
      +tags: ['marts', 'daily']
```
```bash
dbt build --select tag:daily                 # everything tagged daily
dbt build --select staging                   # a folder
dbt build --select +fct_orders               # model and all upstream
dbt build --select stg_orders+               # model and all downstream
dbt build --select fct_orders --exclude tag:staging
dbt ls --select +fct_orders                  # list what would run, without running
```
For CI, `dbt build --select state:modified+` runs only changed models and their downstream, using a saved `manifest.json` (`--state path/`).

**Project conventions**
- Prefixes: `stg_` (staging), `int_` (intermediate), `fct_` (facts), `dim_` (dimensions).
- One source table per staging model, no joins in staging.
- Import CTEs at the top, final `select` at the bottom.
- Every model has a primary key with `unique` and `not_null` tests.

**Next: capstone project** on a public dataset (for example Olist e-commerce) with sources, staging, intermediate models, a fact and a dimension, tests on all keys, an incremental model, a snapshot, generated docs and a clean README.

---

## Command cheat sheet

| Command | Purpose |
|---|---|
| `dbt debug` | Verify connection and config |
| `dbt seed` | Load CSVs from `seeds/` |
| `dbt compile` | Generate compiled SQL |
| `dbt run` | Build models |
| `dbt test` | Run tests |
| `dbt build` | Seed + run + test in DAG order |
| `dbt source freshness` | Check raw data recency |
| `dbt docs generate` / `dbt docs serve` | Build and view documentation |
| `--select model+` / `+model` | Downstream / upstream selection |
| `--target prod` | Use another environment |
| `dbt deps` | Install packages from `packages.yml` |
| `dbt snapshot` | Capture row history (SCD Type 2) |
| `--full-refresh` | Rebuild an incremental model from scratch |
| `dbt ls --select ...` | List matching nodes without running |

---

## Common errors

| Error | Cause |
|---|---|
| Could not find profile | Profile name mismatch between `dbt_project.yml` and `profiles.yml` |
| Database is locked | Another process has the `.duckdb` file open |
| Source not found | Name in `source()` does not match `sources.yml` |
| Schema `raw` not found | `load_raw.py` was not run first |
| Folder configs ignored | Key under `models:` does not match the project `name:` |
| Test not running | YAML indentation, or model name differs from the `.sql` file |
| YAML error | Tabs used instead of spaces |
| Docs port in use | Use `dbt docs serve --port 8081` |
| `dbt_utils` not found | `dbt deps` not run, or `packages.yml` not in the project root |
| Duplicates in incremental table | Missing or wrong `unique_key` |
| Old rows keep old logic | Run with `--full-refresh` |
| Prod build fails, raw tables missing | Run `python load_raw.py prod.duckdb` first |
| Snapshot schema not found | Run `show all tables`, since it may be `main_snapshots` |