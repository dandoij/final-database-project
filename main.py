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
    while True:
        choice = ui.prompt_menu("Customer Menu", [
            ("1", "Database status"),
            ("0", "Back to role selection"),
        ])
        if choice == "0":
            return
        if choice == "1":
            show_database_status(conn)


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
