import os
import pandas as pd
import psycopg2
from psycopg2 import sql
import logging
import streamlit as st


# setup error logging capture
logger = logging.getLogger("neon_db_app")

@st.cache_data
def READ_NEON_DB_TABLE_INTO_DATAFRAME(database_to_read, table_to_read):
    """
    function will read the table of a Neon database and return a pandas dataframe.  Function requires a .env file
    containing the database URL and authorization key.  Databases to be read are limited to wct_data, wct_ledger, and
    wct_unposted_ledger.  Logging of process and errors are captured in an "Error_Log_yyyymmdd_hhmmss.
    :param database_to_read: name of the database to be read from Neon
    :param table_to_read: name of the database table to read from Neon
    :return: df dataframe containing the data and column names to be returned
    """
    logger.info("")
    logger.info(f"ATTEMPTING TO READ FROM DATABASE: {database_to_read} TABLE: {table_to_read}")
    logger.info(f"Assign correct env file KEY based on the database: {database_to_read}.")
    # map to the correct .env file KEY name
    if database_to_read == "wct_unposted_ledger":
        env_key = "NEON_WCT_UNPOSTED_LEDGER_DB_URL"
    elif database_to_read == "wct_ledger":
        env_key = "NEON_WCT_LEDGER_DB_URL"
    elif database_to_read == "wct_data":
        env_key = "NEON_WCT_DATA_DB_URL"
    else:
        logger.error(f"Invalid database name requested: '{database_to_read}'. Not from mapping logic!")
        return None

    logger.info(f"Attempting to read environment variable key '{env_key}' from .env file.")
    db_url = os.getenv(env_key)

    # check if the key exists or is completely empty in the .env file
    if not db_url:
        logger.error(f"CRITICAL: Key '{env_key}' was NOT found or is empty in the .env file.")
        return None

    # extracts the host domain from 'postgresql://user:pass@host/db' while masking the password
    safe_host = db_url.split("@")[-1] if "@" in db_url else "Unknown Host"
    logger.info(f"Successfully retrieved connection string from .env. Target host: {safe_host}")

    db_connection = None
    try:
        logger.info(f"Attempting to establish network connection to Neon host...")
        db_connection = psycopg2.connect(db_url)
        logger.info("Neon database network connection successfully established.")

        with db_connection.cursor() as cursor:
            logger.info(f"Cursor initialized. Executing query on table: '{table_to_read}'")

            query = sql.SQL("SELECT * FROM {};").format(sql.Identifier(table_to_read))
            cursor.execute(query)

            rows = cursor.fetchall()
            # log how many records PostgreSQL returned before building the dataframe
            logger.info(f"Query executed successfully. Retrieved {len(rows)} raw rows from database.")

            # get the names of the columns in the database which will be stored in the dataframe
            column_names = [desc[0] for desc in cursor.description]
            # ADDED: Log columns found to help track schema mismatch errors
            logger.debug(f"Table columns discovered: {column_names}")

            # load the data into a Pandas dataframe
            df = pd.DataFrame(rows, columns=column_names)
            return df

    except Exception as error:
        # FIXED: Added missing 'f' to string, and included the 'error' variable directly in the log
        logger.error(f"CRITICAL failure reading database '{database_to_read}', table '{table_to_read}'. Details: {error}",
                 exc_info=True)
        return None

    finally:
        if db_connection:
            db_connection.close()
            logger.info(f"Database connection to database: {database_to_read} safely closed via finally block.")