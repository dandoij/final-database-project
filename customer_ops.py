from datetime import date

import psycopg2

import ui

CARD_TYPES = ["Visa", "Mastercard", "Amex", "Discover", "Other"]


def create_customer(conn):
    print("\n-- New customer --")
    first_name = ui.prompt_text("First name", max_length=50)
    last_name = ui.prompt_text("Last name", max_length=50)

    while True:
        email = ui.prompt_text("Email", max_length=100)
        if "@" in email and "." in email.split("@")[-1]:
            break
        print("  That does not look like an email address.")

    phone = ui.prompt_text("Phone (optional)", required=False, max_length=20)

    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Customer (first_name, last_name, email, phone) "
                "VALUES (%s, %s, %s, %s) RETURNING customer_id",
                (first_name, last_name, email, phone),
            )
            customer_id = cur.fetchone()[0]
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        print(f"\n  {email} is already registered. Use a different email address.")
        return None
    except psycopg2.Error as exc:
        conn.rollback()
        print(f"\n  Could not create the customer: {str(exc).strip().splitlines()[0]}")
        return None

    print(f"\n  Created customer #{customer_id}: {first_name} {last_name}")
    return (customer_id, first_name, last_name, email)


def select_customer(conn):
    while True:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT customer_id, first_name, last_name, email "
                "FROM Customer ORDER BY customer_id"
            )
            customers = cur.fetchall()

        rows = [(c[0], f"{c[1]} {c[2]}", c[3]) for c in customers]
        print("\nWho is shopping?")
        choice = ui.choose_row(
            ["ID", "Name", "Email"],
            rows,
            prompt="Select customer #",
            new_label="Create a new customer",
        )

        if choice is None:
            return None
        if choice is ui.NEW:
            created = create_customer(conn)
            if created is None:
                continue
            return created

        return next(c for c in customers if c[0] == choice[0])


def browse_products(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT product_id, name, category, price, stock_quantity "
            "FROM Product ORDER BY category, name"
        )
        products = cur.fetchall()

    print("\nAll products:")
    _print_products(products)


def search_products_by_name(conn):
    term = ui.prompt_text("\nSearch product names for")

    with conn.cursor() as cur:
        cur.execute(
            "SELECT product_id, name, category, price, stock_quantity "
            "FROM Product WHERE name ILIKE %s ORDER BY name",
            (f"%{term}%",),
        )
        products = cur.fetchall()

    print(f"\nProducts matching '{term}':")
    _print_products(products, empty_message="No products matched that search.")


def filter_products_by_category(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT DISTINCT category FROM Product "
            "WHERE category IS NOT NULL ORDER BY category"
        )
        categories = cur.fetchall()

    print("\nCategories:")
    choice = ui.choose_row(["Category"], categories, prompt="Select category #")
    if choice is None:
        return

    category = choice[0]
    with conn.cursor() as cur:
        cur.execute(
            "SELECT product_id, name, category, price, stock_quantity "
            "FROM Product WHERE category = %s ORDER BY name",
            (category,),
        )
        products = cur.fetchall()

    print(f"\nProducts in {category}:")
    _print_products(products)


def list_cards(conn, customer_id):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT card_id, card_type, last_four, exp_month, exp_year, billing_zip "
            "FROM CreditCard WHERE customer_id = %s ORDER BY card_id",
            (customer_id,),
        )
        return cur.fetchall()


def show_cards(conn, customer):
    cards = list_cards(conn, customer[0])
    print(f"\nCards on file for {customer[1]} {customer[2]}:")
    ui.print_table(
        ["Card", "Type", "Number", "Expires", "ZIP"],
        [
            (c[0], c[1], f"**** {c[2]}", f"{c[3]:02d}/{c[4]}", c[5])
            for c in cards
        ],
        empty_message="No cards registered yet.",
    )


def register_credit_card(conn, customer):
    customer_id = customer[0]
    print(f"\n-- Register a card for {customer[1]} {customer[2]} --")

    type_choice = ui.prompt_menu(
        "Card type",
        [(str(i + 1), name) for i, name in enumerate(CARD_TYPES)] + [("0", "Cancel")],
    )
    if type_choice == "0":
        return
    card_type = CARD_TYPES[int(type_choice) - 1]

    while True:
        last_four = ui.prompt_text("Last four digits")
        if len(last_four) == 4 and last_four.isdigit():
            break
        print("  Enter exactly four digits, for example 4242.")

    today = date.today()
    exp_month = ui.prompt_int("Expiration month (1-12)", minimum=1, maximum=12)
    exp_year = ui.prompt_int("Expiration year (YYYY)", minimum=2000, maximum=2099)

    if (exp_year, exp_month) < (today.year, today.month):
        print(
            f"\n  That card expired in {exp_month:02d}/{exp_year}. "
            "Register a card that is still valid."
        )
        return

    billing_zip = ui.prompt_text("Billing ZIP (optional)", required=False, max_length=10)

    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO CreditCard "
                "(customer_id, card_type, last_four, exp_month, exp_year, billing_zip) "
                "VALUES (%s, %s, %s, %s, %s, %s) RETURNING card_id",
                (customer_id, card_type, last_four, exp_month, exp_year, billing_zip),
            )
            card_id = cur.fetchone()[0]
    except psycopg2.Error as exc:
        conn.rollback()
        print(f"\n  Could not register the card: {str(exc).strip().splitlines()[0]}")
        return

    print(f"\n  Registered {card_type} ending {last_four} as card #{card_id}.")


def _print_products(products, empty_message="No products found."):
    ui.print_table(
        ["ID", "Name", "Category", "Price", "Stock"],
        [(p[0], p[1], p[2], ui.money(p[3]), p[4]) for p in products],
        empty_message=empty_message,
    )
