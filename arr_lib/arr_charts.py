import streamlit as st
import pandas as pd
import altair as alt

from arr_lib.styling import BUTTON_STYLE
from arr_lib.styling import MARKDOWN_STYLES
from arr_lib.styling import GLOBAL_STYLING

from arr_lib import styling as style




def arr_walk_chart(metrics_df, bar_color, chart_title): 
    """
    generate and return an altair chart - for customer ARR walk 
    """
    # Check if 'Total_Sales' column exists, and drop it if it does
    if 'Total_Sales' in metrics_df.columns:
        metrics_df = metrics_df.drop(columns=['Total_Sales'])

    # Running ARR charts 
    melted_metrics_df = pd.melt(metrics_df, id_vars=['measureType'], var_name='month', value_name='ARR')

    arr_df = melted_metrics_df[melted_metrics_df['measureType']=='monthlyRevenue']
    # Convert 'month' to datetime and extract year and quarter
    arr_df['month'] = pd.to_datetime(arr_df['month'])
    arr_df['quarter'] = arr_df['month'].dt.year.astype(str) + '-Q' + arr_df['month'].dt.quarter.astype(str)

    # Group by quarter and sum/average the ARR
    #quarterly_data = arr_df.groupby('quarter')['ARR'].mean().reset_index()


    # Filter to keep only the third month of each quarter
    third_months = arr_df[arr_df['month'].dt.month.isin([3, 6, 9, 12])]

    # Group by quarter and take the value of the third month
    quarterly_data = third_months.groupby('quarter')['ARR'].last().reset_index()



    # Transform and scale the ARR values to thousands for the bar chart
    bar_chart = alt.Chart(quarterly_data).transform_calculate(
        scaled_arr="datum.ARR / 1000"  # Scaling the ARR to thousands
    ).mark_bar(color=bar_color, cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X('quarter', title=None),
        y=alt.Y('scaled_arr:Q', title="Quarterly ARR (in Thousands) ", axis=alt.Axis(format=',.0f')) 
    )

    # Create the text layer for labels, using the same scaled values
    text_chart = bar_chart.mark_text(
        align='left',
        baseline='middle',
        angle=270,  # Rotate the text by 270 degrees
        dx=3,  # Horizontal offset
        dy=-5,  # Vertical offset
        fontSize=12,
        color='gray'
    ).encode(
        x='quarter',
        y='scaled_arr:Q',  # Use scaled ARR for positioning text
        text=alt.Text('scaled_arr:Q', format=',.0f')  # Display scaled ARR
    )

    # Layer the text and the bar chart
    arr_walk_chart = alt.layer(bar_chart, text_chart).properties(
        title=chart_title,
        width=1100,
        height=400,
        padding= {"bottom": 15, "top":20, "left": 15, "right": 15}
    ).configure(
    background="#F5F8F8" # Set the background color
    ).configure_title(
        fontSize=14,
        fontWeight='normal', 
        anchor='middle',
        orient='bottom', 
        color='gray'
    ).configure_axis(
        gridColor='#e0e0e0'  # Set grid line color
    )

    return arr_walk_chart



def cust_count_chart(df, chart_color, chart_title): 
       
    # Check if 'Total_Sales' column exists, and drop it if it does
    if 'Total_Sales' in df.columns:
        df = df.drop(columns=['Total_Sales'])

        # Running Customer Count 
    melted_count_df = pd.melt(df, id_vars=['measureType'], var_name='month', value_name='customerCount')

    count_df = melted_count_df[melted_count_df['measureType']=='monthlyRevenueLogo']

    # Transform and scale the ARR values to thousands for the bar chart
    cust_count_result = alt.Chart(count_df).mark_bar(color=chart_color, size=9, cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=alt.X('month:T', axis=alt.Axis(title=None, labelAngle=270, labelOverlap=True)),
        y=alt.Y('customerCount:Q', title="Monthly Count ", axis=alt.Axis(format=',.0f')) 
    ).properties(
        title=chart_title,
        width=1100,
        height=350,
        padding= {"bottom": 15, "top":20, "left": 15, "right": 15}
    ).configure(
        background="#F5F8F8" # Set the background color
    ).configure_title(
        fontSize=14,
        fontWeight='normal',
        anchor='middle',
        orient='bottom', 
        color='gray'
    ).configure_axis(
        gridColor='#e0e0e0'  # Set grid line color
    )

    return cust_count_result


