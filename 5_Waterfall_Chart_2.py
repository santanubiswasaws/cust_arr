import streamlit as st
import pandas as pd
import altair as alt
from streamlit_dimensions import st_dimensions
from arr_lib import styling as style

def create_dataframe():
    data = {
        'period': ['2022-12', '2023-01', '2023-02', '2023-03', '2023-04', '2023-05', '2023-06', '2023-07', '2023-08', '2023-09'],
        'preRev': [1000, 1210, 1310, 1810, 2310, 3110, 3310, 2910, 2910, 3210],
        'newBusiness': [200, 0, 500, 0, 700, 500, 0, 0, 0, 300],
        'upSell': [30, 400, 0, 600, 100, 0, 0, 0, 400, 200],
        'downSell': [-20, 0, 0, -100, 0, -300, 0, 0, -100, -100],
        'churn': [0, -300, 0, 0, 0, 0, -400, 0, 0, -50],
        'curRev': [1210, 1310, 1810, 2310, 3110, 3310, 2910, 2910, 3210, 3560]
}


    df = pd.DataFrame(data)

    #df['curRev'] = df['preRev'] + df['newBusiness'] + df['upSell'] + df['downSell'] + df['churn']

    # Add the 'nb_end' column as the sum of 'preRev' and 'newBusiness'
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


    df['lead_period'] = df['period'].shift(-1).ffill()






    df['curMid'] = df['curRev'] / 2
    df['preMid'] = df['preRev'] / 2

    return df



def calculate_offsets(df):
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






def create_chart(df, chart_width):



    base = alt.Chart(df).encode(
        x=alt.X('period:N', axis=alt.Axis(labelAngle=0, title=None, domain=True, domainColor='black', domainWidth=1, ticks=True, tickWidth=1, tickSize=8))
    )


    # newBusiness bars
    nb_bars = base.transform_filter(
        alt.datum.newBusiness != 0
    ).mark_bar(size=20, color=style.newBusiness_color).encode(
        y=alt.Y('nb_end:Q', axis=alt.Axis(title="Recurring Revenue", format=',.0f', domain=True, domainColor='black', domainWidth=1, ticks=True, tickWidth=1, tickSize=8)),
        y2='preRev:Q'
    )

    # newBusiness labels with explicit Y positioning
    nb_labels = base.transform_filter(
        alt.datum.newBusiness != 0
    ).mark_text(angle=270, dx=15).encode(
        x='period:N',
        y='nb_end:Q',
        #y=alt.Y('sales_end:Q', axis=alt.Axis(labels=False)),  # Position based on sales_end
        text=alt.Text('newBusiness:Q', format=',')
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
        text=alt.Text('upSell:Q', format=',')
    )


    upSell_label_10_offset = base.transform_filter(
        (alt.datum.upSell != 0) & (alt.datum.ex_offset == 20)
    ).mark_text(angle=270, dx=15, xOffset=20).encode(
        x='period:N',
        y='ex_end:Q',
        text=alt.Text('upSell:Q', format=',')
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
        text=alt.Text('downSell:Q', format=',')
    )


    downSell_label_10_offset = base.transform_filter(
        (alt.datum.downSell != 0) & (alt.datum.cnt_offset == 20)
    ).mark_text(angle=270, dx=15, xOffset=20).encode(
        x='period:N',
        y='ex_end:Q',
        text=alt.Text('downSell:Q', format=',')
    )


    downSell_label_20_offset = base.transform_filter(
        (alt.datum.downSell != 0) & (alt.datum.cnt_offset == 30)
    ).mark_text(angle=270, dx=15, xOffset=40).encode(
        x='period:N',
        y='ex_end:Q',
        text=alt.Text('downSell:Q', format=',')
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
        text=alt.Text('churn:Q', format=',')
    )

    churn_label_10_offset = base.transform_filter(
        (alt.datum.churn != 0) & (alt.datum.churn_offset == 20)
    ).mark_text(angle=270, dx=15, xOffset=20).encode(
        x='period:N',
        y='cnt_end:Q',
        text=alt.Text('churn:Q', format=',')
    )

    churn_label_20_offset = base.transform_filter(
        (alt.datum.churn != 0) & (alt.datum.churn_offset == 30)
    ).mark_text(angle=270, dx=15, xOffset=40).encode(
        x='period:N',
        y='cnt_end:Q',
        text=alt.Text('churn:Q', format=',')
    )


    churn_label_30_offset = base.transform_filter(
        (alt.datum.churn != 0) & (alt.datum.churn_offset == 40)
    ).mark_text(angle=270, dx=15, xOffset=60).encode(
        x='period:N',
        y='cnt_end:Q',
        text=alt.Text('churn:Q', format=',')
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
        text=alt.Text('curRev:Q', format=',')
    )
    text_decrease = base.transform_filter(
        ((alt.datum.downSell != 0) | (alt.datum.churn != 0)) & (alt.datum.period != 'End Period')
    ).mark_text(dx=50, dy=10, angle=0, fontWeight='bold', fontSize = 14, align='center').encode(
        x='period:N',
        y='curRev:Q',
        text=alt.Text('curRev:Q', format=',')
    )



    # Opening sales bar with xOffset
    first_period_data = df.iloc[0]
    opening_rev = alt.Chart(pd.DataFrame({'period': [first_period_data['period']], 
                                            'preRev': [first_period_data['preRev']]})).mark_bar(size=20, color=style.beginPeriod_color, xOffset=-20).encode(
        x='period:N',
        y='preRev:Q'
    )

    # Add a text label to the opening revenue bar
    opening_label = alt.Chart(pd.DataFrame({'period': [first_period_data['period']], 
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
        text=alt.Text('label:N', format=',')  # Assuming you want to display the revenue as text
    )



    closing_rev = alt.Chart(df[df['period'] == 'End Period']).mark_bar(size=20, color=style.endPeriod_color, xOffset=20).encode(
        x='period:N',
        y='curRev:Q'
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
        y='curMid:Q',
        text=alt.Text('curRev:N', format=',')  # Assuming you want to display the revenue as text
    )




    main_chart = nb_bars +  nb_labels + \
                upSell_bars_no_offset + upSell_label_no_offset + upSell_bars_10_offset + upSell_label_10_offset + \
                downSell_bars_no_offset + downSell_bars_10_offset + downSell_bars_20_offset + \
                downSell_label_no_offset + downSell_label_10_offset + downSell_label_20_offset + \
                churn_bars_no_offset +  churn_bars_10_offset + churn_bars_20_offset +  churn_bars_30_offset + \
                churn_label_no_offset + churn_label_10_offset + churn_label_20_offset + churn_label_30_offset + \
                rules_no_offset +  rules_10_offset + rules_20_offset +  rules_30_offset + rules_left_offset + \
                text_increase + text_decrease + opening_rev +  opening_label +  closing_rev + closng_label
    
                # churn_bars + rules


    main_chart = main_chart.properties(width=chart_width, height=600)

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





def main():
    st.set_page_config(layout="wide")  # Set the Streamlit layout as wide
    st.title('Streamlit Program with DataFrame Display')

    dimension_data = st_dimensions(key="main")
    try:
        chart_width = int(dimension_data["width"] * 0.9)
    except: 
        chart_width = 1100

    df = create_dataframe()
    df = calculate_offsets(df)


    chart = create_chart(df, chart_width)
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Display the DataFrame with container width set to True
    st.dataframe(df, use_container_width=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

    st.altair_chart(chart, use_container_width=True)

if __name__ == '__main__':
    main()
