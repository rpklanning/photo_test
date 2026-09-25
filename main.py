import io
import random
import string
import streamlit as st
from neon_db_manager import READ_NEON_DB_TABLE_INTO_DATAFRAME
from logger_configuration import LOGGER_CONFIGURATION
from misc_functions import GET_NEW_NO_COL_RECORD_VALUE
from misc_functions import GET_ACTIVE_RECORDS_FROM_DATABASE
from misc_functions import GET_TODAYS_DATE_AND_FORMAT
from cloudinary_file_manager import UPLOAD_FILE_TO_CLOUDINARY
import datetime
from datetime import date
import pandas as pd
from io import FileIO
from dotenv import load_dotenv
import sqlalchemy  # Or sqlite3 / libsql depending on your driver


### PROGRAM CONFIGURATION PRIOR TO RUNNING MAIN SECTION CODE ###
################################################################
# Call function to initialize the error logger
logger = LOGGER_CONFIGURATION()
logger.info("===== LOGGER INITIALIZED =====")
logger.info(f'LOG FILE: {st.session_state.log_filename}')
logger.info(f"LOGGER NAME: {logger.name}")
logger.info(f"HANDLERS: {logger.handlers}")

# Load the .env file from the current directory
load_dotenv()

### DEFINE SESSION_STATE VARIABLES ###
######################################
if "document_id" in st.session_state:
    st.session_state["storage_id"] = ""

if "amount_number" not in st.session_state:
    st.session_state.amount_number = 0.00

if "img_file_buffer" not in st.session_state:
    st.session_state.img_file_buffer = ""

if "generate_revised_dataframe" not in st.session_state:
    st.session_state.generate_revised_dataframe = False

if "generate_photo" not in st.session_state:
    st.session_state.generate_photo = False

### FUNCTIONS CODE AREA ###
###########################
def btn_new_entry():
    st.session_state["amount_number"] = 0.00
    st.session_state.img_file_buffer = ""