def cust_count_waterfall_chart(df,  chart_title): 

     
    # Check if 'Total_Sales' column exists, and drop it if it does
    if 'Total_Sales' in df.columns:
        df = df.drop(columns=['Total_Sales'])
 
    # Running Customer Count 
    melted_count_df = pd.melt(df, id_vars=['measureType'], var_name='month', value_name='customerCount')

    # Calculate min and max values with a bit of padding
    min_count = melted_count_df['customerCount'].min() - (melted_count_df['customerCount'].max() - melted_count_df['customerCount'].min()) * 0.1
    max_count = melted_count_df['customerCount'].max() + (melted_count_df['customerCount'].max() - melted_count_df['customerCount'].min()) * 0.1


    # Assuming df is your DataFrame with columns 'month', 'measureType', and 'customerCount'

    # Define a dictionary for translating category names
    translate_dict = {
        'churnLogo': 'Churn',
        'newBusinessLogo': 'New Logo',
        'lastMonthRevenueLogo': 'Previous Count',
        'monthlyRevenueLogo': 'Monthly Count'
    }

    # Define the color scheme as a dictionary
    color_scheme = {
        'Churn': '#ee7777',
        'New Logo': '#77aaca',
        'Previous Count': 'lightgray',
        'Monthly Count': '#88b988'
    }

    # Apply the translation to the DataFrame
    melted_count_df['translated_measureType'] = melted_count_df['measureType'].map(translate_dict)

    # Create a line chart
    count_wf_chart = alt.Chart(melted_count_df).mark_line(point=True).encode(
        x=alt.X('month:T', axis=alt.Axis(title=None, labelAngle=270, labelOverlap=True)),  # Assuming 'month' is of datetime type; if not, change to 'month:N'
        y=alt.Y('customerCount:Q', axis=alt.Axis(title='Customer Count', format=',.0f'), scale=alt.Scale(domain=(min_count, max_count))),
        color=alt.Color('translated_measureType:N', scale=alt.Scale(domain=list(color_scheme.keys()), range=list(color_scheme.values())), legend=alt.Legend(title=None, orient='top')),  # Position legend at top
        tooltip=['month', 'translated_measureType', 'customerCount']
    ).properties(
        title=chart_title,
        width=1100,
        height=350,
        padding= {"bottom": 15, "top":15, "left": 15, "right": 15}
    ).configure(
        background="#F5F8F8" # Set the background color
    ).configure_title(
        fontSize=14,
        fontWeight='normal',
        anchor='middle',
        orient='bottom', 
        color='gray'
    ).configure_axis(
        gridColor='#e0e0e0'  # Set grid line color
    )
    
    return count_wf_chart


def top_cust_chart(customer_arr_df, bar_color, chart_title): 
    """
    generate and return an altair chart - for customer pareto 
    """

    # Check if 'Total_Sales' column exists, and drop it if it does
    if 'Total_Sales' in customer_arr_df.columns:
        customer_arr_df = customer_arr_df.drop(columns=['Total_Sales'])

    # Create a new column with the sum of monthly sales
    customer_arr_df['Total_Sales'] = customer_arr_df.iloc[:, 2:].sum(axis=1)

    # Sort the DataFrame by 'Total_Sales' in descending order
    customer_arr_df = customer_arr_df.sort_values(by='Total_Sales', ascending=False)

    # Optionally, reset the index if you want the index to be sequential
    top_10_customers = customer_arr_df.head(10)
    top_10_customers = top_10_customers [['customerName', 'Total_Sales']]


    top_bar_chart = alt.Chart(top_10_customers).transform_calculate(
        scaled_tcv="datum.Total_Sales / 1000"  # Scaling the ARR to thousands
    ).mark_bar(color=bar_color, cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X('customerName', title=None, sort=None),
        y=alt.Y('scaled_tcv:Q', title="Total Contract Values (in Thousands)", axis=alt.Axis(format=',.0f'))
    )

        # Create the text layer for labels, with text rotated by 270 degrees
    top_text_chart = top_bar_chart.mark_text(
        align='left',
        baseline='middle',
        angle=270,  # Rotate the text by 270 degrees
        dx=5,  # Adjust this value to position the text correctly with respect to the bar
        dy=-3,  # Adjust this value to position the text correctly on the bar
        fontSize=12,
        color='gray'
    ).encode(
        y='scaled_tcv:Q',  # Use scaled ARR for positioning text
        text=alt.Text('scaled_tcv:Q', format=',.0f')  # Display scaled TCV
    )

    # Layer the text and the bar chart
    top_final_chart = alt.layer(top_bar_chart, top_text_chart).properties(
        title=chart_title,
        width=1100,
        height=500,
        padding= {"bottom": 15, "top":25, "left": 15, "right": 15}
    ).configure(    
        background="#F5F8F8" # Set the background color
    ).configure_title(
        fontSize=14,
        fontWeight='normal', 
        anchor='middle',
        orient='bottom', 
        color='gray'
    ).configure_axis(
        gridColor='#e0e0e0'  # Set grid line color
    )    

    return top_final_chart



