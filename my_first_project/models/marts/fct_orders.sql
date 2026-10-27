with orders as ( 
    select * from {{ref('stg_orders')}}
),

customers as (
    select * from {{ref('stg_customers')}}
),

SELECT

    orders.order_id,
    orders.order_date,
    orders.status,
    orders.amount,
    customers.customer_id,
    customers.full_name,
    customers.email

FROM orders
LEFT JOIN customers
ON orders.customer_id = customers.customer_id