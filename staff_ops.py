from decimal import Decimal

import psycopg2

import customer_ops
import ui


def create_staff(conn):
    print("\n-- New staff member --")
    first_name = ui.prompt_text("First name", max_length=50)
    last_name = ui.prompt_text("Last name", max_length=50)

    while True:
        email = ui.prompt_text("Email", max_length=100)
        if "@" in email and "." in email.split("@")[-1]:
            break
        print("  That does not look like an email address.")

    role = ui.prompt_text("Role (optional)", required=False, max_length=50)

    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Staff (first_name, last_name, email, role) "
                "VALUES (%s, %s, %s, %s) RETURNING staff_id",
                (first_name, last_name, email, role),
            )
            staff_id = cur.fetchone()[0]
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        print(f"\n  {email} is already registered to another staff member.")
        return None
    except psycopg2.Error as exc:
        conn.rollback()
        print(f"\n  Could not add the staff member: {str(exc).strip().splitlines()[0]}")
        return None

    print(f"\n  Added staff member #{staff_id}: {first_name} {last_name}")
    return (staff_id, first_name, last_name, email)


def select_staff(conn):
    while True:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT staff_id, first_name, last_name, email, role "
                "FROM Staff ORDER BY staff_id"
            )
            staff = cur.fetchall()

        rows = [(s[0], f"{s[1]} {s[2]}", s[3], s[4]) for s in staff]
        print("\nWho is working?")
        choice = ui.choose_row(
            ["ID", "Name", "Email", "Role"],
            rows,
            prompt="Select staff #",
            new_label="Add a new staff member",
        )

        if choice is None:
            return None
        if choice is ui.NEW:
            created = create_staff(conn)
            if created is None:
                continue
            return created

        return next(s for s in staff if s[0] == choice[0])


def add_product(conn, staff):
    print(f"\n-- New product, added by {staff[1]} {staff[2]} --")

    with conn.cursor() as cur:
        cur.execute(
            "SELECT DISTINCT category FROM Product "
            "WHERE category IS NOT NULL ORDER BY category"
        )
        categories = [c[0] for c in cur.fetchall()]

    name = ui.prompt_text("Product name", max_length=100)
    description = ui.prompt_text("Description (optional)", required=False)
    price = ui.prompt_decimal("Price", minimum=Decimal("0.01"))
    stock = ui.prompt_int("Initial stock", minimum=0)

    print(f"  Existing categories: {', '.join(categories)}")
    category = ui.prompt_text("Category (optional)", required=False, max_length=50)

    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Product (name, description, price, stock_quantity, category, staff_id) "
                "VALUES (%s, %s, %s, %s, %s, %s) RETURNING product_id",
                (name, description, price, stock, category, staff[0]),
            )
            product_id = cur.fetchone()[0]
    except psycopg2.Error as exc:
        conn.rollback()
        print(f"\n  Could not add the product: {str(exc).strip().splitlines()[0]}")
        return

    print(f"\n  Added product #{product_id}: {name} at {ui.money(price)}, {stock} in stock.")


def update_product(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT product_id, name, category, price, stock_quantity "
            "FROM Product ORDER BY name"
        )
        products = cur.fetchall()

    print("\nWhich product needs updating?")
    choice = ui.choose_row(
        ["ID", "Name", "Category", "Price", "Stock"],
        [(p[0], p[1], p[2], ui.money(p[3]), p[4]) for p in products],
        prompt="Select product #",
    )
    if choice is None:
        return

    product = next(p for p in products if p[0] == choice[0])
    print(f"\n{product[1]}: {ui.money(product[3])}, {product[4]} in stock")
    print("  Leave a field blank to keep its current value.")

    price = ui.prompt_decimal("New price", minimum=Decimal("0.01"), required=False)
    stock = ui.prompt_int("New stock quantity", minimum=0, required=False)

    if price is None and stock is None:
        print("\n  Nothing changed.")
        return

    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE Product SET price = COALESCE(%s::numeric, price), "
                "stock_quantity = COALESCE(%s::integer, stock_quantity) "
                "WHERE product_id = %s RETURNING name, price, stock_quantity",
                (price, stock, product[0]),
            )
            name, new_price, new_stock = cur.fetchone()
    except psycopg2.Error as exc:
        conn.rollback()
        print(f"\n  Could not update the product: {str(exc).strip().splitlines()[0]}")
        return

    print(f"\n  {name} is now {ui.money(new_price)} with {new_stock} in stock.")


def low_stock_report(conn):
    threshold = ui.prompt_int("\nShow products with stock at or below", minimum=0)

    with conn.cursor() as cur:
        cur.execute(
            "SELECT product_id, name, category, stock_quantity, price "
            "FROM Product WHERE stock_quantity <= %s "
            "ORDER BY stock_quantity ASC, name",
            (threshold,),
        )
        products = cur.fetchall()

    print(f"\nProducts at or below {threshold} in stock:")
    ui.print_table(
        ["ID", "Name", "Category", "Stock", "Price"],
        [(p[0], p[1], p[2], p[3], ui.money(p[4])) for p in products],
        empty_message="Every product is above that threshold.",
    )


def view_all_orders(conn):
    while True:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT p.purchase_id, p.purchase_date, "
                "c.first_name || ' ' || c.last_name, p.status, p.total_amount "
                "FROM Purchase p JOIN Customer c ON c.customer_id = p.customer_id "
                "ORDER BY p.purchase_date DESC"
            )
            orders = cur.fetchall()

        print("\nAll orders, most recent first:")
        choice = ui.choose_row(
            ["Order", "Date", "Customer", "Status", "Total"],
            [
                (o[0], o[1].strftime("%Y-%m-%d %H:%M"), o[2], o[3], ui.money(o[4]))
                for o in orders
            ],
            prompt="View details for order #",
            empty_message="No orders yet.",
        )
        if choice is None:
            return

        customer_ops.show_order_details(conn, choice[0])