def cust_arr_waterfall_chart(df,  chart_title): 

     
    # Check if 'Total_Sales' column exists, and drop it if it does
    if 'Total_Sales' in df.columns:
        df = df.drop(columns=['Total_Sales'])
 
    df = df[df['measureType'] != 'lastMonthRevenue']

    # Running Customer Count 
    melted_arr_df = pd.melt(df, id_vars=['customerId', 'customerName', 'measureType'], var_name='month', value_name='MRR')


    # Calculate min and max values with a bit of padding
    min_mrr = melted_arr_df['MRR'].min() - (melted_arr_df['MRR'].max() - melted_arr_df['MRR'].min()) * 0.1
    max_mrr = melted_arr_df['MRR'].max() + (melted_arr_df['MRR'].max() - melted_arr_df['MRR'].min()) * 0.1


    # Assuming df is your DataFrame with columns 'month', 'measureType', and 'customerCount'

    # Define a dictionary for translating category names
    translate_dict = {
        "lastMonthRevenue" : "Opening ARR",
        "newBusiness" : "New Business",
        "upSell" : "Expansion",
        "downSell" : "Contraction",
        "churn" : "Churn",
        "monthlyRevenue" : "MRR", 
    }

    # Define the color scheme as a dictionary
    color_scheme = {
        "New Business": '#77aaca',
        "Expansion": 'green',
        "Contraction": 'magenta',
        "Churn": '#ee7777',
        "MRR": '#88b988'
    }

    # Apply the translation to the DataFrame
    melted_arr_df['translated_measureType'] = melted_arr_df['measureType'].map(translate_dict)

    # Create a line chart
    arr_wf_chart = alt.Chart(melted_arr_df).mark_line(point=True).encode(
        x=alt.X('month:T', axis=alt.Axis(title=None, labelAngle=270, labelOverlap=True)),  # Assuming 'month' is of datetime type; if not, change to 'month:N'
        y=alt.Y('MRR:Q', axis=alt.Axis(title='Customer MRR', format=',.0f'), scale=alt.Scale(domain=(min_mrr, max_mrr))),
        color=alt.Color('translated_measureType:N', scale=alt.Scale(domain=list(color_scheme.keys()), range=list(color_scheme.values())), legend=alt.Legend(title=None, orient='top')),  # Position legend at top
        tooltip=['month', 'translated_measureType', 'MRR']
    ).properties(
        title=chart_title,
        width=1100,
        height=600,
        padding= {"bottom": 15, "top":25, "left": 15, "right": 15}
    ).configure(    
        background="#F5F8F8" # Set the background color
    ).configure_title(
        fontSize=14,
        fontWeight='normal',
        anchor='middle',
        orient='bottom', 
        color='gray'
    ).configure_axis(
        gridColor='#e0e0e0'  # Set grid line color
    )
    
    return arr_wf_chart






