SELECT 
    period,
    sum(total_sales) / sum(total_orders) AS avg_check
FROM data_warehouse.sales_analytics_mart
GROUP BY period
ORDER BY period;