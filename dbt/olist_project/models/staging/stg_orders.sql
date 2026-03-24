SELECT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp::timestamp AS order_purchase_ts,
    order_approved_at::timestamp AS order_approved_ts,
    order_delivered_carrier_date::timestamp AS order_delivered_carrier_ts,
    order_delivered_customer_date::timestamp AS order_delivered_customer_ts,
    order_estimated_delivery_date::timestamp AS order_estimated_delivery_ts
FROM {{ source('raw', 'raw_orders') }}