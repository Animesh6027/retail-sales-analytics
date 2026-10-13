USE retail_analytics;

SELECT ROUND(SUM(sales), 2) AS total_revenue FROM order_items;
SELECT ROUND(SUM(profit), 2) AS total_profit FROM order_items;
SELECT COUNT(*) AS number_of_orders FROM orders;
SELECT SUM(quantity) AS total_units_sold FROM order_items;
SELECT ROUND(SUM(item_totals.order_sales) / COUNT(*), 2) AS average_order_value
FROM (
    SELECT order_id, SUM(sales) AS order_sales
    FROM order_items
    GROUP BY order_id
) AS item_totals;
