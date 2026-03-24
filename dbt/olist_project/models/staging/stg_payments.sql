SELECT
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    CAST(payment_value AS NUMERIC) AS payment_value
FROM {{ source('raw', 'raw_payments') }}