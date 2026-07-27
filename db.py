import os
import sys

import psycopg2


class ConnectionError_(Exception):
    pass


def get_connection():
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")
    name = os.environ.get("DB_NAME", "shopdb")
    user = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "")

    try:
        return psycopg2.connect(
            host=host, port=port, dbname=name, user=user, password=password
        )
    except psycopg2.OperationalError as exc:
        detail = str(exc).strip().splitlines()
        detail = detail[0] if detail else "unknown error"
        raise ConnectionError_(
            "Could not connect to the database.\n"
            f"  host={host}  port={port}  database={name}  user={user}\n"
            f"  PostgreSQL said: {detail}\n"
            "  Check that the PostgreSQL service is running, that the 'shopdb'\n"
            "  database exists (createdb -U postgres shopdb), and that\n"
            '  $env:DB_PASSWORD is set for this terminal session.'
        ) from None


def connect_or_exit():
    try:
        return get_connection()
    except ConnectionError_ as exc:
        print(f"\n{exc}\n")
        sys.exit(1)
