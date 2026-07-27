-- The three required SQL queries, runnable on their own:
--     psql -U postgres -d shopdb -f queries.sql
-- Each one is also wired into the application under "SQL Reports".


-- 1. Multi-table join across four tables: Customer -> Purchase -> PurchaseItem ->
--    Product. Shows the names of customers along with the names of the products
--    they purchased, limited to products priced above $100. The application
--    supplies the price as a parameter instead of the literal used here.
SELECT c.first_name || ' ' || c.last_name AS customer_name,
       p.name AS product_name,
       p.price,
       pi.quantity,
       pu.purchase_date
FROM Customer c
JOIN Purchase pu ON pu.customer_id = c.customer_id
JOIN PurchaseItem pi ON pi.purchase_id = pu.purchase_id
JOIN Product p ON p.product_id = pi.product_id
WHERE p.price > 100.00
ORDER BY customer_name, product_name;


-- 2. Aggregation with GROUP BY: total revenue per product across every purchase,
--    ranked highest first. Revenue uses PurchaseItem.unit_price, the price at the
--    time of sale, so later price changes do not rewrite past results.
SELECT p.product_id,
       p.name,
       p.category,
       SUM(pi.quantity) AS units_sold,
       SUM(pi.quantity * pi.unit_price) AS revenue
FROM Product p
JOIN PurchaseItem pi ON pi.product_id = p.product_id
GROUP BY p.product_id, p.name, p.category
ORDER BY revenue DESC;


-- 3. Correlated subquery: products that have never appeared in any purchase.
--    NOT EXISTS stops at the first matching line item, and reads as the question
--    being asked - "is there no purchase item for this product?"
SELECT p.product_id,
       p.name,
       p.category,
       p.price,
       p.stock_quantity
FROM Product p
WHERE NOT EXISTS (
    SELECT 1
    FROM PurchaseItem pi
    WHERE pi.product_id = p.product_id
)
ORDER BY p.name;
