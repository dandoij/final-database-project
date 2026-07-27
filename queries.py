from decimal import Decimal

import ui


def customers_and_products_above_price(conn, min_price):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT c.first_name || ' ' || c.last_name AS customer_name, "
            "       p.name AS product_name, "
            "       p.price, "
            "       pi.quantity, "
            "       pu.purchase_date "
            "FROM Customer c "
            "JOIN Purchase pu ON pu.customer_id = c.customer_id "
            "JOIN PurchaseItem pi ON pi.purchase_id = pu.purchase_id "
            "JOIN Product p ON p.product_id = pi.product_id "
            "WHERE p.price > %s "
            "ORDER BY customer_name, product_name",
            (min_price,),
        )
        return cur.fetchall()


def products_by_revenue(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT p.product_id, p.name, p.category, "
            "       SUM(pi.quantity) AS units_sold, "
            "       SUM(pi.quantity * pi.unit_price) AS revenue "
            "FROM Product p "
            "JOIN PurchaseItem pi ON pi.product_id = p.product_id "
            "GROUP BY p.product_id, p.name, p.category "
            "ORDER BY revenue DESC"
        )
        return cur.fetchall()


def never_purchased_products(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT p.product_id, p.name, p.category, p.price, p.stock_quantity "
            "FROM Product p "
            "WHERE NOT EXISTS ( "
            "    SELECT 1 FROM PurchaseItem pi WHERE pi.product_id = p.product_id "
            ") "
            "ORDER BY p.name"
        )
        return cur.fetchall()


def show_customers_and_products_above_price(conn):
    min_price = ui.prompt_decimal("\nShow purchases of products priced above",
                                  minimum=Decimal("0.00"))
    rows = customers_and_products_above_price(conn, min_price)

    print(f"\nCustomers and the products they bought over {ui.money(min_price)}:")
    ui.print_table(
        ["Customer", "Product", "Price", "Qty", "Purchased"],
        [
            (r[0], r[1], ui.money(r[2]), r[3], r[4].strftime("%Y-%m-%d"))
            for r in rows
        ],
        empty_message="No purchases of products above that price.",
    )


def show_products_by_revenue(conn):
    rows = products_by_revenue(conn)

    print("\nProducts ranked by total revenue:")
    ui.print_table(
        ["ID", "Product", "Category", "Units sold", "Revenue"],
        [(r[0], r[1], r[2], r[3], ui.money(r[4])) for r in rows],
        empty_message="Nothing has been purchased yet.",
    )


def show_never_purchased_products(conn):
    rows = never_purchased_products(conn)

    print("\nProducts that have never been purchased:")
    ui.print_table(
        ["ID", "Product", "Category", "Price", "Stock"],
        [(r[0], r[1], r[2], ui.money(r[3]), r[4]) for r in rows],
        empty_message="Every product has been purchased at least once.",
    )


def report_menu(conn):
    while True:
        choice = ui.prompt_menu("SQL Reports", [
            ("1", "Customers and the products they bought above a price"),
            ("2", "Products ranked by total revenue"),
            ("3", "Products never purchased"),
            ("0", "Back"),
        ])
        if choice == "0":
            return
        if choice == "1":
            show_customers_and_products_above_price(conn)
        elif choice == "2":
            show_products_by_revenue(conn)
        elif choice == "3":
            show_never_purchased_products(conn)
