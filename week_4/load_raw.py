import sys  # read command-line arguments
import duckdb  # DuckDB database library

# use the database name passed in the command, otherwise default to dev.duckdb
db = sys.argv[1] if len(sys.argv) > 1 else 'dev.duckdb'

# open the database file (creates it if it doesn't exist)
con = duckdb.connect(db)

# create the raw schema where dbt sources will point
con.sql("create schema if not exists raw")

# load customers CSV into raw.customers (replaces the table on every run)
con.sql("create or replace table raw.customers as select * from read_csv_auto('data/customers.csv')")

# load orders CSV into raw.orders (replaces the table on every run)
con.sql("create or replace table raw.orders as select * from read_csv_auto('data/orders.csv')")

# confirm which database was loaded and how many orders it has
print(f"Loaded raw data into {db}")
print(con.sql("select count(*) as orders from raw.orders"))

# release the file so dbt isn't blocked by a database lock
con.close()

#------------------------------------------------------------------------------#

# usage: python load_raw.py [db_file]  ->  e.g. python load_raw.py prod.duckdb