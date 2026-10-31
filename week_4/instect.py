import duckdb
con = duckdb.connect('prod.duckdb')

# print(con.sql("""
#     select table_schema, table_name, table_type
#     from information_schema.tables
#     where table_schema in ('raw', 'main')
# """))

print(con.sql("select * from fct_orders"))
print(con.sql("show all tables"))
print(con.sql("select * from main_snapshots.customers_snapshot order by id, dbt_valid_from"))

con.close()