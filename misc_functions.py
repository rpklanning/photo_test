import os
import pandas as pd
import psycopg2
from psycopg2 import sql
import logging
import streamlit as st
import datetime
from datetime import date

# setup error logging capture
logger = logging.getLogger(__name__)

@st.cache_data
def GET_NEW_NO_COL_RECORD_VALUE(df):
    """
    Function will receive the dataframe and read the No column into a list.  The list will be converted to integers and
    the maximum value determined.  The new value will be determined by incrementing the maximum value by 1.  This will
    be converted to a string and returned to the calling program
    :param df: dataframe containing the No column
    :return: no_col_new_value - string of the incremented max value of the No column
    """

    logger.info("")
    logger.info("FUNCTION WILL PARSE THE DATAFRAME AND GET NEXT NO COLUMN VALUE")
    logger.info("Attempt to convert 'No' column to list.")
    # read the "No" field of the dataframe into a list.
    try:
        lst_no_col_str = df['No'].tolist()
        logger.info("Conversion of 'No' column to list was successful.")

    except KeyError as e:
        logger.error(f"KeyError captured: The column {e} does not exist in the DataFrame.")
        lst_no_col_str = []
        no_col_next_value = "X"
        return no_col_next_value

    # convert the string values in No column to integers using list comprehension
    lst_no_col_int = [int(x) for x in lst_no_col_str]

    # get the max value in No column
    no_col_max_value = max(lst_no_col_int)

    # increment the max value in No column of dataframe by 1 and convert to string
    no_col_next_value = str(no_col_max_value + 1)

    if no_col_next_value is not "":
        logger.info("Obtaining 'No' column max value, incrementing, and converting to string was successful.")

    return no_col_next_value

@st.cache_data
def GET_ACTIVE_LIST(df, get_column, status_column):
    """
    Function will parse a dataframe and return a list of get_column items based on whether the status_colum
     is "Active"
    :param df: dataframe of the projects_list containing 'Status' and 'Project' columns
    :param get_column: field which will be obtained from the dataframe based on the status_column
    :param status_column: column which will be evaluated to confirm it is "Active"
    :return: active_list - list of get column records
    """
    logger.info("")
    logger.info("ATTEMPT TO PARSE THE DATAFRAME AND GET A LIST OF THE ACTIVE RECORDS")
    logger.info(f"Parsing of dataframe column {status_column}=Active to obtain list of column records {get_column}")
    # parse the database
    try:
        active_list = df.loc[df['Status'] == status_column, get_column].tolist()
        logger.info("Generation of the active {get_column} list was successful.")
        return active_list

    except KeyError as e:
        logger.error(f"KeyError captured: The column {e} does not exist in the DataFrame.")
        active_list = []

        return active_list

@st.cache_data
def GET_TODAYS_DATE_AND_FORMAT():
    logger.info("")

    # generate and display today's data
    day = date.today()
    day_str = (str(day)).replace("-","")
    return day_str

