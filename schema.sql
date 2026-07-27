DROP TABLE IF EXISTS PurchaseItem, Purchase, CreditCard, Product, Staff, Customer CASCADE;

CREATE TABLE Customer (
    customer_id   SERIAL PRIMARY KEY,
    first_name    VARCHAR(50) NOT NULL,
    last_name     VARCHAR(50) NOT NULL,
    email         VARCHAR(100) UNIQUE NOT NULL,
    phone         VARCHAR(20),
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Staff (
    staff_id      SERIAL PRIMARY KEY,
    first_name    VARCHAR(50) NOT NULL,
    last_name     VARCHAR(50) NOT NULL,
    email         VARCHAR(100) UNIQUE NOT NULL,
    role          VARCHAR(50),
    hire_date     DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE Product (
    product_id      SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    price           NUMERIC(10,2) NOT NULL CHECK (price > 0),
    stock_quantity  INTEGER NOT NULL CHECK (stock_quantity >= 0),
    category        VARCHAR(50),
    staff_id        INTEGER NOT NULL REFERENCES Staff(staff_id)
);

CREATE TABLE CreditCard (
    customer_id   INTEGER NOT NULL REFERENCES Customer(customer_id),
    card_id       SERIAL,
    card_type     VARCHAR(20) NOT NULL,
    last_four     CHAR(4) NOT NULL,
    exp_month     SMALLINT NOT NULL CHECK (exp_month BETWEEN 1 AND 12),
    exp_year      SMALLINT NOT NULL CHECK (exp_year >= 2024),
    billing_zip   VARCHAR(10),
    PRIMARY KEY (customer_id, card_id)
);

CREATE TABLE Purchase (
    purchase_id    SERIAL PRIMARY KEY,
    purchase_date  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status         VARCHAR(20) NOT NULL DEFAULT 'Pending',
    total_amount   NUMERIC(10,2) NOT NULL CHECK (total_amount >= 0),
    customer_id    INTEGER NOT NULL REFERENCES Customer(customer_id),
    card_id        INTEGER NOT NULL,
    FOREIGN KEY (customer_id, card_id) REFERENCES CreditCard(customer_id, card_id)
);

CREATE TABLE PurchaseItem (
    purchase_id  INTEGER NOT NULL REFERENCES Purchase(purchase_id),
    product_id   INTEGER NOT NULL REFERENCES Product(product_id),
    quantity     INTEGER NOT NULL CHECK (quantity > 0),
    unit_price   NUMERIC(10,2) NOT NULL CHECK (unit_price > 0),
    PRIMARY KEY (purchase_id, product_id)
);
