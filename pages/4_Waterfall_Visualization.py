import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
import pandas as pd
import altair as alt
from pandas.tseries.offsets import MonthEnd
from datetime import datetime, timedelta

from arr_lib.print_logos import print_logos
from streamlit_extras.app_logo import add_logo
from streamlit_dimensions import st_dimensions


from arr_lib.styling import BUTTON_STYLE
from arr_lib.styling import MARKDOWN_STYLES
from arr_lib.styling import GLOBAL_STYLING

import arr_lib.arr_visualize as av
import arr_lib.arr_charts as ac

from dotenv import load_dotenv
import os


st.header("Visualize ARR Waterfall")
st.markdown("<br>", unsafe_allow_html=True)

load_dotenv()

print_logos()


if 'metrics_df' not in st.session_state: 
    metrics_df = pd.DataFrame()
else:
    # copy uploaded ARR metrics from session 
    metrics_df = st.session_state.metrics_df.copy()
    customer_arr_waterfall_df = st.session_state.customer_arr_waterfall_df.copy()
    customer_arr_df = st.session_state.customer_arr_df.copy()
    logo_metrics_df = st.session_state.logo_metrics_df.copy()

if 'replan_metrics_df' not in st.session_state: 
    replan_metrics_df = pd.DataFrame()
else: 
    # copy adjusted ARR metrics from session 
    replan_metrics_df = st.session_state.replan_metrics_df.copy()
    replan_customer_arr_waterfall_df = st.session_state.replan_customer_arr_waterfall_df.copy()
    replan_customer_arr_df = st.session_state.replan_customer_arr_df.copy()
    replan_logo_metrics_df = st.session_state.replan_logo_metrics_df.copy()

if (metrics_df.empty or replan_metrics_df.empty): 
    st.error('Please generate ARR metrics')
    st.stop()

#chart_width = av.chart_width('main')

chart_width = 1100


## ARR waterfall chart 
st.markdown("<br>", unsafe_allow_html=True)
st.subheader('ARR Waterfall Analysis ')
arr_wf_tab1, arr_wf_tab2= st.tabs(["Adjusted Values", "Uploaded Values"])
with arr_wf_tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    date_selector_1 = st.date_input('Select end date for Waterfall analysis ', key="wf_dt_1")
    with st.spinner("Generating ARR Waterfall ..."):
        df1 = av.prepare_waterfall_data(replan_metrics_df, date_selector_1)
        agg_arr_wf_chart_replan = ac.create_waterfall_chart(df1, chart_width)
        st.altair_chart(agg_arr_wf_chart_replan, theme="streamlit", use_container_width=False)

        # st.dataframe(df1, use_container_width=True)

with arr_wf_tab2: 
    st.markdown("<br>", unsafe_allow_html=True)
    date_selector_2 = st.date_input('Select end date for Waterfall analysis ', key="wf_dt_2")
    with st.spinner("Generating ARR Waterfall ..."):
        df2 = av.prepare_waterfall_data(metrics_df, date_selector_2)
        agg_arr_wf_chart = ac.create_waterfall_chart(df2, chart_width)
        st.altair_chart(agg_arr_wf_chart, theme="streamlit", use_container_width=False)

        # st.dataframe(df2, use_container_width=True)






st.markdown(BUTTON_STYLE, unsafe_allow_html=True)
st.markdown(MARKDOWN_STYLES, unsafe_allow_html=True)
st.markdown(GLOBAL_STYLING, unsafe_allow_html=True)






