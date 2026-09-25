import cloudinary
import cloudinary.uploader
import streamlit as st
from dotenv import load_dotenv

# load the Cloudinary credentials from the .eng file
load_dotenv()

# assign the Cloudinary credentials to variables.
cloudinary.config(
    cloud_name="hnavxuex",
    api_key="CLOUDINARY_API_KEY",
    api_secret="CLOUDINARY_API_SECRET",
    secure=True
)

def UPLOAD_FILE_TO_CLOUDINARY(image_data, public_id, file_type):

     # folders in cloudinary are Invoices, Error_Logs, and Photos

    if file_type == "photos":
        # files stored are photos typically from mobile app camera
        subfolder = "/Photos"
        resource = "image"
    elif file_type == "miscellaneous":
        # files stored are typically pdf uploaded from email
        subfolder = "/Miscellaneous"
        resource = "raw"
    else:
        # storage of error logs
        # files stored are text files from the python program
        subfolder = "/Error_Logs"
        resource = "raw"


    if subfolder != "":
        try:
            # define the file to be uploaded, the upload location, and attempt to upload
            response = cloudinary.uploader.upload(
                image_data,
                folder="parent_folder"+ subfolder,
                public_id=st.session_state["photo_id"],
                overwrite=True,
                resource_type=resource
            )

        except Exception as e:
            print(e)
            return None