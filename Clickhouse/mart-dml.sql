INSERT INTO data_warehouse.sales_analytics_mart
WITH 
recent_sales AS (
    SELECT 
        fs.seller_id,
        fs.product_id,
        fs.order_id,
        fs.amount,
        fs.currency,
        toDate(fs.created_at) AS sale_date,
        toStartOfMonth(fs.created_at) AS month_start
    FROM data_warehouse.fact_sales fs
    WHERE fs.created_at >= addMonths(now(), -6)
),
sales_aggregation AS (
    SELECT
        rs.month_start AS period,
        rs.seller_id,
        s.name AS seller_name,
        rs.product_id,
        p.name AS product_name,
        toUUID(p.category_id) AS category_id,
        c.name AS category_name,
        sum(rs.amount) AS total_sales,
        uniqExact(rs.order_id) AS total_orders,
        total_sales / total_orders AS avg_order_amount
    FROM recent_sales rs
    LEFT JOIN data_warehouse.dim_sellers s ON rs.seller_id = s.id
    LEFT JOIN data_warehouse.dim_products p ON rs.product_id = p.id
    LEFT JOIN data_warehouse.dim_categories c ON toUUID(p.category_id) = c.id
    GROUP BY 
        period, 
        rs.seller_id, 
        seller_name, 
        rs.product_id, 
        product_name, 
        p.category_id, 
        category_name
),
top_products AS (
    SELECT 
        product_id
    FROM sales_aggregation
    GROUP BY product_id
    ORDER BY sum(total_sales) DESC
    LIMIT 10
),
top_sellers AS (
    SELECT 
        seller_id
    FROM sales_aggregation
    GROUP BY seller_id
    ORDER BY sum(total_sales) DESC
    LIMIT 10
)
SELECT
    sa.*,
    if(tp.product_id IS NOT NULL, 1, 0) AS top_product_flag,
    if(ts.seller_id IS NOT NULL, 1, 0) AS top_seller_flag
FROM sales_aggregation sa
LEFT JOIN top_products tp ON sa.product_id = tp.product_id
LEFT JOIN top_sellers ts ON sa.seller_id = ts.seller_id;