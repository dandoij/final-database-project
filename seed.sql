-- Staff
INSERT INTO Staff (staff_id, first_name, last_name, email, role, hire_date) VALUES
    (1, 'Alice',  'Nguyen', 'alice.nguyen@shopdb.example',  'Inventory Manager', '2023-03-15'),
    (2, 'Marcus', 'Bell',   'marcus.bell@shopdb.example',   'Sales Associate',   '2024-01-08'),
    (3, 'Priya',  'Raman',  'priya.raman@shopdb.example',   'Store Manager',     '2022-07-01');

-- Customers. Tomas Novak has no credit card, so checkout must refuse him.
INSERT INTO Customer (customer_id, first_name, last_name, email, phone) VALUES
    (1, 'John',   'Carter',  'john.carter@example.com',    '513-555-0142'),
    (2, 'Maria',  'Lopez',   'maria.lopez@example.com',    '513-555-0173'),
    (3, 'Wei',    'Zhang',   'wei.zhang@example.com',      '859-555-0110'),
    (4, 'Fatima', 'Ali',     'fatima.ali@example.com',     '513-555-0198'),
    (5, 'Derek',  'Olsen',   'derek.olsen@example.com',    '937-555-0121'),
    (6, 'Hannah', 'Schmidt', 'hannah.schmidt@example.com', '513-555-0167'),
    (7, 'Luis',   'Ortega',  'luis.ortega@example.com',    '859-555-0184'),
    (8, 'Grace',  'Kim',     'grace.kim@example.com',      '513-555-0159'),
    (9, 'Tomas',  'Novak',   'tomas.novak@example.com',    '937-555-0136');

-- Products across 5 categories.
-- Products 5, 8, 14, 16 are low on stock; 9 and 15 are never purchased.
INSERT INTO Product (product_id, name, description, price, stock_quantity, category, staff_id) VALUES
    (1,  'Wireless Headphones',       'Over-ear Bluetooth headphones with active noise cancelling', 129.99,  40, 'Electronics',    1),
    (2,  '27" 4K Monitor',            'IPS 4K UHD monitor with USB-C power delivery',               289.50,  12, 'Electronics',    1),
    (3,  'Mechanical Keyboard',       'Tenkeyless mechanical keyboard, brown switches',              89.99,  25, 'Electronics',    1),
    (4,  'USB-C Hub',                 '7-in-1 USB-C hub with HDMI and card reader',                  34.95,  60, 'Electronics',    2),
    (5,  'Bluetooth Speaker',         'Portable waterproof speaker, 12-hour battery',                59.00,   3, 'Electronics',    2),
    (6,  'Espresso Machine',          'Semi-automatic espresso machine with milk frother',          249.99,   8, 'Home & Kitchen', 3),
    (7,  '8" Chef Knife',             'Forged stainless steel chef knife with walnut handle',        74.50,  18, 'Home & Kitchen', 3),
    (8,  'Cast Iron Skillet',         'Pre-seasoned 12-inch cast iron skillet',                      42.00,   5, 'Home & Kitchen', 1),
    (9,  'Ceramic Dinnerware Set',    '16-piece stoneware dinnerware set, service for four',        118.75,  10, 'Home & Kitchen', 3),
    (10, 'Database Systems Textbook', 'Undergraduate textbook on relational database design',       156.00,  22, 'Books',          2),
    (11, 'The Pragmatic Programmer',  'Classic software craftsmanship title, 20th anniversary ed.',  45.99,  30, 'Books',          2),
    (12, 'Pocket Notebook 3-Pack',    'Dot-grid pocket notebooks, 48 pages each',                    12.50, 100, 'Books',          1),
    (13, 'Running Shoes',             'Neutral cushioned road running shoes',                       110.00,  14, 'Apparel',        2),
    (14, 'Rain Jacket',               'Lightweight waterproof shell with taped seams',               89.95,   2, 'Apparel',        3),
    (15, 'Yoga Mat',                  'Non-slip 6mm exercise mat with carry strap',                  28.99,  45, 'Sports',         1),
    (16, 'Adjustable Dumbbell Set',   'Pair of adjustable dumbbells, 5-52 lbs each',                199.99,   4, 'Sports',         3);

