SELECT
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date::timestamp AS shipping_limit_ts,
    CAST(price AS NUMERIC) AS price,
    CAST(freight_value AS NUMERIC) AS freight_value
FROM {{ source('raw', 'raw_order_items') }}