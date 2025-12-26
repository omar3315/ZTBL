from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, insert, select
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import sys
import oracledb

# ------------------------------
# 1️⃣ Oracle connection
# ------------------------------
def get_engine():
    username = "system"
    password = "1234"
    host = "localhost"
    port = 1521
    service_name = "ORCL"  # Or SID

    try:
        # oracledb in thin mode does NOT need Instant Client
        # oracledb.init_oracle_client(lib_dir=None)  # Only needed for thick mode

        # Build DSN for Oracle
        dsn = f"{host}:{port}/{service_name}"

        # SQLAlchemy connection string
        conn_str = f"oracle+oracledb://{username}:{password}@{dsn}?"

        engine = create_engine(conn_str)

        # Test connection
        with engine.connect():
            print("✅ Oracle DB connection established!")

        return engine

    except Exception as e:
        print(f"❌ Oracle DB connection failed:\n{e}")
        sys.exit()