-- Credit cards, 1-2 per customer. card_id is global to the table, not per customer.
INSERT INTO CreditCard (customer_id, card_id, card_type, last_four, exp_month, exp_year, billing_zip) VALUES
    (1,  1, 'Visa',       '4242',  8, 2027, '45219'),
    (1,  2, 'Mastercard', '5581',  3, 2028, '45219'),
    (2,  3, 'Visa',       '1881', 11, 2027, '45044'),
    (3,  4, 'Amex',       '0005',  6, 2029, '41075'),
    (4,  5, 'Discover',   '9424',  2, 2028, '45236'),
    (5,  6, 'Visa',       '7712',  9, 2027, '45402'),
    (6,  7, 'Mastercard', '3310', 12, 2028, '45140'),
    (6,  8, 'Visa',       '8802',  4, 2027, '45140'),
    (7,  9, 'Visa',       '5566',  7, 2027, '41017'),
    (8, 10, 'Mastercard', '2244',  1, 2029, '45242');

-- Purchases. Each total_amount equals the sum of its line items below.
INSERT INTO Purchase (purchase_id, purchase_date, status, total_amount, customer_id, card_id) VALUES
    (1,  '2026-03-04 10:15:00', 'Delivered',  199.89, 1,  1),
    (2,  '2026-03-18 14:02:00', 'Delivered',  156.00, 2,  3),
    (3,  '2026-04-02 09:47:00', 'Delivered',  114.99, 3,  4),
    (4,  '2026-04-11 16:30:00', 'Delivered',  249.99, 1,  2),
    (5,  '2026-04-25 11:20:00', 'Delivered',  155.99, 4,  5),
    (6,  '2026-05-06 13:05:00', 'Shipped',    348.50, 5,  6),
    (7,  '2026-05-14 08:55:00', 'Shipped',    129.00, 6,  7),
    (8,  '2026-05-29 19:40:00', 'Shipped',    199.99, 7,  9),
    (9,  '2026-06-08 12:12:00', 'Processing', 259.98, 8, 10),
    (10, '2026-06-19 15:33:00', 'Processing', 135.94, 2,  3),
    (11, '2026-07-01 10:05:00', 'Pending',    280.94, 6,  8),
    (12, '2026-07-12 17:26:00', 'Pending',    232.50, 3,  4);

-- Line items. unit_price is the product's price at the time of the purchase.
INSERT INTO PurchaseItem (purchase_id, product_id, quantity, unit_price) VALUES
    (1,   1, 1, 129.99),
    (1,   4, 2,  34.95),
    (2,  10, 1, 156.00),
    (3,   3, 1,  89.99),
    (3,  12, 2,  12.50),
    (4,   6, 1, 249.99),
    (5,  13, 1, 110.00),
    (5,  11, 1,  45.99),
    (6,   2, 1, 289.50),
    (6,   5, 1,  59.00),
    (7,   7, 1,  74.50),
    (7,   8, 1,  42.00),
    (7,  12, 1,  12.50),
    (8,  16, 1, 199.99),
    (9,   1, 2, 129.99),
    (10, 14, 1,  89.95),
    (10, 11, 1,  45.99),
    (11, 10, 1, 156.00),
    (11,  3, 1,  89.99),
    (11,  4, 1,  34.95),
    (12, 13, 2, 110.00),
    (12, 12, 1,  12.50);

-- The IDs above are explicit, so advance each sequence past them.
SELECT setval(pg_get_serial_sequence('staff',      'staff_id'),    (SELECT MAX(staff_id)    FROM Staff));
SELECT setval(pg_get_serial_sequence('customer',   'customer_id'), (SELECT MAX(customer_id) FROM Customer));
SELECT setval(pg_get_serial_sequence('product',    'product_id'),  (SELECT MAX(product_id)  FROM Product));
SELECT setval(pg_get_serial_sequence('creditcard', 'card_id'),     (SELECT MAX(card_id)     FROM CreditCard));
SELECT setval(pg_get_serial_sequence('purchase',   'purchase_id'), (SELECT MAX(purchase_id) FROM Purchase));
