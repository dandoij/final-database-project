```text
Table Customer {
  customer_id int [pk, increment]
  first_name varchar(50) [not null]
  last_name varchar(50) [not null]
  email varchar(100) [not null, unique]
  phone varchar(20)
  created_at timestamp [not null, default: `CURRENT_TIMESTAMP`]
}

Table Staff {
  staff_id int [pk, increment]
  first_name varchar(50) [not null]
  last_name varchar(50) [not null]
  email varchar(100) [not null, unique]
  role varchar(50)
  hire_date date [not null, default: `CURRENT_DATE`]
}

Table Product {
  product_id int [pk, increment]
  name varchar(100) [not null]
  description text
  price numeric(10,2) [not null, note: 'CHECK (price > 0)']
  stock_quantity int [not null, note: 'CHECK (stock_quantity >= 0)']
  category varchar(50)
  staff_id int [not null]
}

Table CreditCard {
  customer_id int [not null]
  card_id int [increment]
  card_type varchar(20) [not null]
  last_four char(4) [not null]
  exp_month smallint [not null, note: 'CHECK (exp_month BETWEEN 1 AND 12)']
  exp_year smallint [not null, note: 'CHECK (exp_year >= 2024)']
  billing_zip varchar(10)

  indexes {
    (customer_id, card_id) [pk]
  }
}

Table Purchase {
  purchase_id int [pk, increment]
  purchase_date timestamp [not null, default: `CURRENT_TIMESTAMP`]
  status varchar(20) [not null, default: 'Pending']
  total_amount numeric(10,2) [not null, note: 'CHECK (total_amount >= 0)']
  customer_id int [not null]
  card_id int [not null]
}

Table PurchaseItem {
  purchase_id int [not null]
  product_id int [not null]
  quantity int [not null, note: 'CHECK (quantity > 0)']
  unit_price numeric(10,2) [not null, note: 'price at time of sale']

  indexes {
    (purchase_id, product_id) [pk]
  }
}

Ref: Product.staff_id > Staff.staff_id
Ref: CreditCard.customer_id > Customer.customer_id
Ref: Purchase.customer_id > Customer.customer_id
Ref: Purchase.(customer_id, card_id) > CreditCard.(customer_id, card_id)
Ref: PurchaseItem.purchase_id > Purchase.purchase_id
Ref: PurchaseItem.product_id > Product.product_id
```