def create_waterfall_chart(input_df, chart_width):
    """
    
    ARR Waterfall chart 
    
    """

    df = input_df.copy()

    min_val = df['curRev'].min()
    padding = (df['curRev'].max() - min_val) * 0.05  # Adjust padding as needed

    common_y_scale = alt.Scale(domainMin=min_val - padding)


    base = alt.Chart(df).encode(
        x=alt.X('period:N', axis=alt.Axis(labelAngle=0, title=None, domain=True, domainColor='black', domainWidth=1, ticks=True, tickWidth=1, tickSize=8))
    )


    # newBusiness bars
    nb_bars = base.transform_filter(
        alt.datum.newBusiness != 0
    ).mark_bar(size=20, color=style.newBusiness_color).encode(
        y=alt.Y('nb_end:Q', scale=common_y_scale, axis=alt.Axis(title="Recurring Revenue", format=',.0f', domain=True, domainColor='black', domainWidth=1, ticks=True, tickWidth=1, tickSize=8)),
        y2='preRev:Q'
    )

    # newBusiness labels with explicit Y positioning
    nb_labels = base.transform_filter(
        alt.datum.newBusiness != 0
    ).mark_text(angle=270, dx=15).encode(
        x='period:N',
        y='nb_end:Q',
        #y=alt.Y('sales_end:Q', axis=alt.Axis(labels=False)),  # Position based on sales_end
        text=alt.Text('newBusiness:Q', format=',.0f')
    )


    # upSell bars without offset (ex_offset == 0)
    upSell_bars_no_offset = base.mark_bar(size=20, color=style.upSell_color, xOffset=0).encode(
        y='ex_end:Q',
        y2='nb_end:Q'
    ).transform_filter(
        (alt.datum.upSell != 0) & (alt.datum.ex_offset == 10)
    )

    # upSell bars with offset (ex_offset == 20)
    upSell_bars_10_offset = base.mark_bar(size=20, color=style.upSell_color, xOffset=20).encode(
        y='ex_end:Q',
        y2='nb_end:Q'
    ).transform_filter(
        (alt.datum.upSell != 0) & (alt.datum.ex_offset == 20)
    )



    # upsell  labels with explicit Y positioning
    upSell_label_no_offset = base.transform_filter(
        (alt.datum.upSell != 0) & (alt.datum.ex_offset == 10)
    ).mark_text(angle=270, dx=15, xOffset=0).encode(
        x='period:N',
        y='ex_end:Q',
        text=alt.Text('upSell:Q', format=',.0f')
    )


    upSell_label_10_offset = base.transform_filter(
        (alt.datum.upSell != 0) & (alt.datum.ex_offset == 20)
    ).mark_text(angle=270, dx=15, xOffset=20).encode(
        x='period:N',
        y='ex_end:Q',
        text=alt.Text('upSell:Q', format=',.0f')
    )



    # downSell bars without offset (ex_offset == 0)
    downSell_bars_no_offset = base.mark_bar(size=20, color=style.downSell_color, xOffset=0).encode(
        y='cnt_end:Q',
        y2='ex_end:Q'
    ).transform_filter(
        (alt.datum.downSell != 0) & (alt.datum.cnt_offset == 10)
    )

        # downSell bars with offset (ex_offset == 20)
    downSell_bars_10_offset = base.mark_bar(size=20, color=style.downSell_color, xOffset=20).encode(
        y='cnt_end:Q',
        y2='ex_end:Q'
    ).transform_filter(
        (alt.datum.downSell != 0) & (alt.datum.cnt_offset == 20)
    )

    # downSell bars with offset (ex_offset == 20)
    downSell_bars_20_offset = base.mark_bar(size=20, color=style.downSell_color, xOffset=40).encode(
        y='cnt_end:Q',
        y2='ex_end:Q'
    ).transform_filter(
        (alt.datum.downSell != 0) & (alt.datum.cnt_offset == 30)
    )

    # downSell  labels with explicit Y positioning
    downSell_label_no_offset = base.transform_filter(
        (alt.datum.downSell != 0) & (alt.datum.cnt_offset == 10)
    ).mark_text(angle=270, dx=15, xOffset=0).encode(
        x='period:N',
        y='ex_end:Q',
        text=alt.Text('downSell:Q', format=',.0f')
    )


    downSell_label_10_offset = base.transform_filter(
        (alt.datum.downSell != 0) & (alt.datum.cnt_offset == 20)
    ).mark_text(angle=270, dx=15, xOffset=20).encode(
        x='period:N',
        y='ex_end:Q',
        text=alt.Text('downSell:Q', format=',.0f')
    )


    downSell_label_20_offset = base.transform_filter(
        (alt.datum.downSell != 0) & (alt.datum.cnt_offset == 30)
    ).mark_text(angle=270, dx=15, xOffset=40).encode(
        x='period:N',
        y='ex_end:Q',
        text=alt.Text('downSell:Q', format=',.0f')
    )


    # churn bars without offset (ex_offset == 0)
    churn_bars_no_offset = base.mark_bar(size=20, color=style.churn_color, xOffset=0).encode(
        y='churn_end:Q',
        y2='cnt_end:Q'
    ).transform_filter(
        (alt.datum.churn != 0) & (alt.datum.churn_offset == 10)
    )

        # churn bars with offset (ex_offset == 20)
    churn_bars_10_offset = base.mark_bar(size=20, color=style.churn_color, xOffset=20).encode(
        y='churn_end:Q',
        y2='cnt_end:Q'
    ).transform_filter(
        (alt.datum.churn != 0) & (alt.datum.churn_offset == 20)
    )

    # churn bars with offset (ex_offset == 20)
    churn_bars_20_offset = base.mark_bar(size=20, color=style.churn_color, xOffset=40).encode(
        y='churn_end:Q',
        y2='cnt_end:Q'
    ).transform_filter(
        (alt.datum.churn != 0) & (alt.datum.churn_offset == 30)
    )

    # churn bars with offset (ex_offset == 40)
    churn_bars_30_offset = base.mark_bar(size=20, color=style.churn_color, xOffset=60).encode(
        y='churn_end:Q',
        y2='cnt_end:Q'
    ).transform_filter(
        (alt.datum.churn != 0) & (alt.datum.churn_offset == 40)
    )


    # churn  labels with explicit Y positioning
    churn_label_no_offset = base.transform_filter(
        (alt.datum.churn != 0) & (alt.datum.churn_offset == 10)
    ).mark_text(angle=270, dx=15, xOffset=0).encode(
        x='period:N',
        y='cnt_end:Q',
        text=alt.Text('churn:Q', format=',.0f')
    )

    churn_label_10_offset = base.transform_filter(
        (alt.datum.churn != 0) & (alt.datum.churn_offset == 20)
    ).mark_text(angle=270, dx=15, xOffset=20).encode(
        x='period:N',
        y='cnt_end:Q',
        text=alt.Text('churn:Q', format=',.0f')
    )

    churn_label_20_offset = base.transform_filter(
        (alt.datum.churn != 0) & (alt.datum.churn_offset == 30)
    ).mark_text(angle=270, dx=15, xOffset=40).encode(
        x='period:N',
        y='cnt_end:Q',
        text=alt.Text('churn:Q', format=',.0f')
    )


    churn_label_30_offset = base.transform_filter(
        (alt.datum.churn != 0) & (alt.datum.churn_offset == 40)
    ).mark_text(angle=270, dx=15, xOffset=60).encode(
        x='period:N',
        y='cnt_end:Q',
        text=alt.Text('churn:Q', format=',.0f')
    )


    # Rules without offset (ex_offset == 0)
    rules_no_offset = base.mark_rule(color="#707070", opacity=1, strokeWidth=1, xOffset=-10, x2Offset=10).encode(
        x='period:N',
        x2='lead_period:N',
        y='curRev:Q',
        y2='curRev:Q'
    ).transform_filter(
        (alt.datum.churn_offset == 10)
    )

    # rules bars with offset (ex_offset == 20)
    rules_10_offset = base.mark_rule(color="#707070", opacity=1, strokeWidth=1, xOffset=10, x2Offset=10).encode(
        x='period:N',
        x2='lead_period:N',
        y='curRev:Q',
        y2='curRev:Q'
    ).transform_filter(
        (alt.datum.churn_offset == 20)
    )

    # rules bars with offset (ex_offset == 20)
    rules_20_offset = base.mark_rule(color="#707070", opacity=1, strokeWidth=1, xOffset=30, x2Offset=10).encode(
        x='period:N',
        x2='lead_period:N',
        y='curRev:Q',
        y2='curRev:Q'
    ).transform_filter(
       (alt.datum.churn_offset == 30)
    )

    # rules bars with offset (ex_offset == 20)
    rules_30_offset = base.mark_rule(color="#707070", opacity=1, strokeWidth=1, xOffset=50, x2Offset=10).encode(
        x='period:N',
        x2='lead_period:N',
        y='curRev:Q',
        y2='curRev:Q'
    ).transform_filter(
        (alt.datum.churn_offset == 40)
    )

    # rules bars with offset (ex_offset == 20)
    rules_left_offset = base.mark_rule(color="#707070", opacity=1, strokeWidth=1, xOffset=-30, x2Offset=10).encode(
        x='period:N',
        x2='lead_period:N',
        y='curRev:Q',
        y2='curRev:Q'
    ).transform_filter(
        (alt.datum.churn_offset == 0)
    )


    # Text for increase and decrease
    text_increase = base.transform_filter(
        (alt.datum.downSell == 0) & (alt.datum.churn == 0) & (alt.datum.period != 'End Period')
    ).mark_text(dx=50, dy=-10, angle=0, fontWeight='bold', fontSize = 14, align='center').encode(
        x='period:N',
        y='curRev:Q',
        text=alt.Text('curRev:Q', format=',.0f')
    )
    text_decrease = base.transform_filter(
        ((alt.datum.downSell != 0) | (alt.datum.churn != 0)) & (alt.datum.period != 'End Period')
    ).mark_text(dx=50, dy=10, angle=0, fontWeight='bold', fontSize = 14, align='center').encode(
        x='period:N',
        y='curRev:Q',
        text=alt.Text('curRev:Q', format=',.0f')
    )



    # Opening sales bar with xOffset
    first_period_data = df.iloc[0]
    opening_rev = alt.Chart(pd.DataFrame({'period': [first_period_data['period']], 
                                            'preRev': [first_period_data['preRev']], 'startFrom' : [(min_val - padding)],
                                            })).mark_bar(size=20, color=style.beginPeriod_color, xOffset=-20).encode(
        x='period:N',
        y=alt.Y('preRev:Q', scale=common_y_scale), 
        y2='startFrom:N'
    )



    # Add a text label to the opening revenue bar
    opening_label = alt.Chart(pd.DataFrame({'period': [first_period_data['period']], 
                                        'startFrom' : [(min_val - padding)],   
                                        'preRev': [first_period_data['preRev']],
                                        'preMid': [first_period_data['preMid']],
                                        'curMid': [first_period_data['curMid']],
                                        'label': [first_period_data['preRev']]})).mark_text(
        angle=270,  # Rotate the text by 270 degrees
        # fontWeight='bold',
        fontSize = 12,
        align='center', 
        baseline='middle',
        dy = -20  # Adjust this value to position the text within the bar
    ).encode(
        x='period:N',
        y='preMid:Q',
        y2='startFrom:Q',
        text=alt.Text('label:N', format=',.0f')  # Assuming you want to display the revenue as text
    )

    closing_rev = alt.Chart(df[df['period'] == 'End Period']).mark_bar(size=20, color=style.endPeriod_color, xOffset=20).encode(
        x='period:N',
        y=alt.Y('curRev:Q', scale=common_y_scale),
        y2='startFromY'
    )

        
    # Add a text label to the opening revenue bar
    closng_label = alt.Chart(df[df['period'] == 'End Period']).mark_text(
        angle=270,  # Rotate the text by 270 degrees
        # fontWeight='bold',
        fontSize = 12,
        align='center', 
        baseline='middle',
        dy = 20  # Adjust this value to position the text within the bar
    ).encode(
        x='period:N',
        y=alt.Y('curMid:Q', scale=common_y_scale),
        text=alt.Text('curRev:N', format=',.0f')  # Assuming you want to display the revenue as text
    )




    main_chart = nb_bars +  nb_labels + \
                upSell_bars_no_offset + upSell_label_no_offset + upSell_bars_10_offset + upSell_label_10_offset + \
                downSell_bars_no_offset + downSell_bars_10_offset + downSell_bars_20_offset + \
                downSell_label_no_offset + downSell_label_10_offset + downSell_label_20_offset + \
                churn_bars_no_offset +  churn_bars_10_offset + churn_bars_20_offset +  churn_bars_30_offset + \
                churn_label_no_offset + churn_label_10_offset + churn_label_20_offset + churn_label_30_offset + \
                rules_no_offset +  rules_10_offset + rules_20_offset +  rules_30_offset + rules_left_offset + \
                text_increase + text_decrease + opening_rev  +  closing_rev #+ opening_label + closng_label
    
                # churn_bars + rules


    main_chart = main_chart.properties(width=chart_width, height=500)

    # Update the legend data
    legend_data = pd.DataFrame({    
        'category': ['Opening Revenue', 'New Business', 'Expansion', 'Contraction', 'Churn', 'Closing Revenue'],
        'color': [style.beginPeriod_color, style.newBusiness_color, style.upSell_color , style.downSell_color, style.churn_color, style.endPeriod_color],
        'x_pos': [1, 2, 3, 4, 5, 6]
    })



    # Create colored squares for the legend
    squares = alt.Chart(legend_data).mark_square(size=250, stroke='gray', strokeWidth=1).encode(
        x='x_pos:O',
        color=alt.Color('color:N', scale=None)
    )

    # Create text labels for the legend with added spacing
    text = alt.Chart(legend_data).mark_text(align='left', dx=15, fontSize = 12).encode(
        x=alt.X('x_pos:O', axis=alt.Axis(title=None, labels=False)),
        text='category:N'
    )

    # Combine squares and text into one legend chart
    legend = alt.layer(squares, text).properties(
        width=chart_width * 0.8,
        height=50
    )

   # Combine the main chart with the legend
    final_chart = alt.vconcat(
        main_chart,
        legend,
        spacing=10
    )

    return final_chart