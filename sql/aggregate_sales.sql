SELECT 
    order_date AS sales_date,
    category,
    sub_category,
    ROUND(SUM(sales), 2) AS total_sales,
    COUNT(order_id) AS total_orders
FROM raw_sales
WHERE order_date IS NOT NULL
GROUP BY sales_date, category, sub_category
ORDER BY sales_date ASC;