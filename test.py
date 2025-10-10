import psycopg2
from psycopg2.extras import execute_values

# ---------- CONFIGURATION ---------- #
PROD_CONN = "postgres://postgres:XXOs1e7%7Cr_i%7CLQqs@34.131.53.198:5432/postgres"
DEV_CONN = "postgresql://neondb_owner:npg_1eOChWzpSiY6@ep-tiny-hill-a117jsao-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
BATCH_SIZE = 1000  # rows per insert
# ----------------------------------- #


# Tables to skip (system/Django tables)
SKIP_TABLES = [
    "django_migrations",
    "django_content_type",
    "auth_permission",
    "auth_group",
    "auth_group_permissions",
    "django_admin_log",
    "django_session",
    "authtoken_token",
    "django_celery_results_taskresult",
    "django_celery_results_groupresult",
    "django_celery_results_chordcounter",
    "django_celery_beat_periodictask",
    "django_celery_beat_periodictasks",
    "django_celery_beat_intervalschedule",
    "django_celery_beat_crontabschedule",
    "django_celery_beat_solarschedule",
    "django_celery_beat_clockedschedule",
]
# ----------------------------------- #


def get_tables(conn):
    """Get all user tables from the database."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type='BASE TABLE';
        """)
        return [row[0] for row in cur.fetchall()]


def fetch_table_data(conn, table_name):
    """Fetch all rows from a table in batches."""
    with conn.cursor(
        name=f"cursor_{table_name}"
    ) as cur:  # server-side cursor for large tables
        cur.itersize = BATCH_SIZE
        cur.execute(f"SELECT * FROM {table_name};")
        while True:
            rows = cur.fetchmany(BATCH_SIZE)
            if not rows:
                break
            columns = [desc[0] for desc in cur.description]
            yield columns, rows


def insert_data(dev_conn, table_name, columns, rows):
    """Insert a batch of rows into dev."""
    with dev_conn.cursor() as cur:
        cols_str = ", ".join(columns)
        query = (
            f"INSERT INTO {table_name} ({cols_str}) VALUES %s ON CONFLICT DO NOTHING;"
        )
        data = [tuple(row) for row in rows]
        if data:
            execute_values(cur, query, data, template=None, page_size=BATCH_SIZE)
    dev_conn.commit()


def main():
    # Connect to prod and dev
    with (
        psycopg2.connect(PROD_CONN) as prod_conn,
        psycopg2.connect(DEV_CONN) as dev_conn,
    ):
        tables = get_tables(prod_conn)
        # Skip system tables
        tables = [t for t in tables if t not in SKIP_TABLES]
        print(f"[+] Copying app tables: {tables}")

        for table in tables:
            print(f"[+] Copying table: {table}")
            for columns, rows in fetch_table_data(prod_conn, table):
                insert_data(dev_conn, table, columns, rows)
            print(f"[+] Finished table: {table}")

    print("[+] All app tables copied successfully!")


if __name__ == "__main__":
    main()
