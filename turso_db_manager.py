import pandas as pd
import os
import libsql
import libsql_client.dbapi2
import logging
import streamlit as st
from sqlalchemy import create_engine

# setup error logging
logger = logging.getLogger(__name__)

def READ_DATABASE_TABLE_INTO_DATAFRAME(database_to_read, table_to_read):
    logger.info("")
    logger.info(f"START SECTION TO READ DATABASE: {database_to_read} TABLE: {table_to_read}...")

    logger.info("Attempting to get credential information.")
    # get the correct db url from the .env file
    if database_to_read == "wct-unposted-charges":
        db_url = os.getenv("TURSO_WCT_UNPOSTED_CHARGES_DB_URL")
    elif database_to_read == "wct-ledger":
        db_url = os.getenv("TURSO_WCT_LEDGER_DB_URL")
    elif database_to_read == "wct-data":
        db_url = os.getenv("TURSO_WCT_DATA_DB_URL")

    print("db_url = ", db_url)

    # log whether the db_url was obtained
    if not db_url:
        logger.error("Missing environment variable: 'TURSO_DATABASE_URL' is not set.")
    else:
        logger.info("Environmental variable: 'TURSO_DATABASE_URL' is set.")

    # get the db authorization token from the .env file
    db_authorization_token = os.getenv("TURSO_AUTH_TOKEN")
    # log whether the db_authorization_token was obtained
    if not db_authorization_token:
        logger.error("Missing environment variable: 'TURSO_DATABASE_AUTHORIZATION_TOKEN' is not set.")
    else:
        logger.info("Environmental variable: 'TURSO_DATABASE_AUTHORIZATION_TOKEN' is set.")

    # 2. use try-except to gracefully handle missing/bad config without crashing or stopping
    try:
        if not db_url or not db_authorization_token:
            # Instead of st.stop(), we raise an error to trigger the recovery UI
            raise ValueError("Missing database URL or authentication token configuration.")

        # do not use the sqlalchemy function as it is deprecated.
        logger.info("Attempt to convert database URL (db_url) to https format.")
        # 1. standardize your Turso URL scheme
        if db_url.startswith("libsql://"):
            db_url = db_url.replace("libsql://", "https://")

        # 2. define a custom cached engine factory.
        # The leading underscore on `_db_authorization_token` tells Streamlit NOT to hash it.
        @st.cache_resource
        def GET_TURSO_ENGINE(url: str, _auth_token: str):
            logger.info("Initializing cached SQLAlchemy engine with decoupled remote connection.")

            # Securely format the remote URL parameter for the driver pipeline
            separator = "&" if "?" in url else "?"
            authenticated_remote_url = f"{url}{separator}authToken={_auth_token}"

            return create_engine(
                "sqlite+pysqlite://",  # 🌟 FIX: Force a valid local isolated memory footprint
                _initialize=False,  # Bypasses internal SQLite extension function checks
                creator=lambda: libsql_client.dbapi2.connect(
                    database=authenticated_remote_url  # Explicitly pipes queries to Turso
                )
            )

        # 3. Initialize and establish your engine
        logger.info(f"Attempt to establish connection to database: {database_to_read}.")
        engine = GET_TURSO_ENGINE(db_url, db_authorization_token)
        logger.info(f"Database engine connection to database: {database_to_read} was successful!.")

        @st.cache_data
        def RUN_QUERY(query_string: str):
            # pass the global cached engine directly to pandas
            with engine.connect() as connection:
                return pd.read_sql(query_string, connection)


        df = RUN_QUERY("SELECT * FROM table_to_read;")
        st.dataframe(df)
        #TODO remove this line of code
        print(df)

    except Exception as e:
        # app stays running! Display a gentle warning with a recovery action
        # provide the clear error message to the user HMI
        st.error(f"❌ Database Subprogram Error: {e}")
        message = (f"URL conversion, connection to database: {database_to_read} table: {table_to_read} resulted "
                   f"in error: {e}.")
        logger.error(message)

        # Close the subprogram to break out of the function and go back to the main app layout.
        return

def UPDATE_DATABASE_TABLE_FROM_DATAFRAME(df, database_name, table_name):
    # 1 set Turso projects database connection url and token from Turso dashboard
    # below line of code (wct-ledger, wct-data, wct-unposted-changes) will vary based on the database used
    TURSO_DB_URL = "libsql://wct-ledger-rpklanning.aws-us-east-1.turso.io"
    TURSO_AUTH_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJnaWQiOiI5NGE5ZDI3Ny1hYWE1LTQxOWMtYjI4Yy01N2E4MmM1OTcwZWQiLCJpYXQiOjE3ODk3NDQ0OTgsImtpZCI6IllraGF5Q2RxSU5fNUs5UlNXaUFSbWlVUXRVelpjT213MFBNSWpOeXNybTAiLCJyaWQiOiIzMmYyOTdhMS05YmQ0LTQ3ODMtOGQ2MC00ZWFiMmQzZTZmMmQifQ.7-hRrfAtznJTltHj2PrB7uU1qCtlCmIqsB49cw_4Yrcb8y_ynKJlM8CHlYUgOnG9EB017MH3fRbogk6wK6slCQ"
    # 2 connect to your Turso instance
    print("Connecting to Turso Web Cost Tracing Data DB...")
    conn = libsql.connect(database=TURSO_DB_URL, auth_token=TURSO_AUTH_TOKEN)

    try:
        print(f"Uploading DataFrame to table '{table_name}'...")

        # 3 use Pandas native to_sql method to handle table creation and inserts
        # if_exists options: 'fail' (default), 'replace' (drops/recreates), or 'append'
        df.to_sql(
            name=table_name,
            con=conn,
            if_exists="replace",
            index=False,  # Set to True if you want to keep the DataFrame index as a column
            chunksize=1000,  # Batches inserts to optimize network performance over Turso
        )

        # 4 commit the transaction explicitly
        conn.commit()
        print(f"Successfully uploaded {len(df)} rows to '{table_name}'!")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # 5 close the connection
        conn.close()
