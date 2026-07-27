# ShopDB - Databases Final Project

A terminal application backed by PostgreSQL for **ShopDB**, a simple e-commerce
backend. 

Customers browse products, register credit cards, and place orders. Staff add and
update products, watch inventory, and review orders. Python 3.10+ with psycopg2,
direct parameterized SQL, no ORM.

---

## Setup

All commands are PowerShell, run from the repository root.

**1. Install PostgreSQL 14+** — the installer from
<https://www.postgresql.org/download/windows/>, or:

```powershell
winget install -e --id PostgreSQL.PostgreSQL.17
```

Add PostgreSQL's `bin` directory (for example `C:\Program Files\PostgreSQL\17\bin`) to
your `PATH` so `psql` and `createdb` work, then open a new terminal.

**2. Create the database:**

```powershell
createdb -U postgres shopdb
```

**3. Install Python 3.10+** from <https://www.python.org/downloads/windows/>, checking
"Add python.exe to PATH", then:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

If PowerShell blocks the activation script, run
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again.

**4. Set the database password** for the terminal session:

```powershell
$env:DB_PASSWORD = "your_postgres_password"
```

The connection also reads `DB_HOST`, `DB_PORT`, `DB_NAME`, and `DB_USER`, which default
to `localhost`, `5432`, `shopdb`, and `postgres`. See `.env.example`.

**5. Build the schema and load the sample data:**

```powershell
psql -U postgres -d shopdb -f schema.sql
psql -U postgres -d shopdb -f seed.sql
```

**6. Run it:**

```powershell
python main.py
```

To return to a clean, freshly seeded database at any point:

```powershell
psql -U postgres -d shopdb -f reset.sql
```

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

1. **Multi-table join** — customers alongside the products they purchased, limited to
   products above a price the user supplies.
2. **Aggregation** — products ranked by total revenue, `SUM(quantity * unit_price)`.
3. **Subquery** — products that have never been purchased, using `NOT EXISTS`.

Run them with `psql -U postgres -d shopdb -f queries.sql`, or from the application under
**SQL reports** in either menu.
