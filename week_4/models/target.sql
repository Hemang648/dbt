select * from {{ ref('stg_orders') }}

{% if target.name == 'dev' %}
limit 100
{% endif %}