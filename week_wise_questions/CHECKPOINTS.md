# dbt Core Checkpoint Q&A (Weeks 1 to 4)

Self-test questions and answers for each week of the dbt Core learning journey. Try answering each question before reading the answer.

**Contents**
- [Week 1: Setup and fundamentals](#week-1-setup-and-fundamentals)
- [Week 2: Sources, staging and marts](#week-2-sources-staging-and-marts)
- [Week 3: Testing, freshness and documentation](#week-3-testing-freshness-and-documentation)
- [Week 4: Incremental, snapshots, macros, packages, environments](#week-4-incremental-snapshots-macros-packages-environments)
- [Bonus: mixed questions across weeks](#bonus-mixed-questions-across-weeks)

---

## Week 1: Setup and fundamentals

**Q1.** What do `profile`, `target` and `output` mean in `profiles.yml`?

**Ans.** A **profile** is a named set of connection settings, and it must match `profile:` in `dbt_project.yml`. An **output** is one named connection config inside it (for example `dev` or `prod`). The **target** is the output dbt uses by default.

**Q2.** Why isn't `profiles.yml` committed to Git?

**Ans.** It holds connection details and credentials, so it stays on your machine or in CI secrets. The project files (`dbt_project.yml`, models) are what go in the repo.

**Q3.** What do `dbt debug`, `dbt compile` and `dbt run` each do?

**Ans.**
- `dbt debug` checks the profile, the project and the database connection.
- `dbt compile` turns Jinja into plain SQL without running it.
- `dbt run` builds the models in the database.

**Q4.** What is the difference between `models/`, `target/compiled/` and `target/run/`?

**Ans.** `models/` holds your original SQL and Jinja. `target/compiled/` holds the same SQL with Jinja resolved (`ref()` becomes the real table name). `target/run/` holds the final SQL dbt executed, including the `CREATE VIEW/TABLE` wrapper.

**Q5.** How does `ref()` create the DAG?

**Ans.** Each `ref('model')` tells dbt that the current model depends on that model. dbt collects all these dependencies into a graph and builds the models in the right order.

**Q6.** Why did dbt build first, then second, then third?

**Ans.** Because each model used `ref()` to point at the previous one. dbt can't build a model before the one it depends on.

**Q7.** How do you switch a model between view and table?

**Ans.** Add `{{ config(materialized='table') }}` at the top of the model file, or set `+materialized` in `dbt_project.yml`. Confirm it by checking `table_type` in `information_schema.tables` (`VIEW` or `BASE TABLE`).

---

## Week 2: Sources, staging and marts

**Q1.** What is the difference between `source()` and `ref()`?

**Ans.** `source()` points to raw tables that dbt did not build (declared in `sources.yml`). `ref()` points to models and seeds that dbt built.

**Q2.** What should a staging model do, and not do?

**Ans.** It should be one model per source table, with light cleaning only: renaming, casting types and simple derived columns. It should not contain joins or business logic.

**Q3.** Why declare sources instead of hardcoding `raw.customers`?

**Ans.** You avoid hardcoded table names, the DAG and docs show where the data comes from, and you can add tests and freshness checks on the raw data.

**Q4.** How do you set materializations for a whole folder?

**Ans.** In `dbt_project.yml`:
```yaml
models:
  my_first_project:
    staging:
      +materialized: view
    marts:
      +materialized: table
```
A `config()` inside a single file overrides the folder setting.

**Q5.** What do `{{ }}`, `{% %}` and `{# #}` mean in Jinja?

**Ans.** `{{ }}` outputs an expression, `{% %}` runs logic (set, for, if), and `{# #}` is a comment that is not compiled.

**Q6.** What is the purpose of a Jinja `for` loop in dbt?

**Ans.** It generates repetitive SQL. In `customer_order_counts`, the loop expanded into four `sum(case ...)` lines, and you can verify it in `target/compiled/`.

**Q7.** When should you use a seed instead of a source?

**Ans.** Use a seed for small, static data that you manage in the repo (lookup tables, mappings). Use a source for raw data loaded into the warehouse by a pipeline, especially if it is large or changes often.

**Q8.** What does `dbt run --select stg_orders+` do, and how is it different from `+fct_orders`?

**Ans.** `stg_orders+` runs the model and everything downstream. `+fct_orders` runs the model and everything upstream.

**Q9.** Why does `load_raw.py` call `con.close()`?

**Ans.** DuckDB allows only one writer at a time. If the script keeps the file open, dbt fails with "database is locked".

---

## Week 3: Testing, freshness and documentation

**Q1.** Why does a dbt test pass when it returns zero rows?

**Ans.** Because a test is written as a query that finds bad rows. No rows means no problems were found. Any returned rows are failures.

**Q2.** Name the four built-in generic tests and what each checks.

**Ans.**
- `unique`: no value appears more than once.
- `not_null`: no value is null.
- `accepted_values`: every value is in an allowed list.
- `relationships`: every foreign key has a matching parent row (no orphans).

**Q3.** What is the difference between a generic and a singular test?

**Ans.** A generic test is reusable and declared in YAML on a column. A singular test is a custom SQL file in `tests/` for one specific rule, such as `assert_amount_not_negative`.

**Q4.** Which tests belong on primary keys and foreign keys?

**Ans.** Primary keys get `unique` and `not_null`. Foreign keys get `relationships` (and usually `not_null`).

**Q5.** How do you read a failing test?

**Ans.** The output shows which test failed and `Got N results, configured to fail if != 0`. Open the compiled test SQL under `target/compiled/` to see the exact query, or run `dbt test --store-failures` and query the `main_dbt_test__audit` schema to see the bad rows.

**Q6.** How does source freshness work?

**Ans.** You set `loaded_at_field` on a source table plus `warn_after` and `error_after` thresholds. `dbt source freshness` checks how old the newest row is. Past `warn_after` gives a WARN, past `error_after` gives an ERROR.

**Q7.** How do you make a test warn instead of fail?

**Ans.** Set `config: severity: warn` on the test. The build continues and the problem is flagged.

**Q8.** Why is `dbt build` safer than `dbt run` followed by `dbt test`?

**Ans.** `dbt build` tests each model in DAG order and skips downstream models if an upstream test fails, so bad data never reaches your marts. With `run` then `test`, everything is built before testing, so bad data is already in the marts.

**Q9.** How do you document a project and view it?

**Ans.** Add `description:` fields in `schema.yml`, and use doc blocks in `models/docs.md` with `{{ doc('name') }}` for longer text. Then run `dbt docs generate` and `dbt docs serve` to open the site with the lineage graph.

---

## Week 4: Incremental, snapshots, macros, packages, environments

**Q1.** What do `is_incremental()` and `{{ this }}` do?

**Ans.** `is_incremental()` is true only when the table already exists and `--full-refresh` wasn't used, so the filter runs only on later runs. `{{ this }}` refers to the model's own existing table, such as `select max(order_date) from {{ this }}`.

**Q2.** Why does `unique_key` matter in an incremental model?

**Ans.** If an incoming row matches an existing key, dbt updates that row instead of inserting a duplicate. Without it, reprocessed rows create duplicates.

**Q3.** Name two pitfalls of incremental models and how to handle them.

**Ans.**
- **Late-arriving data** (old dates arriving later) is missed by a date filter. Handle it with a lookback window or a load-timestamp filter.
- **Updates to old rows** are missed if the date doesn't change. Filter on an `updated_at` column instead.

Also, logic changes apply only to new rows, so rebuild with `--full-refresh`.

**Q4.** What do `dbt_valid_from` and `dbt_valid_to` represent in a snapshot?

**Ans.** `dbt_valid_from` is when that version of the row became active. `dbt_valid_to` is when it was replaced. `NULL` means it is the current version.

**Q5.** What is the difference between the `check` and `timestamp` snapshot strategies?

**Ans.** `check` compares the listed columns to detect changes. `timestamp` uses an `updated_at` column, which is cheaper and preferred when the source has a reliable one.

**Q6.** How do you write and verify a macro?

**Ans.** Define it in `macros/` with `{% macro name(args) %} ... {% endmacro %}`, call it with `{{ name(...) }}`, then run `dbt compile` and read the output in `target/compiled/` to confirm the generated SQL.

**Q7.** How do you install and use a package?

**Ans.** List it in `packages.yml` at the project root, run `dbt deps`, then use its macros and tests (for example `dbt_utils.generate_surrogate_key` and `dbt_utils.accepted_range`). `dbt_packages/` is not committed, so anyone who clones the repo runs `dbt deps`.

**Q8.** How do you build into dev and prod?

**Ans.** Load raw data into each database (`python load_raw.py prod.duckdb`), then run `dbt build --target prod`. Without `--target`, dbt uses the default (`dev`). Models can also branch with `{% if target.name == 'dev' %}`, for example to limit rows in dev.

**Q9.** How do you select models by tag, folder or graph?

**Ans.**
- Tag: `dbt build --select tag:daily`
- Folder: `dbt build --select staging`
- Upstream: `+fct_orders`, downstream: `stg_orders+`
- Exclude: `--exclude tag:staging`
- Preview without running: `dbt ls --select +fct_orders`

---

## Bonus: mixed questions across weeks

**Q1.** A mart has duplicate rows after you re-ran an incremental model. What are two likely causes?

**Ans.** A missing or wrong `unique_key`, or an overlapping filter (such as `>=`) combined with no `unique_key`.

**Q2.** `dbt build --target prod` fails saying the `raw` schema is missing. Why?

**Ans.** `prod.duckdb` is a separate file with no raw data. Run `python load_raw.py prod.duckdb` first.

**Q3.** Your folder-level `+materialized` settings are being ignored. What should you check?

**Ans.** Whether the key under `models:` in `dbt_project.yml` matches the project `name:`. A mismatch means the settings silently stop applying.

**Q4.** You changed the SQL of an incremental model, but old rows still show the old values. Why?

**Ans.** Incremental runs only process new rows. Use `--full-refresh` to rebuild the whole table.

**Q5.** Where should a "no negative amounts" rule go, and where should the cents-to-dollars conversion go?

**Ans.** The rule goes in a singular test (or `dbt_utils.accepted_range`). The conversion goes in a macro (`cents_to_dollars`) used in the staging model.