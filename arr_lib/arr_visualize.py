import streamlit as st
import pandas as pd
import altair as alt
from pandas.tseries.offsets import MonthEnd
from datetime import datetime, timedelta
from streamlit_dimensions import st_dimensions


def get_list_of_months(df, descending):
    """
    Given a dataframe with a column name called months - returns distinct months 
    """
    inpput_df = df.copy()

    # Melting the DataFrame
    inpput_df = inpput_df.melt(id_vars='measureType', var_name='month', value_name='value')

    # Sorting the unique months
    month_columns = sorted(inpput_df['month'].unique(), reverse = descending)

    # Calculate last month based on today's date
    today = datetime.today()
    first_day_of_this_month = today.replace(day=1)
    last_month_end = first_day_of_this_month - timedelta(days=1)
    last_month = last_month_end.strftime("%Y-%m")

    # Check if last_month is in the list of months, otherwise use the last available month
    last_month = last_month if last_month in month_columns else month_columns[-1]

    return month_columns,last_month

@st.cache_data
def get_core_arr_metrics (df_agg, df_logo, selected_month): 
    """
    Calculate the following metrics 

    1. ARR and growth over last 12 monhts 
    2. New Logo and growith over last 12 months 
    3. Churned Logo and rate of change over last 12 months 
    4. Net Retention Rate 
    5. Gross Retention Rate 

    @todo -  make the display structure dynamic - so that just by adding new metrics to the structure - it can be rendered automatically 
    """


    input_df_agg = df_agg.copy()
    input_df_agg = input_df_agg.melt(id_vars='measureType', var_name='month', value_name='value')
    filtered_data = input_df_agg[input_df_agg['month'] == selected_month].fillna(0) 

    # Get the current date to calculate the last 12 and 24 months
    selected_month_date = pd.to_datetime(selected_month) + MonthEnd(0)

    inpput_df_logo = df_logo.copy()
    logo_df = inpput_df_logo.melt(id_vars='measureType', var_name='month', value_name='value')
    logo_df['month'] = pd.to_datetime(logo_df['month']) + MonthEnd(0)

    # ARR metrics 
    arr = filtered_data.loc[(filtered_data['month'] == selected_month) & (filtered_data['measureType'] == 'monthlyRevenue'), 'value'].values[0] 
    arr= arr / 1000 
    arr = "{:,.0f}".format(arr)

    arr_growth = filtered_data.loc[(filtered_data['month'] == selected_month) & (filtered_data['measureType'] == 'yearlyRevenueGrowth'), 'value'].values[0] 
    arr_growth *= 100
    arr_growth = "{:,.2f}%".format(arr_growth)

    # Customer Count Metrics    
    # Filter for 'monthlyBusinessLogo'
    cust_count = logo_df[logo_df['measureType'] == 'newBusinessLogo']

    sum_last_12_months = cust_count[(cust_count['month'] <= selected_month_date) & 
                                    (cust_count['month'] > selected_month_date - pd.DateOffset(months=12))]['value'].sum()

    sum_last_24_months = cust_count[(cust_count['month'] <= selected_month_date) & 
                                    (cust_count['month'] > selected_month_date - pd.DateOffset(months=24))]['value'].sum()

    logo_growth = ( sum_last_12_months * 100 / (sum_last_24_months - sum_last_12_months) ) 
    logo_cnt = "{:,.0f}".format(sum_last_12_months)
    logo_growth = "{:,.2f}%".format(logo_growth)



    # Churn customer Metrics 
    # Filter for 'churnLogo'
    churn_count = logo_df[logo_df['measureType'] == 'churnLogo']

    # Get the current date to calculate the last 12 and 24 months

    churn_last_12_months = churn_count[(churn_count['month'] <= selected_month_date) & 
                                    (churn_count['month'] > selected_month_date - pd.DateOffset(months=12))]['value'].sum()

    churn_last_24_months = churn_count[(churn_count['month'] <= selected_month_date) & 
                                    (churn_count['month'] > selected_month_date - pd.DateOffset(months=24))]['value'].sum()

    churn_growth = ( churn_last_12_months * 100 / (churn_last_24_months - churn_last_12_months) ) 
    churn_cnt = "{:,.0f}".format(churn_last_12_months)
    churn_growth = "{:,.2f}%".format(churn_growth)


    # Net retention 
    nr = filtered_data.loc[(filtered_data['month'] == selected_month) & (filtered_data['measureType'] == 'netRetentionRate'), 'value'].values[0] 
    if not nr:
        nr = 0
    nr *= 100 
    nr = "{:,.2f}%".format(nr)

    # Gross retention 
    gr = filtered_data.loc[(filtered_data['month'] == selected_month) & (filtered_data['measureType'] == 'grossRetentionRate'), 'value'].values[0] 
    gr *= 100
    gr = "{:,.2f}%".format(gr)

    return arr, arr_growth, logo_cnt, logo_growth, churn_cnt, churn_growth, nr, gr 

