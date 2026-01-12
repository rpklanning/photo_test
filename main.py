import random
import string
import streamlit as st
import datetime
from datetime import date
import pandas as pd
from io import FileIO

def test_projects():
    # used for testing only - disable when in production when the information is
    # read from the database.  The dataframe the file data is read into is
    # st.session_state.df_projects.
    description = ["Brown House", "Peters Garage", "Jones Deck"]

    lst_columns = ["Description"]

    df_projects_description = pd.DataFrame(
        list(zip(
            description
        )),
        columns=lst_columns
    )

    suppliers = ["Lowes", "84 Lumber", "Home Depot", "Dandridge Hardware"]

    lst_columns = ["Supplier"]

    df_suppliers = pd.DataFrame(
        list(zip(
            suppliers
        )),
        columns=lst_columns
    )

    return df_projects_description, df_suppliers

# obtain and display todays data
day = date.today()
st.write("Today's Date: ",day)
day_str = (str(day)).replace("-","")

# display project descriptions selection in dropdown selectbox
# TODO below code is to switch between production and test data
result = test_projects()
df_descriptions = result[0]
df_suppliers = result[1]
# df_suppliers = df_projects["Company"]
# df_descriptions = df_projects["Descriptions"]
selected_supplier = st.selectbox("Supplier: ", df_suppliers, key = "selected_supplier")
selected_project = st.selectbox("Project: ", df_descriptions, key = "selected_project")

# strip the spaces out of the selected_project
selected_project_string = selected_project.replace(" ", "")

# allow user to input the purchase amount
purchase_amount = st.number_input(
    "Enter amount($): ",
    min_value = 0.00,
    format = "%.02f",
    step = .01
)

# remove decimal from amount
purchase_amount_string = str(purchase_amount).replace(".",""
                                 )
# generate the image filename based on a 4 digit random number
characters = string.ascii_letters
variable_string ="".join(random.choices(characters, k=4))

file_name = day_str +"_" + selected_project_string + "_" + purchase_amount_string+"_" + variable_string + ".png"
st.write("File name: ", file_name)

# configure camera input
img_file_buffer = st.camera_input("")

if img_file_buffer is not None:
    # Get and display the file size
    bytes_data = len(img_file_buffer.getvalue())
    save = st.button("💾 **Save**")
    st.write("File Size: ", bytes_data)

    if save:
        st.write("file is being saved")

