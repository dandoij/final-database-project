from decimal import Decimal, InvalidOperation

NEW = "__new__"


def money(value):
    return f"${Decimal(str(value)):,.2f}"


def print_table(headers, rows, empty_message="(nothing to show)"):
    rows = [[("" if v is None else str(v)) for v in row] for row in rows]
    if not rows:
        print(f"  {empty_message}")
        return

    headers = [str(h) for h in headers]
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    line = "  ".join(h.ljust(w) for h, w in zip(headers, widths))
    print("  " + line.rstrip())
    print("  " + "  ".join("-" * w for w in widths))
    for row in rows:
        print("  " + "  ".join(c.ljust(w) for c, w in zip(row, widths)).rstrip())


def print_menu(title, options):
    print(f"\n=== {title} ===")
    for key, label in options:
        print(f"  {key}) {label}")


def prompt_menu(title, options):
    valid = {str(key) for key, _ in options}
    print_menu(title, options)
    while True:
        choice = input("Choice: ").strip()
        if choice in valid:
            return choice
        print("  Please enter one of: " + ", ".join(sorted(valid)))


def prompt_text(label, required=True, max_length=None):
    while True:
        value = input(f"{label}: ").strip()
        if not value:
            if required:
                print("  This field is required.")
                continue
            return None
        if max_length and len(value) > max_length:
            print(f"  Too long - {max_length} characters maximum.")
            continue
        return value


def prompt_int(label, minimum=None, maximum=None, required=True):
    while True:
        raw = input(f"{label}: ").strip()
        if not raw:
            if required:
                print("  This field is required.")
                continue
            return None
        try:
            value = int(raw)
        except ValueError:
            print("  Please enter a whole number.")
            continue
        if minimum is not None and value < minimum:
            print(f"  Must be {minimum} or greater.")
            continue
        if maximum is not None and value > maximum:
            print(f"  Must be {maximum} or less.")
            continue
        return value


def prompt_decimal(label, minimum=None, required=True):
    while True:
        raw = input(f"{label}: ").strip().lstrip("$")
        if not raw:
            if required:
                print("  This field is required.")
                continue
            return None
        try:
            value = Decimal(raw)
        except InvalidOperation:
            print("  Please enter a number, for example 19.99")
            continue
        if minimum is not None and value < minimum:
            print(f"  Must be {minimum} or greater.")
            continue
        return value.quantize(Decimal("0.01"))


def confirm(label):
    while True:
        answer = input(f"{label} (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  Please answer y or n.")


def choose_row(headers, rows, prompt="Select #", new_label=None,
               empty_message="(nothing to choose from)"):
    if not rows and not new_label:
        print(f"  {empty_message}")
        return None

    numbered = [[i + 1] + list(row) for i, row in enumerate(rows)]
    print_table(["#"] + list(headers), numbered, empty_message)

    print("  0) Cancel")
    if new_label:
        print(f"  n) {new_label}")

    while True:
        choice = input(f"{prompt}: ").strip().lower()
        if choice == "0":
            return None
        if new_label and choice == "n":
            return NEW
        try:
            index = int(choice)
        except ValueError:
            print("  Please enter one of the numbers listed.")
            continue
        if 1 <= index <= len(rows):
            return rows[index - 1]
        print("  Please enter one of the numbers listed.")
