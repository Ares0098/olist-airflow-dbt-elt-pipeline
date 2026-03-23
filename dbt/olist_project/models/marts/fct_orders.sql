WITH order_items_agg AS (

    SELECT
        order_id,
        SUM(price) AS total_item_value,
        SUM(freight_value) AS total_freight_value
    FROM {{ ref('stg_order_items') }}
    GROUP BY order_id

),

orders AS (

    SELECT
        order_id,
        customer_id,
        order_purchase_ts,
        order_status
    FROM {{ ref('stg_orders') }}

)

SELECT
    o.order_id,
    o.customer_id,
    o.order_purchase_ts,
    o.order_status,

    oi.total_item_value,
    oi.total_freight_value,

    (oi.total_item_value + oi.total_freight_value) AS total_order_value

FROM orders o
LEFT JOIN order_items_agg oi
    ON o.order_id = oi.order_id