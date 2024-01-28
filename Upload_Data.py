import streamlit as st
import pandas as pd
from arr_lib.setup import PREDEFINED_COLUMN_HEADERS
from arr_lib.setup import PREDEFINED_DATE_FORMATS
from arr_lib.arr_analysis import create_monthly_buckets
from arr_lib.arr_analysis import create_arr_metrics
from arr_lib.arr_analysis import create_customer_and_aggregated_metrics
from arr_lib.arr_analysis import reconcile_overrides
from arr_lib.arr_analysis import highlight_positive_negative_cells, decorate_logo_metrics_df
from arr_lib.arr_analysis import apply_overrides
from arr_lib.arr_analysis import stylize_metrics_df, rename_columns
from arr_lib.arr_analysis import find_overlapiing_contracts
from arr_lib.column_mapping_ui import perform_column_mapping
from arr_lib.column_filtering_ui import perform_column_filtering
from arr_lib.styling import BUTTON_STYLE
from arr_lib.styling import MARKDOWN_STYLES
from arr_lib.styling import GLOBAL_STYLING
from streamlit_extras.app_logo import add_logo


# on_change callback for file upload 
def clear_session_cb ():
    for key in st.session_state.keys():
        del st.session_state[key]

def main():

    st.set_page_config(page_title="ARR Analysis" , layout='wide')
    #st.image('insight_logo.png', use_column_width=False)
    st.header("Analyze Annual Recurring Revnue (ARR)")


    st.markdown(BUTTON_STYLE, unsafe_allow_html=True)
    st.markdown(MARKDOWN_STYLES, unsafe_allow_html=True)
    st.markdown(GLOBAL_STYLING, unsafe_allow_html=True)


    # add app log 
    # add_logo("insight2_logo.png")
    
    # Initialize file upload details 
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
        st.session_state.df = pd.DataFrame()
        print('getting wiped')


    # Intialize few flags 
    if 'prepare_ai_data' not in st.session_state:  
        st.session_state.prepare_ai_data = "False"          

    # upload files
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], on_change = clear_session_cb)
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.session_state.df = df
        st.session_state.uploaded_file = uploaded_file       
  
    # Conitnue processing is uploaded data is available 
    df = st.session_state.df
    if not df.empty:
        # Display mapped data 
        with st.expander('Show/Hide uploaded raw data', expanded=True):
            st.subheader('Uploaded Data :', divider='green') 
            st.write(df)

        st.markdown("<br>", unsafe_allow_html=True)



        # -------------------------------------------------------------------------------
        # Step 1: Filter Data
        # -------------------------------------------------------------------------------
        # initialize mapped_df
        if 'filtered_df' not in st.session_state:
                st.session_state.filtered_df = pd.DataFrame()
        # # initialize validation status
        if 'column_filtering_status' not in st.session_state:
                st.session_state.column_filtering_status = False
                
        with st.expander("Show/Hide Column filtering", expanded=True): 
            st.subheader("Filter Data :", divider='green') 
            filtered_df, filtering_status = perform_column_filtering(df)

        # -------------------------------------------------------------------------------
        # Step 2: Display filtered df
        # -------------------------------------------------------------------------------
        #            
        filtered_df = st.session_state.filtered_df
        if not filtered_df.empty: 
            with st.expander("Show/Hide Filtered data  ", expanded=True): 
                st.subheader("Filtered Data :", divider='green') 
                st.dataframe(filtered_df)
        st.markdown("<br>", unsafe_allow_html=True)


        # -------------------------------------------------------------------------------
        # Step 3: Column Mapping and Validation Section 
        # -------------------------------------------------------------------------------

        filtered_df = st.session_state.filtered_df

        if 'mapped_df' not in st.session_state:
            st.session_state.mapped_df = pd.DataFrame()
        # # initialize validation status
        if 'column_mapping_status' not in st.session_state:
                st.session_state.column_mapping_status = False

        if (not filtered_df.empty) and st.session_state.column_filtering_status:
        # initialize mapped_df
            # Map file column names based on mapped columns and validate content     
            with st.expander('Show/Hide Column mapping', expanded=True):
                mapped_df, column_mapping_status = perform_column_mapping(PREDEFINED_COLUMN_HEADERS, PREDEFINED_DATE_FORMATS, filtered_df)  
                st.session_state.column_mapping_status = column_mapping_status
                st.session_state.mapped_df =  mapped_df

        mapped_df = st.session_state.mapped_df

        # -------------------------------------------------------------------------------        
        # Step 4: Display mapped uploaded data 
        # -------------------------------------------------------------------------------

        if (not mapped_df.empty) and st.session_state.column_mapping_status:

            # Display mapped data 
            with st.expander('Show/Hide mapped data', expanded=True):
                st.subheader("Mapped Data :", divider='green') 
                st.dataframe(st.session_state.mapped_df, use_container_width=False)

            st.markdown("<br><br>", unsafe_allow_html=True)

        # -------------------------------------------------------------------------------        
        # Step 5: Overlapping contracts
        # -------------------------------------------------------------------------------

        if 'overlapiing_contracts_df' not in st.session_state:
            st.session_state.overlapiing_contracts_df = pd.DataFrame()

        if (not mapped_df.empty) and st.session_state.column_mapping_status:

            # Display mapped data 
            with st.expander('Show/Hide overlapping contract', expanded=True):
                st.subheader("Overlapping contract :", divider='green') 
                overlapiing_contracts_df = find_overlapiing_contracts(mapped_df)
                st.session_state.overlapiing_contracts_df = overlapiing_contracts_df
                st.dataframe (overlapiing_contracts_df)

            st.markdown("<br><br>", unsafe_allow_html=True)

        # -------------------------------------------------------------------------------        
        # Step 6: Navigate to Analyze Page
        # -------------------------------------------------------------------------------

        if (not mapped_df.empty) and st.session_state.column_mapping_status:


            if st.button("Analyze ARR Data"):
                st.switch_page("pages/1_Analyze_Data.py")



if __name__ == "__main__":
    main()


