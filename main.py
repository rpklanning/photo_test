import random
import string
import streamlit as st
from neon_db_manager import READ_NEON_DB_TABLE_INTO_DATAFRAME
from logger_configuration import LOGGER_CONFIGURATION
from misc_functions import GET_NEW_NO_COL_RECORD_VALUE
from misc_functions import GET_ACTIVE_LIST
from misc_functions import GET_TODAYS_DATE_AND_FORMAT
import datetime
from datetime import date
import pandas as pd
from io import FileIO
from dotenv import load_dotenv
import sqlalchemy  # Or sqlite3 / libsql depending on your driver

# ==============================================================================
# INITIALIZE SESSION_STATE VARIABLES FOR THE SESSION
# ==============================================================================
# initialize logger.  This will only be used 1 time
if "logger" not in st.session_state:
    # Calls your function, sets up basicConfig, and returns the 'turso_app' logger
    st.session_state["logger"] = LOGGER_CONFIGURATION()

# 2 Load the .env file from the current directory
load_dotenv()

### DEFINE SESSION_STATE VARIABLES ###
if "photo_id" in st.session_state:
    st.session_state["photo_id"] = ""



def STREAMLIT_MAIN(next_no_value, todays_date, active_project, active_suppliers):
    # page configuration
    st.set_page_config(page_title="Web Cost Tracker Mobile Application", layout="wide")
    st.markdown('<p style="text-align: center; font-size: 24px;"><b>Web Cost Tracker Mobile Application<b></p>', unsafe_allow_html=True)
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background-color: #27EBF5;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    line_height = '3.5'
    col1, col2, col3, col4 = st.columns([.5,1,1,.5])

    # add widgets
    with col2:
        st.markdown(
            f"<div style='line-height: {line_height}; font-weight: bold;'>No:</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='line-height: {line_height}; font-weight: bold;'>Date:</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"<div style='line-height: {line_height}; font-weight: bold;'>Select Charges or Invoices</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='line-height: {line_height}; font-weight: bold;'>Select Active Project:</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='line-height: {line_height}; font-weight: bold;'>Select Supplier:</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='line-height: {line_height}; font-weight: bold;'>Input Amount:</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='line-height: {line_height}; font-weight: bold;'>Photo ID:</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='line-height: {line_height}; font-weight: bold;'>Input Check:</div>",
            unsafe_allow_html=True
        )

    with col3:
        st.text_input("next_no_value", value=str(next_no_value), label_visibility="collapsed", disabled=True)
        st.text_input("todays_date", value=str(todays_date), label_visibility="collapsed", disabled=True)
        unposted_items = ['Matl','Sub', 'Equip']
        selected_type = st.selectbox("Select the Unposted Item Type:", unposted_items, label_visibility="collapsed")
        selected_project = st.selectbox("Select the active project:", active_project, label_visibility="collapsed")
        selected_supplier = st.selectbox("Select the active supplier:", lst_active_suppliers, label_visibility="collapsed")
        amount = st.number_input("Enter amount($): ", min_value = 0.00, format = "%.02f",step = .01, label_visibility="collapsed")
        # generate the photo_id from the user inputs
        st.session_state["photo_id"] = selected_project + "_"+ todays_date + "_" + selected_supplier + "_" + selected_type + "_" + next_no_value
        st.text_input("photo_id", key="photo_id", label_visibility="collapsed")
        if amount == 0.00:
            st.error("Amount cannot be zero!", icon="🚨")
        else:
            st.warning("Inputs are valid!", icon="")

    # CODE SECTION TO TEST THAT THE DATAFRAME ADDITION IS WORKING CORRECTLY
    display_test = True
    if display_test:
        with st.expander("Original, New Row, and Combined Dataframe Viewing:"):
            # display the original unposted_ledger
            st.write(" Original Unposted Ledger Dataframe:")
            st.dataframe(df_unposted_ledger, hide_index=True)
            # generate a new dataframe
            df_new_row = pd.DataFrame({
                "No":[int(next_no_value)],
                "Project":[selected_project],
                "Date":[todays_date],
                "Amount":[str(round(amount,2))],
                "Supplier":[selected_supplier],
                "Posted":["No"],
                "Photo ID":[st.session_state["photo_id"]],
                "Type":[selected_type]
            })
            # display the newly created unposted item dataframe
            st.write("New Row Dataframe:")
            st.dataframe(df_new_row, hide_index=True)
            # combine the original and new row dataframes
            df_revised = pd.concat([df_unposted_ledger, df_new_row], axis=0, ignore_index=True)
            st.write("Revised Dataframe:")
            st.dataframe(df_revised, hide_index=True)

    # configure camera input
    img_file_buffer = st.camera_input("")


    if img_file_buffer is not None:
        # get and display the file size
        bytes_data = len(img_file_buffer.getvalue())
        save = st.button("💾 **Save**")
        st.write("File Size: ", bytes_data)

        if save:
            st.write("file is being saved")


#TODO append data to the dataframe using python indexer
#df = pd.DataFrame({"Name": ["Alice"], "Age": [25]})

# Append using .loc and the next available index number
#df.loc[len(df)] = ["Bob", 30]
#print(df)




# Main calling program
if __name__ == "__main__":
    # call function to read the database data needed for the program
    df_unposted_ledger = READ_NEON_DB_TABLE_INTO_DATAFRAME("wct_unposted_ledger", "unposted_ledger")
    df_projects_list = READ_NEON_DB_TABLE_INTO_DATAFRAME("wct_data", "projects_list")
    df_suppliers_list = READ_NEON_DB_TABLE_INTO_DATAFRAME("wct_data", "suppliers_list")

    # call function to get the max value in field "No" in the dataframe: df_unposted_ledger
    unposted_ledger_next_no_column_value = GET_NEW_NO_COL_RECORD_VALUE(df_unposted_ledger)

    # call function to get list of active projects from dataframe: df_projects_list
    lst_active_projects = GET_ACTIVE_LIST(df_projects_list, "Project", "Active")

    # call function to get list of active suppliers from dataframe: df_suppliers_list
    lst_active_suppliers = GET_ACTIVE_LIST(df_suppliers_list, "Company", "Active")

    # call function to get today's date
    todays_date =  GET_TODAYS_DATE_AND_FORMAT()

    # call streamlit to display the web page
    STREAMLIT_MAIN(unposted_ledger_next_no_column_value, todays_date, lst_active_projects, lst_active_suppliers)
