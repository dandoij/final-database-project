# ShopDB — Requirements

## Data Requirements

**Customer** — first and last name, email address, optional phone number, and the date
the account was created. Email must be unique.

**Staff** — first and last name, email address, job role, and hire date. Email must be
unique.

**Product** — name, optional description, price, current stock quantity, optional
category, and the staff member who added it. Price must be greater than zero; stock may
reach zero but never go negative.

**Credit Card** — the card network, last four digits, expiration month and year, and
optional billing ZIP. A card belongs to exactly one customer and cannot exist without
one, so it is identified by its owner plus a card number. A card that has already
expired may not be registered. Full card numbers are never stored.

**Purchase** — date and time, fulfillment status, total amount charged, the customer who
placed it, and the card used to pay. The card must belong to the purchasing customer. A
customer with no registered card cannot place an order.

**Purchase Line Items** — for each product in a purchase, the quantity bought and the
unit price at the time of the sale. The historical price is stored so that later price
changes do not rewrite past orders.

## Relationships

| Relationship | Cardinality | Participation |
| --- | --- | --- |
| Customer **owns** CreditCard | 1:N | Optional for Customer, total for CreditCard (identifying — CreditCard is a weak entity) |
| Customer **places** Purchase | 1:N | Optional for Customer, total for Purchase |
| CreditCard **pays for** Purchase | 1:N | Optional for CreditCard, total for Purchase |
| Staff **maintains** Product | 1:N | Optional for Staff, total for Product |
| Purchase **contains** Product | M:N | Total for Purchase, optional for Product — resolved by PurchaseItem, which carries `quantity` and `unit_price` |

## Functional Requirements

### Customer

| ID | Requirement |
| --- | --- |
| C1 | Create a customer account with name, email, and optional phone; reject a duplicate email with a readable message |
| C2 | List all products with name, category, price, and stock |
| C3 | Search products by a substring of the name, case-insensitively |
| C4 | Filter products by category |
| C5 | Register a credit card; reject an expiration date in the past |
| C6 | View the cards registered to the account |
| C7 | Add products and quantities to a cart, review it, and remove lines |
| C8 | Check out the cart against a chosen registered card |
| C9 | View past orders with date, status, and total, and drill into one for its line items |

### Staff

| ID | Requirement |
| --- | --- |
| S1 | Add a product with name, description, price, initial stock, and category, attributed to the acting staff member |
| S2 | Update an existing product's price, stock quantity, or both |
| S3 | List products at or below a stock threshold the staff member supplies, lowest stock first |
| S4 | View every order in the system, most recent first, with the customer's name |
| S5 | Add a new staff member, rejecting a duplicate email |

### Reporting

| ID | Requirement |
| --- | --- |
| R1 | List customers alongside the products they purchased, limited to products above a supplied price |
| R2 | Rank products by total revenue across all purchases |
| R3 | List products that have never been purchased |

## Business Rules

| ID | Rule | Enforced by |
| --- | --- | --- |
| B1 | Customer and staff email addresses are unique | `UNIQUE` constraint |
| B2 | Product price is greater than zero | `CHECK (price > 0)` |
| B3 | Stock quantity is never negative | `CHECK (stock_quantity >= 0)` |
| B4 | Line item quantity is at least one | `CHECK (quantity > 0)` |
| B5 | A card's expiration month is 1–12 | `CHECK (exp_month BETWEEN 1 AND 12)` |
| B6 | A card may not be registered already expired | Application check before insert |
| B7 | A purchase must be paid with a card belonging to the purchasing customer | Composite `FOREIGN KEY (customer_id, card_id)` |
| B8 | An order may not be placed for more units than are in stock | Application check inside the checkout transaction |
| B9 | An order either records completely — purchase, all line items, and all stock decrements — or not at all | Single transaction with explicit commit/rollback |
| B10 | A line item's unit price is the product's price at the time of sale and never changes afterward | `unit_price` stored on `PurchaseItem` |

## Assumptions

- One store with one inventory; no warehouses or locations.
- No authentication. The application asks which role and which person is acting; it does
  not verify identity.
- No real payment processing, shipping, returns, reviews, discounts, or taxes.
- Prices are in US dollars, stored as `NUMERIC(10,2)` for exact arithmetic.
- A cart exists only for the duration of a shopping session and is never persisted; only
  completed purchases are stored.
- Order status is set to `Pending` at creation; fulfillment workflow beyond that is out
  of scope.
- Sample data is fictional, and card details are last-four digits only.
