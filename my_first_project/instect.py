import duckdb
con = duckdb.connect('dev.duckdb')

print(con.sql("""
    select table_schema, table_name, table_type
    from information_schema.tables
    where table_schema in ('raw', 'main')
"""))

print(con.sql("select * from fct_orders"))
con.close()