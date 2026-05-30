import psycopg2

def get_connection(database_url, ssl_root_cert):
    conn = psycopg2.connect(
        database_url,
        sslmode="verify-full",
        sslrootcert=ssl_root_cert
    )

    conn.set_session(
        readonly=True,
    )

    return conn