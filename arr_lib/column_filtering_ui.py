import streamlit as st
import pandas as pd
from arr_lib.column_mapping import map_columns
from arr_lib.arr_validations import validate_input_data
from arr_lib.arr_validations import validate_mapping
import os


# column mapper with dateformat picker
def perform_column_filtering(input_df):

    df = input_df.copy()


    # Function to check if a column is numeric
    def is_numeric_column(df, col):
        return pd.api.types.is_numeric_dtype(df[col])

    # Function to infer if a column is a date column
    def infer_date_column(df, col, sample_size=100):
        if is_numeric_column(df, col):
            return False  # Numeric columns are not date columns
        non_null_data = df[col].dropna()
        sample_size = min(sample_size, len(non_null_data))
        sample = non_null_data.sample(sample_size)
        try:
            pd.to_datetime(sample)
            return True
        except (ValueError, TypeError):
            return False

    # Function to get min/max dates from a date column
    def get_date_range(df, col):
        try:
            date_col = pd.to_datetime(df[col].dropna())
            min_date = date_col.min()
            max_date = date_col.max()
            return min_date, max_date
        except Exception:
            return None, None

    # Function to convert date columns to datetime
    def convert_date_columns(df, date_columns):
        for col in date_columns:
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass
        return df

    # Function to filter the dataframe
    def filter_dataframe(df, column_filters, date_filters, exclusion_filters, numeric_filters):
        for col, values in column_filters.items():
            df = df[df[col].isin(values)]

        for col, values in exclusion_filters.items():
            df = df[~df[col].isin(values)]

        for col, (start_date, end_date) in date_filters.items():
            if start_date:
                df = df[df[col] >= pd.Timestamp(start_date)]
            if end_date:
                df = df[df[col] <= pd.Timestamp(end_date)]

        for col, num_range in numeric_filters.items():
            if num_range:
                min_val, max_val = num_range
                df = df[(df[col] >= min_val) & (df[col] <= max_val)]

        return df



    # Convert date columns to datetime
    date_columns = [col for col in df.columns if infer_date_column(df, col)]
    df = convert_date_columns(df, date_columns)

    col1, col2 = st.columns([2, 3], gap="medium")

    with col1:
        st.markdown(f"#### Select columns to filter")
        columns_to_filter = st.multiselect(" ", df.columns, placeholder="Select columns to filter", key="select-filter-main-1")

    column_filters = {}
    date_filters = {}
    exclusion_filters = {}
    numeric_filters = {}

    with col2:
        for col in columns_to_filter:
            if is_numeric_column(df, col):
                st.markdown(f"###### {col}")
                min_val, max_val = df[col].min(), df[col].max()
                num_range = st.slider(f"Select range for {col}", min_val, max_val, (min_val, max_val), key=f"{col}_num_range")
                numeric_filters[col] = num_range
                st.markdown(f"Current range: {num_range[0]:,.2f} - {num_range[1]:,.2f}")
            elif col in date_columns:
                min_date, max_date = get_date_range(df, col)
                st.markdown(f"###### {col}")
                col_from, col_to = st.columns(2)
                with col_from:
                    from_date = st.date_input(f"From date for {col}", value=min_date, key=f"{col}_from_date")
                with col_to:
                    to_date = st.date_input(f"To date for {col}", value=max_date, key=f"{col}_to_date")
                date_filters[col] = (from_date, to_date)
            else:
                st.markdown(f"###### {col}")
                col_inc, col_exc = st.columns(2)
                with col_inc:
                    selected_values_include = st.multiselect(f"Include {col}", df[col].dropna().unique(), key=f"{col}_inc")
                    if selected_values_include:
                        column_filters[col] = selected_values_include
                with col_exc:
                    selected_values_exclude = st.multiselect(f"Exclude {col}", df[col].dropna().unique(), key=f"{col}_exc")
                    if selected_values_exclude:
                        exclusion_filters[col] = selected_values_exclude

            st.markdown("---")  # Separator



    if st.button(" Filter Uploaded Data "):
        filtered_df = filter_dataframe(df, column_filters, date_filters, exclusion_filters, numeric_filters)
        filtering_status = True 
        st.session_state.column_filtering_status = filtering_status
        st.session_state.filtered_df = filtered_df

        return filtered_df, filtering_status
    else: 
        return pd.DataFrame(), False