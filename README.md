# ShopDB - Databases Final Project

A terminal application backed by PostgreSQL for **ShopDB**, a simple e-commerce
backend. 

Customers browse products, register credit cards, and place orders. Staff add and
update products, watch inventory, and review orders. Python 3.10+ with psycopg2,
direct parameterized SQL.

**All documentation is held in the `docs/` folder, including requirements, ER Diagrams, and Schemas.**

---

## Setup

Requires PostgreSQL 14+ and Python 3.10+ already installed and on `PATH`. All commands
are PowerShell, run from the repository root.

```powershell
createdb -U postgres shopdb
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
$env:DB_PASSWORD = "your_postgres_password"
psql -U postgres -d shopdb -f schema.sql
psql -U postgres -d shopdb -f seed.sql
python main.py
```

The connection also reads `DB_HOST`, `DB_PORT`, `DB_NAME`, and `DB_USER`, which default
to `localhost`, `5432`, `shopdb`, and `postgres`. See `.env.example`.

To return to a clean, freshly seeded database at any point:

```powershell
psql -U postgres -d shopdb -f reset.sql
```

<details>
<summary>If you need PostgreSQL or Python installed:</summary>

**PostgreSQL** — installer from <https://www.postgresql.org/download/windows/>, or
`winget install -e --id PostgreSQL.PostgreSQL.17`. Add its `bin` directory (e.g.
`C:\Program Files\PostgreSQL\17\bin`) to `PATH` so `psql` and `createdb` work, then open
a new terminal.

**Python** — installer from <https://www.python.org/downloads/windows/>, checking "Add
python.exe to PATH".

If PowerShell blocks `venv\Scripts\activate`, run
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again.

</details>

---

## Files

| File | Purpose |
| --- | --- |
| `main.py` | Entry point: role selection and the menu loop |
| `db.py` | Connection handling |
| `ui.py` | Console helpers: aligned tables and validated input |
| `customer_ops.py` | Accounts, browsing, cards, cart, checkout, order history |
| `staff_ops.py` | Products, stock, low-stock report, all orders |
| `queries.py` | The three required SQL queries |
| `schema.sql` | `CREATE TABLE` statements for all six relations |
| `seed.sql` | Sample data |
| `reset.sql` | Drops and rebuilds everything in one command |
| `queries.sql` | The three required queries as standalone statements |
| `docs/` | Requirements, ER diagram, and relational schema |

---

## The three required queries

1. **Multi-table join** - customers alongside the products they purchased, limited to
   products above a price the user supplies.
2. **Aggregation** - products ranked by total revenue, `SUM(quantity * unit_price)`.
3. **Subquery** - products that have never been purchased, using `NOT EXISTS`.

Run them with `psql -U postgres -d shopdb -f queries.sql`, or from the application under
**SQL reports** in either menu.
