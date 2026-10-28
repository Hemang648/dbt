SELECT id as customer_id,
       FirstName AS first_name,
       LastName AS last_name,
       FirstName || ' ' || LastName as full_name,
       email
FROM {{ source('raw', 'customers')}}