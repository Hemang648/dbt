select
    id as order_id,
    user_id as customer_id,
    cast(order_date as date) as order_date,
    status,
    {{ cents_to_dollars('amount_cents') }} as amount
from {{ source('raw', 'orders') }}