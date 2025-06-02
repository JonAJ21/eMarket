CREATE TABLE IF NOT EXISTS data_warehouse.sales_analytics_mart
(
    period Date,
    seller_id UUID,
    seller_name String,
    product_id UUID,
    product_name String,
    category_id UUID,
    category_name String,
    total_sales Float64,
    total_orders UInt64,
    avg_order_amount Float64,
    top_product_flag UInt8,
    top_seller_flag UInt8
) ENGINE = MergeTree()
ORDER BY (period, seller_id, product_id);