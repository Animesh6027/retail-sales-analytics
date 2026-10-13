USE retail_analytics;

WITH category_sales AS (
    SELECT p.category, p.subcategory, SUM(i.sales) AS revenue
    FROM products p INNER JOIN order_items i ON i.product_id = p.product_id
    GROUP BY p.category, p.subcategory
)
SELECT category, subcategory, ROUND(revenue, 2) AS revenue
FROM category_sales WHERE revenue > (SELECT AVG(revenue) FROM category_sales)
ORDER BY revenue DESC;

WITH monthly AS (
    SELECT DATE_FORMAT(o.order_date, '%Y-%m-01') AS month, SUM(i.sales) AS revenue
    FROM orders o INNER JOIN order_items i ON i.order_id = o.order_id
    GROUP BY month
)
SELECT month, ROUND(revenue, 2) AS revenue,
       ROUND((revenue - LAG(revenue) OVER (ORDER BY month)) / NULLIF(LAG(revenue) OVER (ORDER BY month), 0) * 100, 2) AS mom_growth_percent
FROM monthly ORDER BY month;

WITH product_sales AS (
    SELECT p.category, p.product_id, p.product_name, SUM(i.sales) AS revenue
    FROM products p INNER JOIN order_items i ON i.product_id = p.product_id
    GROUP BY p.category, p.product_id, p.product_name
)
SELECT category, product_name, ROUND(revenue, 2) AS revenue,
       DENSE_RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS category_rank
FROM product_sales ORDER BY category, category_rank;

WITH product_metrics AS (
    SELECT p.product_id, p.product_name, SUM(i.sales) AS revenue, SUM(i.profit) AS profit
    FROM products p INNER JOIN order_items i ON i.product_id = p.product_id
    GROUP BY p.product_id, p.product_name
)
SELECT product_id, product_name, ROUND(revenue, 2) AS revenue, ROUND(profit, 2) AS profit
FROM product_metrics
WHERE revenue >= (SELECT AVG(revenue) FROM product_metrics) AND profit < 0
ORDER BY revenue DESC;

WITH customer_orders AS (
    SELECT o.customer_id, COUNT(DISTINCT o.order_id) AS order_count, SUM(i.sales) AS spending
    FROM orders o INNER JOIN order_items i ON i.order_id = o.order_id
    GROUP BY o.customer_id
)
SELECT c.customer_id, c.customer_name, customer_orders.order_count, ROUND(customer_orders.spending, 2) AS spending
FROM customer_orders INNER JOIN customers c ON c.customer_id = customer_orders.customer_id
WHERE customer_orders.order_count >= 2
ORDER BY spending DESC;

SELECT c.customer_id, c.customer_name
FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name
HAVING COUNT(DISTINCT o.order_id) = 0;