### MAIN STREAMLIT SECTION ###
##############################
def STREAMLIT_MAIN(next_no_value, todays_date, active_project, active_suppliers):
    logger.info("START OF STREAMLIT PROGRAM")

    # page configuration
    st.set_page_config(page_title="Web Cost Tracker Mobile Application", layout="wide")
    st.markdown('<p style="text-align: center; font-size: 24px;"><b>Web Cost Tracker Mobile Application<b></p>', unsafe_allow_html=True)
    # change the background color of the application
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

    # add input widgets
    with col2:
       st.markdown(
            f"<div style='line-height: {line_height}; font-weight: bold;'>Todays Date:</div>",
            unsafe_allow_html=True
        )

       st.markdown(
            f"<div style='line-height: {line_height}; font-weight: bold;'>Select Charge Type:</div>",
            unsafe_allow_html=True
       )
       st.markdown(
            f"<div style='line-height: {line_height}; font-weight: bold;'>Select Active Project:</div>",
            unsafe_allow_html=True
       )
       st.markdown(
            f"<div style='line-height: {line_height}; font-weight: bold;'>Select Active Supplier:</div>",
            unsafe_allow_html=True
       )
       st.markdown(
            f"<div style='line-height: {line_height}; font-weight: bold;'>Enter Charge Amount:</div>",
            unsafe_allow_html=True
       )
       st.markdown(
            f"<div style='line-height: {line_height}; font-weight: bold;'>Generated Storage ID:</div>",
            unsafe_allow_html=True
       )
       st.markdown(
            f"<div style='line-height: {line_height}; font-weight: bold;'>Input Check:</div>",
            unsafe_allow_html=True
       )

    with col3:
        st.write("")
        st.text_input("next_no_value", value=str(next_no_value), label_visibility="collapsed", disabled=True)
        st.text_input("todays_date", value=str(todays_date), label_visibility="collapsed", disabled=True)
        unposted_items = ['Matl','Sub', 'Equip']
        selected_type = st.selectbox("Select the Unposted Item Type:",
                                     unposted_items,
                                     label_visibility="collapsed")
        selected_project = st.selectbox("Select the active project:",
                                        active_project,
                                        label_visibility="collapsed")
        selected_supplier = st.selectbox("Select the active supplier:",
                                         lst_active_suppliers,
                                         label_visibility="collapsed")
        st.number_input("Enter amount($): ",
                                 min_value = 0.00,
                                 format = "%.02f",
                                 step = .01,
                                 key="amount_number",
                                 label_visibility="collapsed")
        # generate the unique storage_id from the user inputs.  Add the jpg extension used by Chrome and Safari.
        st.session_state["storage_id"] = selected_project + "_" + todays_date + "_" + selected_supplier + "_" + selected_type + "_" + next_no_value +".jpg"
        st.text_input("storage_id",
                      key="storage_id",
                      label_visibility="collapsed",
                      disabled=True)
        if st.session_state.amount_number == 0.00:
            st.error("❌ Input Status: Amount cannot be zero!")
            st.session_state.generate_photo = False
            st.session_state.generate_new_dataframe = False
        else:
            st.warning("📷 Input Status: Inputs are valid!  User can now take photo.")
            logger.info("User inputs are valid.  Attempt to open camera and database expander sections.")
            st.session_state.generate_photo = True
            st.session_state.generate_new_dataframe = True

        # CONFIGURE CAMERA SECTION
        # configure camera input buffer
        if st.session_state.generate_photo:
            logger.info("Camera Expander Section Opened")
            img_file_buffer = st.camera_input("Take picture using buttons below:",
                                              resolution="1080p",
                                              )

            if img_file_buffer is not None:
                # --------------------------
                # image conversion of photo
                #----------------------------
                # read the image file buffer as bytes data to be transferred to Cloudinary
                bytes_data = img_file_buffer.getvalue()
                # convert bytes data into a file like object for the SDK
                image_io = io.BytesIO(bytes_data)
                # get and display the file size
                bytes_len = len(img_file_buffer.getvalue())


                logger.info("Camera has taken a photo.")

                # display buttons to post or refresh data or application
                colA, colB, colC = st.columns(3)
                with colA:
                    btn_save = st.button("💾 Save/Post Files")
                with colB:
                    btn_new = st.button("🔄 New / Refresh", on_click=btn_new_entry)
                with colC:
                    st.write("Photo Size (bytes): ", bytes_len)

                if btn_save:
                    storage_type = "photos"
                    # call function to upload the photo to Cloudinary
                    UPLOAD_FILE_TO_CLOUDINARY(image_io, st.session_state["storage_id"],storage_type)


    # EXPANDER TO VIEW DATAFRAME SECTION
    if st.session_state.generate_new_dataframe:
        with st.expander("Original, New Row, and Combined Dataframe for Checking Data Aggregation.:"):
            logger.info("Dataframe Expander Section Opened.  Attempt to display the original unposted_ledger dataframe.")

            # display the original unposted_ledger dataframe
            st.subheader("Original Unposted Ledger Dataframe:")
            st.dataframe(df_unposted_ledger, hide_index=True)
            logger.info("Original unposted_ledger table dataframe displayed")

            # generate a dataframe based on the users input data
            logger.info("Attempt to generate new dataframe based on the user input data.")
            try:
                df_new_row = pd.DataFrame({
                    "No":[int(next_no_value)],
                    "Project":[selected_project],
                    "Date":[todays_date],
                    "Amount":[str(round(st.session_state.amount_number, 2))],
                    "Supplier":[selected_supplier],
                    "Posted":["No"],
                    "Photo ID":[st.session_state["storage_id"]],
                    "Type":[selected_type]
                })
                logger.info(f"Dataframe creation from user data was successfully generated.")
            except Exception as e:
                logger.info(f"Dataframe creation from user data failed due to error {e}")
                return
            # display the new user input data dataframe
            st.subheader("New Row Dataframe:")
            st.dataframe(df_new_row, hide_index=True)

            # concatenate the original dataframe and the user data dataframe to create a combined dataframe
            logger.info(f"Attempt to create a combined dataframe consisting of the original and user input data")
            try:
                df_revised = pd.concat([df_unposted_ledger, df_new_row], axis=0, ignore_index=True)
                logger.info(f"Combined dataframe creation was successful.")
            except Exception as e:
                logger.info(f"Combined dataframe creation failed due to error {e}")
            st.subheader("Revised Dataframe:")
            st.dataframe(df_revised, hide_index=True)

    # EXPANDER TO VIEW ERROR LOG
    with st.expander(" Display the sessions error log information."):
        st.subheader("Session Error Log")
        log_contents = st.session_state.log_stream.getvalue()
        st.code(log_contents if log_contents else "No logs yet.", language="log")


### MAIN CALLING PROGRAM ###
############################
if __name__ == "__main__":
    # set the boolean bit for dataframe creation.  This is changed based on "Amount" definition above.
    generate_new_dataframe = False

    # call function to read the database data needed for the program
    df_unposted_ledger = READ_NEON_DB_TABLE_INTO_DATAFRAME("wct_unposted_ledger", "unposted_ledger")
    df_projects_list = READ_NEON_DB_TABLE_INTO_DATAFRAME("wct_data", "projects_list")
    df_suppliers_list = READ_NEON_DB_TABLE_INTO_DATAFRAME("wct_data", "suppliers_list")

    # call function to get the max value in field "No" in the dataframe: df_unposted_ledger
    unposted_ledger_next_no_column_value = GET_NEW_NO_COL_RECORD_VALUE(df_unposted_ledger)

    # call function to get list of active projects from dataframe: df_projects_list
    lst_active_projects = GET_ACTIVE_RECORDS_FROM_DATABASE(df_projects_list, "wct_data/projects_list","Project", "Status")

    # call function to get list of active suppliers from dataframe: df_suppliers_list
    lst_active_suppliers = GET_ACTIVE_RECORDS_FROM_DATABASE(df_suppliers_list, "wct_data/suppliers_list","Company", "Status")

    # call function to get today's date
    todays_date =  GET_TODAYS_DATE_AND_FORMAT()

    # call streamlit to display the web page
    STREAMLIT_MAIN(unposted_ledger_next_no_column_value, todays_date, lst_active_projects, lst_active_suppliers)
