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