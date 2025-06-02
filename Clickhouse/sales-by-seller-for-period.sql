SELECT 
    seller_name,
    period,
    sum(total_sales) AS monthly_sales,
    sum(total_orders) AS monthly_orders,
    sum(total_sales) / sum(total_orders) AS avg_check
FROM data_warehouse.sales_analytics_mart
GROUP BY seller_name, period
ORDER BY seller_name, period;