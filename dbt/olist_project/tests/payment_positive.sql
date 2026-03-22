SELECT *
FROM {{ ref('fct_payments') }}
WHERE payment_value < 0