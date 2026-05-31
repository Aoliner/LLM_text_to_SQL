import psycopg2

def get_connection(database_url, ssl_root_cert):
    try:
        conn = psycopg2.connect(
            database_url,
            sslmode="verify-full",
            sslrootcert=ssl_root_cert,
        )
        conn.set_session(readonly=True)
        return conn
    except psycopg2.OperationalError as e:
        raise RuntimeError(f"Database connection failed: {e}") from e