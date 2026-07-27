import customer_ops
import db
import ui

TABLES = ["Customer", "Staff", "Product", "CreditCard", "Purchase", "PurchaseItem"]


def show_database_status(conn):
    rows = []
    with conn.cursor() as cur:
        for table in TABLES:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            rows.append([table, cur.fetchone()[0]])
    print("\nDatabase status:")
    ui.print_table(["Table", "Rows"], rows)


def customer_menu(conn):
    customer = customer_ops.select_customer(conn)
    if customer is None:
        return

    while True:
        title = f"Customer Menu - {customer[1]} {customer[2]}"
        choice = ui.prompt_menu(title, [
            ("1", "Browse all products"),
            ("2", "Search products by name"),
            ("3", "Browse products by category"),
            ("4", "Register a credit card"),
            ("5", "View my credit cards"),
            ("6", "Switch customer"),
            ("0", "Back to role selection"),
        ])
        if choice == "0":
            return
        if choice == "1":
            customer_ops.browse_products(conn)
        elif choice == "2":
            customer_ops.search_products_by_name(conn)
        elif choice == "3":
            customer_ops.filter_products_by_category(conn)
        elif choice == "4":
            customer_ops.register_credit_card(conn, customer)
        elif choice == "5":
            customer_ops.show_cards(conn, customer)
        elif choice == "6":
            switched = customer_ops.select_customer(conn)
            if switched is not None:
                customer = switched


def staff_menu(conn):
    while True:
        choice = ui.prompt_menu("Staff Menu", [
            ("1", "Database status"),
            ("0", "Back to role selection"),
        ])
        if choice == "0":
            return
        if choice == "1":
            show_database_status(conn)


def main():
    print("=" * 52)
    print("  ShopDB - e-commerce backend (CS4092 Final Project)")
    print("=" * 52)

    conn = db.connect_or_exit()
    conn.autocommit = True
    print("Connected to the database.")
    show_database_status(conn)

    try:
        while True:
            choice = ui.prompt_menu("Select your role", [
                ("1", "Customer"),
                ("2", "Staff"),
                ("0", "Exit"),
            ])
            if choice == "0":
                print("\nGoodbye.")
                return
            if choice == "1":
                customer_menu(conn)
            elif choice == "2":
                staff_menu(conn)
    except (KeyboardInterrupt, EOFError):
        print("\n\nInterrupted. Goodbye.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