@st.cache_data
def prepare_waterfall_data(input_df, date_selector):

    df = input_df.copy()

    df = pivot_arr_df(df)
    df = get_last_n_period_data(df, date_selector)
    df = df.rename(columns={'month': 'period'})  

    df['nb_end'] = df['preRev'] + df['newBusiness']

    # Add the 'ex_end' column as the sum of 'nb_end' and 'upSell'
    df['ex_end'] = df['nb_end'] + df['upSell']

    # Add the 'cnt_end' column as the sum of 'ex_end' and 'downSell'
    df['cnt_end'] = df['ex_end'] + df['downSell']

    # Add the 'churn_end' column as the sum of 'cnt_end' and 'churn'
    df['churn_end'] = df['cnt_end'] + df['churn']

    # Adding End Period 
    closing_period_data = df.iloc[-1]
    # Sample row data for 'End Period'
    end_period_row = pd.DataFrame({
        'period': ['End Period'],
        'preRev': [closing_period_data['curRev']],
        'curRev': [closing_period_data['curRev']]
        # 'churn_offset': [closing_period_data['churn_offset']]
        # Include other necessary columns here
    })
    # Append the 'End Period' 
    df = pd.concat([df, end_period_row], ignore_index=True)


    min_val = df['curRev'].min()
    padding = (df['curRev'].max() - min_val) * 0.05  # Adjust padding as needed
    
    df['startFromY'] = (min_val - padding)

    df['lead_period'] = df['period'].shift(-1).ffill()


    df['curMid'] = df['curRev'] / 2
    df['preMid'] = df['preRev'] / 2


    # Create boolean masks for non-zero values in each category
    has_newBusiness = df['newBusiness'] != 0
    has_upSell = df['upSell'] != 0
    has_downSell = df['downSell'] != 0
    has_churn = df['churn'] != 0

    # Convert boolean masks to integers (0 or 1)
    newBusiness_int = has_newBusiness.astype(int)
    upSell_int = has_upSell.astype(int)
    downSell_int = has_downSell.astype(int)
    churn_int = has_churn.astype(int)

    # Calculate cumulative offsets for each category
    # Each offset is based on the presence of the previous categories
    df['nb_offset'] = 10 * newBusiness_int
    df['ex_offset'] = df['nb_offset'] + 10 * upSell_int
    df['cnt_offset'] = df['ex_offset'] + 10 * downSell_int
    df['churn_offset'] = df['cnt_offset'] + 10 * churn_int

    return df
 
@st.cache_data
def pivot_arr_df(input_df):

    df = input_df.copy()

        # melt the dataframe for better query results 
    melted_metrics_df = df.melt(id_vars=['measureType'], 
                        var_name='month', 
                        value_name='amount')


    # vidide the amounts with 12 - as it is annualized
    melted_metrics_df['amount'] = melted_metrics_df['amount'] / 1000

    # Splitting the 'YearMonth' into 'Year' and 'Month'
    split_columns_agg = melted_metrics_df['month'].str.split('-', expand=True)
    melted_metrics_df['year'] = split_columns_agg[0]
    melted_metrics_df['monthOfYear'] = split_columns_agg[1]

    # Filter the DataFrame for specific measureType values
    filtered_df_1 = melted_metrics_df[melted_metrics_df['measureType'].isin(['lastMonthRevenue', 'monthlyRevenue', 'newBusiness', 'upSell', 'downSell', 'churn'])]

    filtered_df_1['measureType'] = filtered_df_1['measureType'].replace('monthlyRevenue', 'curRev')
    filtered_df_1['measureType'] = filtered_df_1['measureType'].replace('lastMonthRevenue', 'preRev')
    # Using pivot_table on the filtered DataFrame
    pivoted_agg_df = filtered_df_1.pivot_table(index=['month', 'year', 'monthOfYear'], 
                                        columns='measureType', 
                                        values='amount',
                                        aggfunc='first').fillna(0)
      
    # Resetting the index to turn the indexes back into columns
    pivoted_agg_df.reset_index(inplace=True)

    return pivoted_agg_df

@st.cache_data
def get_last_n_period_data(input_df, given_date=None): 

    df = input_df
   # first get the current_month  
    if given_date is None:
        given_date = datetime.now()
    elif isinstance(given_date, str):
        given_date = pd.to_datetime(given_date)
    date_str = given_date.strftime('%Y-%m')

    # filter data 
    df = df[df['month'] <= date_str]
    df = df.sort_values(by='month')

    return df.tail(13)

@st.cache_data
def chart_width(key):
    dimension_data = st_dimensions(key=key)

    try:
        chart_width = int(dimension_data["width"] * 0.93)
    except: 
        chart_width = int(1100)

    return chart_width