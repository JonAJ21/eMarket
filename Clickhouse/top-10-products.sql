top_products AS (
    SELECT 
        product_id
    FROM sales_aggregation
    GROUP BY product_id
    ORDER BY sum(total_sales) DESC
    LIMIT 10
),