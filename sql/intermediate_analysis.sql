USE retail_analytics;

SELECT p.category, p.subcategory, ROUND(SUM(i.sales), 2) AS revenue, ROUND(SUM(i.profit), 2) AS profit
FROM order_items i INNER JOIN products p ON p.product_id = i.product_id
GROUP BY p.category, p.subcategory ORDER BY revenue DESC;

SELECT DATE_FORMAT(o.order_date, '%Y-%m-01') AS month, ROUND(SUM(i.sales), 2) AS revenue, ROUND(SUM(i.profit), 2) AS profit
FROM orders o INNER JOIN order_items i ON i.order_id = o.order_id
GROUP BY month ORDER BY month;

SELECT o.region, o.state, ROUND(SUM(i.sales), 2) AS revenue
FROM orders o INNER JOIN order_items i ON i.order_id = o.order_id
GROUP BY o.region, o.state ORDER BY revenue DESC;

SELECT p.product_id, p.product_name, ROUND(SUM(i.sales), 2) AS revenue
FROM products p INNER JOIN order_items i ON i.product_id = p.product_id
GROUP BY p.product_id, p.product_name ORDER BY revenue DESC LIMIT 10;

SELECT c.customer_id, c.customer_name, ROUND(SUM(i.sales), 2) AS spending
FROM customers c INNER JOIN orders o ON o.customer_id = c.customer_id INNER JOIN order_items i ON i.order_id = o.order_id
GROUP BY c.customer_id, c.customer_name ORDER BY spending DESC LIMIT 10;

SELECT p.product_id, p.product_name, ROUND(SUM(i.profit), 2) AS profit
FROM products p INNER JOIN order_items i ON i.product_id = p.product_id
GROUP BY p.product_id, p.product_name HAVING profit < 0 ORDER BY profit;

SELECT p.category, ROUND(AVG(i.discount), 4) AS average_discount
FROM products p INNER JOIN order_items i ON i.product_id = p.product_id
GROUP BY p.category ORDER BY average_discount DESC;
