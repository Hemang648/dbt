import duckdb
con = duckdb.connect('dev.duckdb')

print(con.sql("""
    select table_schema, table_name, table_type
    from information_schema.tables
    where table_schema in ('raw', 'main')
"""))

print(con.sql("select * from fct_orders"))

print(con.sql('select * from "dev"."main_dbt_test__audit"."relationships_stg_orders_96411fe0c89b49c3f4da955dfd358ba0"'))
con.close()