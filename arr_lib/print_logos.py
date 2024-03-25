import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
# from streamlit_extras.app_logo import add_logo

def print_logos():

    load_dotenv()

    try:

        # APP_LOGO = st.secrets.get("APP_LOGO", None)
        # # If the secret is not set, fall back to environment variable
        # if APP_LOGO is None:
        #     APP_LOGO = os.getenv("APP_LOGO")
        # # If APP_LOGO is set, display it in the sidebar
        # if APP_LOGO is not None:
        #     add_logo(APP_LOGO)


        # Use the .get method to safely access the secret
        CUST_LOGO = st.secrets.get("CUST_LOGO", None)
        # If the secret is not set, fall back to environment variable
        if CUST_LOGO is None:
            CUST_LOGO = os.getenv("CUST_LOGO")
        # If CUST_LOGO is set, display it in the sidebar
        if CUST_LOGO is not None:
            st.sidebar.image(CUST_LOGO, use_column_width=False)

    except Exception as e:
        print(f"An error occurred: {e}")
