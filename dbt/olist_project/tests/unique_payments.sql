SELECT
    order_id,
    payment_sequential,
    COUNT(*)
FROM {{ ref('fct_payments') }}
GROUP BY order_id, payment_sequential
HAVING COUNT(*) > 1