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


def shop(conn, customer):
    cart = {}
    while True:
        choice = ui.prompt_menu(f"Cart ({sum(cart.values())} items)", [
            ("1", "Add a product to the cart"),
            ("2", "View the cart"),
            ("3", "Remove a product from the cart"),
            ("4", "Checkout"),
            ("0", "Leave the cart"),
        ])
        if choice == "0":
            if cart and not ui.confirm("Leaving discards the cart. Continue?"):
                continue
            return
        if choice == "1":
            add_to_cart(conn, cart)
        elif choice == "2":
            show_cart(conn, cart)
        elif choice == "3":
            remove_from_cart(conn, cart)
        elif choice == "4":
            if checkout(conn, customer, cart):
                return


def add_to_cart(conn, cart):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT product_id, name, category, price, stock_quantity "
            "FROM Product ORDER BY name"
        )
        products = cur.fetchall()

    print("\nPick a product to add:")
    choice = ui.choose_row(
        ["ID", "Name", "Category", "Price", "Stock"],
        [(p[0], p[1], p[2], ui.money(p[3]), p[4]) for p in products],
        prompt="Select product #",
    )
    if choice is None:
        return

    product = next(p for p in products if p[0] == choice[0])
    quantity = ui.prompt_int(f"Quantity of {product[1]}", minimum=1)

    already = cart.get(product[0], 0)
    cart[product[0]] = already + quantity

    if cart[product[0]] > product[4]:
        print(
            f"\n  Heads up: only {product[4]} in stock and the cart now holds "
            f"{cart[product[0]]}. Checkout will refuse this order."
        )
    else:
        print(f"\n  Cart now holds {cart[product[0]]} x {product[1]}.")


def show_cart(conn, cart):
    lines = _cart_lines(conn, cart)
    print("\nCart contents:")
    ui.print_table(
        ["ID", "Product", "Qty", "Price", "Line total"],
        [
            (l[0], l[1], l[3], ui.money(l[2]), ui.money(l[2] * l[3]))
            for l in lines
        ],
        empty_message="The cart is empty.",
    )
    if lines:
        print(f"\n  Cart total: {ui.money(sum(l[2] * l[3] for l in lines))}")


def remove_from_cart(conn, cart):
    lines = _cart_lines(conn, cart)
    if not lines:
        print("\n  The cart is empty.")
        return

    print("\nPick a product to remove:")
    choice = ui.choose_row(
        ["ID", "Product", "Qty"],
        [(l[0], l[1], l[3]) for l in lines],
        prompt="Remove #",
    )
    if choice is None:
        return

    del cart[choice[0]]
    print(f"\n  Removed {choice[1]} from the cart.")


def checkout(conn, customer, cart):
    if not cart:
        print("\n  The cart is empty, so there is nothing to check out.")
        return False

    customer_id = customer[0]
    cards = list_cards(conn, customer_id)
    if not cards:
        print(
            f"\n  {customer[1]} {customer[2]} has no credit card on file. "
            "Register a card before checking out."
        )
        return False

    print("\nPay with which card?")
    card = ui.choose_row(
        ["Card", "Type", "Number", "Expires"],
        [(c[0], c[1], f"**** {c[2]}", f"{c[3]:02d}/{c[4]}") for c in cards],
        prompt="Select card #",
    )
    if card is None:
        return False
    card_id = card[0]

    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            lines = []
            shortages = []
            for product_id, quantity in cart.items():
                cur.execute(
                    "SELECT name, price, stock_quantity FROM Product "
                    "WHERE product_id = %s",
                    (product_id,),
                )
                row = cur.fetchone()
                if row is None:
                    shortages.append(f"product #{product_id} no longer exists")
                    continue
                name, price, stock = row
                if quantity > stock:
                    shortages.append(
                        f"{name}: asked for {quantity}, only {stock} in stock"
                    )
                lines.append((product_id, name, price, quantity))

            if shortages:
                conn.rollback()
                print("\n  Order cancelled. Nothing was charged or changed:")
                for problem in shortages:
                    print(f"    - {problem}")
                return False

            total = sum(price * quantity for _, _, price, quantity in lines)

            cur.execute(
                "INSERT INTO Purchase (total_amount, customer_id, card_id) "
                "VALUES (%s, %s, %s) RETURNING purchase_id",
                (total, customer_id, card_id),
            )
            purchase_id = cur.fetchone()[0]

            for product_id, _, price, quantity in lines:
                cur.execute(
                    "INSERT INTO PurchaseItem (purchase_id, product_id, quantity, unit_price) "
                    "VALUES (%s, %s, %s, %s)",
                    (purchase_id, product_id, quantity, price),
                )
                cur.execute(
                    "UPDATE Product SET stock_quantity = stock_quantity - %s "
                    "WHERE product_id = %s",
                    (quantity, product_id),
                )

        conn.commit()
    except psycopg2.Error as exc:
        conn.rollback()
        print(f"\n  Order failed, nothing was changed: {str(exc).strip().splitlines()[0]}")
        return False
    finally:
        conn.autocommit = True

    print(f"\n  Order #{purchase_id} confirmed - paid with {card[1]} {card[2]}")
    ui.print_table(
        ["Product", "Qty", "Unit price", "Line total"],
        [(name, qty, ui.money(price), ui.money(price * qty))
         for _, name, price, qty in lines],
    )
    print(f"\n  Total charged: {ui.money(total)}")

    cart.clear()
    return True


def view_order_history(conn, customer):
    while True:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT purchase_id, purchase_date, status, total_amount "
                "FROM Purchase WHERE customer_id = %s ORDER BY purchase_date DESC",
                (customer[0],),
            )
            purchases = cur.fetchall()

        print(f"\nOrder history for {customer[1]} {customer[2]}:")
        choice = ui.choose_row(
            ["Order", "Date", "Status", "Total"],
            [
                (p[0], p[1].strftime("%Y-%m-%d %H:%M"), p[2], ui.money(p[3]))
                for p in purchases
            ],
            prompt="View details for order #",
            empty_message="No orders yet.",
        )
        if choice is None:
            return

        show_order_details(conn, choice[0])


def show_order_details(conn, purchase_id):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT p.name, pi.quantity, pi.unit_price "
            "FROM PurchaseItem pi JOIN Product p ON p.product_id = pi.product_id "
            "WHERE pi.purchase_id = %s ORDER BY p.name",
            (purchase_id,),
        )
        items = cur.fetchall()

    print(f"\nOrder #{purchase_id} line items:")
    ui.print_table(
        ["Product", "Qty", "Unit price", "Line total"],
        [(i[0], i[1], ui.money(i[2]), ui.money(i[1] * i[2])) for i in items],
    )
    print(f"\n  Order total: {ui.money(sum(i[1] * i[2] for i in items))}")


def _cart_lines(conn, cart):
    if not cart:
        return []

    with conn.cursor() as cur:
        cur.execute(
            "SELECT product_id, name, price FROM Product WHERE product_id = ANY(%s) "
            "ORDER BY name",
            (list(cart.keys()),),
        )
        return [(p[0], p[1], p[2], cart[p[0]]) for p in cur.fetchall()]


def _print_products(products, empty_message="No products found."):
    ui.print_table(
        ["ID", "Name", "Category", "Price", "Stock"],
        [(p[0], p[1], p[2], ui.money(p[3]), p[4]) for p in products],
        empty_message=empty_message,
    )
