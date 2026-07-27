# ShopDB

A terminal application backed by PostgreSQL for **ShopDB**, a simple e-commerce
backend. Built for CS4092 (Database Design and Development), Summer 2026.

Customers browse products, register credit cards, and place orders. Staff add and
update products, watch inventory, and review orders. Everything runs in the console —
there is no web UI and no login of any kind.

- **Python 3.10+** with **psycopg2** — direct, parameterized SQL, no ORM
- **PostgreSQL 14+**
- Windows only

---

## Setup

Everything below is written for **PowerShell on Windows**, assuming nothing is
installed yet.

### 1. Install PostgreSQL

Download the EDB installer from <https://www.postgresql.org/download/windows/> and run
it, or install it from PowerShell:

```powershell
winget install -e --id PostgreSQL.PostgreSQL.17
```

Note the password you set for the `postgres` superuser during setup. The winget
install is unattended and uses `postgres` as that password unless you override it with
`--custom "--superpassword YourPassword"`.

The installer includes `psql`, `createdb`, and pgAdmin. Make sure PostgreSQL's `bin`
directory is on your Windows `PATH` so those commands work from any terminal — the
graphical installer usually offers to do this, and you can add it by hand under
*Settings → System → About → Advanced system settings → Environment Variables → Path →
New*:

```
C:\Program Files\PostgreSQL\17\bin
```

Open a **new** terminal afterwards (PATH changes don't reach already-running ones), then
confirm:

```powershell
psql --version
Get-Service postgresql-x64-17
```

> **On ARM64 Windows** (Snapdragon machines): there is no native ARM64 build of
> PostgreSQL for Windows, so the x64 installer runs under Windows' x64 emulation. This
> works. Use an x64 build of Python to match — `psycopg2-binary` publishes `win_amd64`
> wheels but no `win_arm64` wheels.

### 2. Create the database

```powershell
createdb -U postgres shopdb
```

It will prompt for the `postgres` password. Silence means success.

### 3. Install Python

Install Python 3.10 or newer from <https://www.python.org/downloads/windows/> if you
don't have it, and check **"Add python.exe to PATH"** during installation.

### 4. Set up the Python environment

From the repository root:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

If PowerShell blocks the activation script, run this once and try again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 5. Configure the connection

The application reads its connection settings from environment variables, with
localhost defaults — no credentials are stored in the source. See `.env.example` for
the full list.

| Variable | Default |
| --- | --- |
| `DB_HOST` | `localhost` |
| `DB_PORT` | `5432` |
| `DB_NAME` | `shopdb` |
| `DB_USER` | `postgres` |
| `DB_PASSWORD` | *(empty — you must set this)* |

Set the password for your terminal session:

```powershell
$env:DB_PASSWORD = "your_postgres_password"
```

That lasts until you close the terminal. To set it permanently:

```powershell
[Environment]::SetEnvironmentVariable("DB_PASSWORD", "your_postgres_password", "User")
```

### 6. Build the schema and load the sample data

```powershell
psql -U postgres -d shopdb -f schema.sql
psql -U postgres -d shopdb -f seed.sql
```

### 7. Run the application

```powershell
python main.py
```

---

## Resetting the database

To return to a clean, freshly seeded state — useful when repeating tests — run this
from the repository root:

```powershell
psql -U postgres -d shopdb -f reset.sql
```

`reset.sql` drops every table and re-runs `schema.sql` and `seed.sql` in one command.
It uses relative paths, so run it from the repository root.

---

## Files

| File | Purpose |
| --- | --- |
| `main.py` | Entry point: role selection and the menu loop |
| `db.py` | Connection handling — `get_connection()` |
| `ui.py` | Shared console helpers: aligned tables and validated input |
| `schema.sql` | `CREATE TABLE` statements for all six relations |
| `seed.sql` | Sample data: staff, customers, products, cards, purchases |
| `reset.sql` | Drops and rebuilds everything in one command |
| `requirements.txt` | Python dependencies (`psycopg2-binary`) |
| `.env.example` | The expected environment variables |

---

## Schema

Six relations:

- **Customer** — `customer_id` PK, unique email
- **Staff** — `staff_id` PK, unique email
- **Product** — `product_id` PK, priced and stocked, attributed to the `Staff` member
  who added it
- **CreditCard** — a weak entity owned by a customer, with the composite primary key
  `(customer_id, card_id)`
- **Purchase** — belongs to a customer and references the card used
- **PurchaseItem** — resolves the M:N *Contains* relationship between `Purchase` and
  `Product`, with the composite primary key `(purchase_id, product_id)`

`Purchase`'s foreign key into `CreditCard` is the **composite pair**
`(customer_id, card_id)`, reusing `Purchase`'s own `customer_id` column. This makes it
structurally impossible to record a purchase paid for with a card belonging to a
different customer — PostgreSQL rejects it, with no application code involved.

`PurchaseItem.unit_price` stores the product's price *at the time of purchase*, so
later price changes never rewrite order history.
