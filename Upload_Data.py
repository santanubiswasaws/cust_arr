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
from arr_lib.arr_analysis import find_overlapiing_contracts, override_dfs, create_acv_analysis, rename_contract_columns
from arr_lib.arr_validations import convert_contract_dates_to_str
from arr_lib.column_mapping_ui import perform_column_mapping
from arr_lib.column_filtering_ui import perform_column_filtering
from arr_lib.styling import BUTTON_STYLE
from arr_lib.styling import MARKDOWN_STYLES
from arr_lib.styling import GLOBAL_STYLING
from streamlit_extras.app_logo import add_logo
from dotenv import load_dotenv
import os


# on_change callback for file upload 
def clear_session_cb ():
    for key in st.session_state.keys():
        del st.session_state[key]

def main():

    st.set_page_config(page_title="ARR Analysis" , layout='wide')
    st.header("Analyze Annual Recurring Revnue (ARR)")


    st.markdown(BUTTON_STYLE, unsafe_allow_html=True)
    st.markdown(MARKDOWN_STYLES, unsafe_allow_html=True)
    st.markdown(GLOBAL_STYLING, unsafe_allow_html=True)


    load_dotenv()

    APP_LOGO = os.getenv("APP_LOGO")
    if not ( APP_LOGO is None):
        add_logo(APP_LOGO)

    CUST_LOGO = os.getenv("CUST_LOGO")
    if not ( CUST_LOGO is None):
        CUST_LOGO = st.secrets["CUST_LOGO"]
        if not ( CUST_LOGO is None):
            st.sidebar.image(CUST_LOGO, use_column_width=False)

    st.write(st.secrets)
    
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
            filtered_df, column_filtering_status = perform_column_filtering(df)
            # st.session_state.filtered_df = filtered_df
            # st.session_state.column_filtering_status = column_filtering_status

        # -------------------------------------------------------------------------------
        # Step 2: Display filtered df
        # -------------------------------------------------------------------------------
        #            
        filtered_df = st.session_state.filtered_df
        column_filtering_status = st.session_state.column_filtering_status

        if not filtered_df.empty: 
            with st.expander("Show/Hide Filtered data  ", expanded=True): 
                st.subheader("Filtered Data :", divider='green') 
                st.dataframe(filtered_df)
        st.markdown("<br>", unsafe_allow_html=True)


        # -------------------------------------------------------------------------------
        # Step 3: Column Mapping and Validation Section 
        # -------------------------------------------------------------------------------


        if 'mapped_df' not in st.session_state:
            st.session_state.mapped_df = pd.DataFrame()

        if 'raw_mapped_df' not in st.session_state:
            st.session_state.raw_mapped_df = pd.DataFrame()

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
        raw_mapped_df = st.session_state.raw_mapped_df

        # -------------------------------------------------------------------------------        
        # Step 4: Display mapped uploaded data 
        # -------------------------------------------------------------------------------

        if (not mapped_df.empty) and st.session_state.column_mapping_status:

            # Display mapped data 
            with st.expander('Show/Hide mapped data', expanded=True):
                st.subheader("Mapped Data :", divider='green') 
                st.dataframe(st.session_state.raw_mapped_df, use_container_width=False)

            st.markdown("<br><br>", unsafe_allow_html=True)


        # -------------------------------------------------------------------------------        
        # Step 5: Overlapping contracts
        # -------------------------------------------------------------------------------

        if 'overlapiing_contracts_df' not in st.session_state:
            st.session_state.overlapiing_contracts_df = pd.DataFrame()

        if 'overlapping_contracts_queried' not in st.session_state:
            st.session_state.overlapping_contracts_queried = False
        # -------------------------------------------------------------------------------        
        # Step 5a: Find overlapping contracts
        # -------------------------------------------------------------------------------        

        if (not mapped_df.empty) and st.session_state.column_mapping_status:

            st.subheader("Overlapping contracts :", divider='green') 
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2 = st.columns (2)
            with col1:
                overlap_days_filter = st.slider('How many days overlap do you want to find?', 0, 30 , 15)

            if st.button(f"Find Contracts Overlapping {overlap_days_filter} days"):    
                st.session_state.overlapping_contracts_queried = True           
                overlapiing_contracts_df = find_overlapiing_contracts(raw_mapped_df, overlap_days_filter)
                st.session_state.overlapiing_contracts_df = overlapiing_contracts_df

         # -------------------------------------------------------------------------------        
        # Step 5b: Display overlapping Contracts
        # -------------------------------------------------------------------------------                  
        overlapiing_contracts_df = st.session_state.overlapiing_contracts_df

        if 'edited_overlapping_contracts_df' not in st.session_state:
            st.session_state.edited_overlapping_contracts_df = pd.DataFrame()

        if 'apply_overlap_changes' not in st.session_state:
            st.session_state.apply_overlap_changes = False

        if st.session_state.overlapping_contracts_queried and st.session_state.column_mapping_status:

            if not overlapiing_contracts_df.empty :
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("###### Adjust overlapping contracts ")

                # display_overlap_df = convert_contract_dates_to_str(overlapiing_contracts_df)

                edited_overlapping_contracts_df = st.data_editor(overlapiing_contracts_df, 
                                disabled = ('customerId', 'customerName', 'totalContractValue', 'startDateFormat', 'endDateFormat', 'rowId'), 
                                key="edit_ovelapping_ctracts")

                st.session_state.edited_overlapping_contracts_df = edited_overlapping_contracts_df
                # st.markdown("<br><br>", unsafe_allow_html=True)

                st.session_state.apply_overlap_changes = st.checkbox('Apply these changes to uploaded data: ', value = st.session_state.apply_overlap_changes)


            else: 
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("###### No overlapping contracts found !")


        # -------------------------------------------------------------------------------        
        # Step 6: Generate ACV & Booking Details 
        # -------------------------------------------------------------------------------

        if 'acv_df' not in st.session_state:
            st.session_state.acv_df = pd.DataFrame()


        if 'overlap_override_df' not in st.session_state:
            st.session_state.overlap_override_df = pd.DataFrame()
        
        if 'acv_button_clicked' not in st.session_state:
            st.session_state.acv_button_clicked = False

        if (not mapped_df.empty) and st.session_state.column_mapping_status:
                       
            st.markdown("<br>", unsafe_allow_html=True) 
            if st.button("Generate ACV Bookings Details"):

                edited_overlapping_contracts_df = st.session_state.edited_overlapping_contracts_df
                if st.session_state.apply_overlap_changes and (not edited_overlapping_contracts_df.empty):
                    overlap_override_df = override_dfs(mapped_df, edited_overlapping_contracts_df, 'rowId') 
                else:
                    overlap_override_df = mapped_df.copy()

                st.session_state.overlap_override_df = overlap_override_df
                acv_df = create_acv_analysis(overlap_override_df)               
                st.session_state.acv_df = acv_df



        # -------------------------------------------------------------------------------        
        # Step 7: Display ACV details 
        # -------------------------------------------------------------------------------

        st.markdown("<br><br>", unsafe_allow_html=True) 
        acv_df = st.session_state.acv_df

        if (not acv_df.empty):

            # Display mapped data 
            with st.expander('Show/Hide TCV and ACV details', expanded=True):
                st.subheader("TCV and ACV Details :", divider='green') 

                display_acv_df = rename_contract_columns(st.session_state.acv_df)
            
                st.dataframe(display_acv_df, use_container_width=False)


        # -------------------------------------------------------------------------------        
        # Step 8: Navigate to Analyze Page
        # -------------------------------------------------------------------------------

        if (not mapped_df.empty) and st.session_state.column_mapping_status:
                        
            st.markdown("<br><br>", unsafe_allow_html=True) 

            if st.button("Analyze Customer MRR and ARR Data"):
                st.switch_page("pages/1_Analyze_Data.py")



if __name__ == "__main__":
    main()


