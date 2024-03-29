import pandas as pd
from datetime import datetime
from arr_lib.setup import PREDEFINED_DATE_FORMAT_MAP
from arr_lib.setup import PREDEFINED_COLUMN_HEADERS
import streamlit as st


def validate_input_data(input_df):
    """
    Validates uploaded contract data 
        1. Validates all the columns 
        2. Validates dates columns with the specified date format

    Parameters:
    - df (pd.DataFrame): Original contract data DataFrame.

    Returns:
    - pd.DataFrame: Processed DataFrame one row for each month - for the customer and contract 
    """
    # Check if the required columns are present

    required_columns = PREDEFINED_COLUMN_HEADERS + ['startDateFormat', 'endDateFormat']
    df = input_df

    # required_columns = ['customerId', 'contractId', 'contractStartDate', 'contractEndDate', 'totalContractValue', 'startDateFormat', 'endDateFormat']
    try:
        if not all(col in df.columns for col in required_columns):
            raise ValueError("Columns 'customerId', 'customerName', 'contractId', 'contractStartDate', 'contractEndDate', 'totalContractValue', 'startDateFormat', and 'endDateFormat' are required columns")
    except:
        st.error("Columns 'customerId', 'customerName', 'contractId', 'contractStartDate', 'contractEndDate', 'totalContractValue', 'startDateFormat', and 'endDateFormat' are required columns")
        return False
    
    # Check if 'customeId' column has a value for all rows
    if not df['customerId'].notna().all():
        st.error("Not all rows have values in the 'customerID' column.")
        return False

    # Check if 'customeName' column has a value for all rows
    if not df['customerName'].notna().all():
        st.error("Not all rows have values in the 'customerName' column.")
        return False


    # Validate date formats in 'contractStartDate' and 'contractEndDate'

    # Convert the date formats to pandas date format 
    df['startDateFormat'] = df['startDateFormat'].map(PREDEFINED_DATE_FORMAT_MAP)
    df['endDateFormat'] = df['endDateFormat'].map(PREDEFINED_DATE_FORMAT_MAP)


    # Use pd.to_datetime to validate and convert the 'startDate' column
    try:
        df['contractStartDate'] = df.apply(lambda row: pd.to_datetime(row['contractStartDate'], format=row['startDateFormat'], errors='coerce'), axis=1)
        if df['contractStartDate'].isna().any():
            raise ValueError("Invalid date format in 'contractStartDate' column for the selected format")
    except:
        st.error("Invalid date format in 'contractStartDate' column for the selected format")
        return False

    # Use pd.to_datetime to validate and convert the 'startDate' column
    try:
        df['contractEndDate'] = df.apply(lambda row: pd.to_datetime(row['contractEndDate'], format=row['endDateFormat'], errors='coerce'), axis=1)
        if df['contractEndDate'].isna().any():
            raise ValueError("Invalid date format in 'contractEndDate' column for the selected format")
    except:
        st.error("Invalid date format in 'contractEndDate' column for the selected format")
        return False
        
    # Calculate the contract duration in months
    df['contractDuration'] = (df['contractEndDate'] - df['contractStartDate']).dt.days 


    # add an row_id column for reference during overlap override 

    df['rowId']  = df.index

    # Validate contract duration
    try:
        valid_contract_duration = df['contractDuration'] > 0
        print(valid_contract_duration)
        if not valid_contract_duration.all():
            raise ValueError("Invalid contract duration. 'contractEndDate' should be later than 'contractStartDate'.")
    except:
        st.error("Invalid contract duration. 'contractEndDate' should be later than 'contractStartDate'.")
        return False
    
    # Validate contract value column
    try:
        if not pd.to_numeric(df['totalContractValue'], errors='coerce').notna().all():
            raise ValueError("Invalid 'totalContractValue'. It must contain numeric values.")
    except: 
        st.error("Invalid 'totalContractValue'. It must contain numeric values.")
        return False
    return True

def validate_mapping(column_names, predefined_date_formats, df):

    # Check all the columns have been mapped
    invalid_column_names = df[~df['columnNames'].isin(column_names)]
    if not invalid_column_names.empty:
        st.error("Please complete column mapping")
        return False

    # Check the dateformat 
    invalid_date_formats = df[
        ((df['columnHeaders'] == 'contractStartDate') | (df['columnHeaders'] == 'contractEndDate')) &
        ~df['dateFormat'].isin(predefined_date_formats)    ]

    if not invalid_date_formats.empty:
        st.error("Please select date format for date fields")
        return False

    return True


def convert_contract_dates_to_str(input_df):
    """
    converts the dates to string 
    """
    df= input_df.copy()

    # Use pd.to_datetime to validate and convert the 'startDate' column
    try:

        df['contractStartDate'] = df.apply(
            lambda row: row['contractStartDate'].strftime(row['startDateFormat']), axis=1)
       
        df['contractEndDate'] = df.apply(
            lambda row: row['contractEndDate'].strftime(row['endDateFormat']), axis=1)
        
    except Exception as e:
        print(f"An error occurred: {e}")

    return df

def convert_contract_dates_to_date(input_df):
    """
    converts the string dates to date 
    """
    df = input_df.copy()

    # Use pd.to_datetime to convert the 'contractStartDate' and 'contractEndDate' columns back to datetime
    try:
        df['contractStartDate'] = df.apply(
            lambda row: pd.to_datetime(row['contractStartDate'], format=row['startDateFormat']), axis=1
        )
        df['contractEndDate'] = df.apply(
            lambda row: pd.to_datetime(row['contractEndDate'], format=row['endDateFormat']), axis=1
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        # Handle the exception or return the original DataFrame depending on your requirements

    return df

