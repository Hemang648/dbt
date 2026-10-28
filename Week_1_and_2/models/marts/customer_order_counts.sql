{% set statuses = ['placed', 'shipped', 'completed', 'returned'] %}

select
    customer_id,
    {% for s in statuses %}
    sum(case when status = '{{ s }}' then 1 else 0 end) as {{ s }}_orders
    {%- if not loop.last %},{% endif %}
    {% endfor %}
from {{ ref('stg_orders') }}
group by 1