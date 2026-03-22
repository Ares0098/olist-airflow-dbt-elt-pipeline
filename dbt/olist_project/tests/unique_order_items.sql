SELECT
    order_id,
    order_item_id,
    COUNT(*)
FROM {{ ref('fct_order_items') }}
GROUP BY order_id, order_item_id
HAVING COUNT(*) > 1