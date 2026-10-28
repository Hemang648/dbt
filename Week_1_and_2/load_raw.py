import duckdb

conn = duckdb.connect(database="dev.duckdb")
conn.sql("CREATE SCHEMA IF NOT EXISTS raw")

conn.sql("CREATE OR REPLACE TABLE raw.customers AS SELECT * FROM read_csv_auto('data/customers.csv')")

conn.sql("CREATE OR REPLACE TABLE raw.orders AS SELECT * FROM read_csv_auto('data/orders.csv')")

print(conn.sql("SELECT count(*) FROM raw.customers"))
print(conn.sql("SELECT count(*) FROM raw.orders"))

conn.close()