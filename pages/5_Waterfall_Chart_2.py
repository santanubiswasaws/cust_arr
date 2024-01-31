
import streamlit as st
import pandas as pd
import altair as alt
from streamlit_dimensions import st_dimensions

# Streamlit page configuration for a wide layout
st.set_page_config(page_title="Waterfall Chart with Sales and Credits", layout='wide')

# Create and prepare the DataFrame
def create_dataframe():
    sales_data = [4000, 1707, 1425, 1030, 0, 1067, 0, 1228, 1176, 1146, 1205, 1388, 1492, 1000]
    credit_data = [-500, -300, -200, -150, -6000, -250, 0, 0, -100, -350, -450, -500, -300, -200]

    data = {
        "label": ["2023-12", "2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06", "2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12", "2025-01"],
        "sales": sales_data,
        "credit": credit_data
    }   

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    df['current_month_cumm_sales'] = df['sales'].add(df['credit']).cumsum()
    df['previous_month_cumm_sales'] = df['current_month_cumm_sales'].shift(1).fillna(0)
    df['lead_label'] = df['label'].shift(-1).fillna(method='ffill')
    df['sales_end'] = df['previous_month_cumm_sales'] + df['sales']
    df['crd_start'] = df['previous_month_cumm_sales'] + df['sales']
    df['crd_end'] = df['crd_start'] + df['credit']
    df['change'] = df['current_month_cumm_sales'] - df['previous_month_cumm_sales']

    minimal_visible_change = 1  # Adjust this value as needed for visibility

    # Adjustments for sales and credit calculations
    df['sales_end'] = df.apply(lambda row: row['previous_month_cumm_sales'] + row['sales'] if row['sales'] != 0 else row['previous_month_cumm_sales'] + minimal_visible_change, axis=1)
    df['crd_end'] = df.apply(lambda row: row['crd_start'] + row['credit'] if row['credit'] != 0 else row['crd_start'] - minimal_visible_change, axis=1)
    
    st.dataframe(df, use_container_width=True)

    return df

def create_chart(df, chart_width):


    base = alt.Chart(df).encode(
        x=alt.X('label:N', axis=alt.Axis(labelAngle=0, title=None))
    )

    # Sales bars
    sales_bars = base.transform_filter(
        alt.datum.sales != 0
    ).mark_bar(size=20, color='#88b988').encode(
        y=alt.Y('sales_end:Q', axis=alt.Axis(title="Monthly Recurring Revenue", format=',.0f', labelPadding=40)),
        y2='previous_month_cumm_sales:Q'
    )

    # # Sales data labels
    # sales_labels = base.transform_filter(
    #     alt.datum.sales != 0
    # ).mark_text(align='left', angle=270, dx=10).encode(
    #     x='label:N',
    #     y=alt.Y('crd_start:Q', axis=alt.Axis(labels=False)),
    #     text=alt.Text('sales:Q', format=',')
    # )


    # Sales data labels with explicit Y positioning
    sales_labels = base.transform_filter(
        alt.datum.sales != 0
    ).mark_text(align='left', angle=270, dx=10).encode(
        x='label:N',
        y=alt.Y('sales_end:Q', axis=alt.Axis(labels=False)),  # Position based on sales_end
        text=alt.Text('sales:Q', format=',')
    )




    # Credit bars
    credit_bars = base.transform_filter(
        alt.datum.credit != 0
    ).mark_bar(size=20, color='#ee7777', xOffset=20).encode(
        x='label:N',
        y='crd_end:Q',
        y2='crd_start:Q'
    )

    # Credit data labels with explicit Y positioning
    credit_labels = base.transform_filter(
        alt.datum.credit != 0
    ).mark_text(align='left', angle=270, dx=-40).encode(
        x='label:N',
        y=alt.Y('crd_end:Q', axis=alt.Axis(labels=False)),  # Position based on crd_end
        text=alt.Text('credit:Q', format=',')
    )

    # # Credit data labels
    # credit_labels = base.transform_filter(
    #     alt.datum.credit != 0
    # ).mark_text(align='left', angle=270, dy=20, dx=-40).encode(
    #     x='label:N',
    #     y=alt.Y('current_month_cumm_sales:Q', axis=alt.Axis(labels=False)),
    #     text=alt.Text('credit:Q', format=',')
    # )

    # Rules
    rules = base.mark_rule(color="#707070", opacity=1, strokeWidth=1, xOffset=10, x2Offset=10).encode(
        x='label:N',
        x2='lead_label:N',
        y='current_month_cumm_sales:Q',
        y2='current_month_cumm_sales:Q'
    )

    # Text for increase and decrease
    text_increase = base.transform_filter(
        alt.datum.credit >= 0
    ).mark_text(dx=45, dy=-10, angle=0, fontWeight='bold', align='center').encode(
        x='label:N',
        y='current_month_cumm_sales:Q',
        text=alt.Text('current_month_cumm_sales:Q', format=',')
    )
    text_decrease = base.transform_filter(
        alt.datum.credit < 0
    ).mark_text(dx=45, dy=10, angle=0, fontWeight='bold', align='center').encode(
        x='label:N',
        y='current_month_cumm_sales:Q',
        text=alt.Text('current_month_cumm_sales:Q', format=',')
    )

    # Closing sales bar with xOffset
    last_month_data = df.iloc[-1]

    closing_sales = alt.Chart(pd.DataFrame({'label': [last_month_data['label']], 
                                            'current_month_cumm_sales': [last_month_data['current_month_cumm_sales']]})).mark_bar(size=20, color='#55aadd', xOffset=40).encode(
        x='label:N',
        y='current_month_cumm_sales:Q'
    )


    # Additional data for Y-axis line
    y_axis_df = pd.DataFrame({'label': [df['label'].min()], 'value': [df['current_month_cumm_sales'].min()]})
    y_axis_line = alt.Chart(y_axis_df).mark_rule(color="#bbbbbb", strokeWidth=1).encode(
        x='label:N',
        y=alt.value(0)
    )

    # Combine main chart elements - as of now - sales_labels and credit_labels are hiding Y axis labels 

    main_chart = sales_bars + credit_bars + sales_labels + credit_labels + rules + closing_sales + text_increase + text_decrease 
    #main_chart = sales_bars + credit_bars +  rules + closing_sales + text_increase + text_decrease 


    main_chart = main_chart.properties(width=chart_width, height=600)



    # Update the legend data
    legend_data = pd.DataFrame({    
        'category': ['Sales', 'Credits', 'Closing Sales'],
        'color': ['#88b988', '#ee7777', '#55aadd'],
        'x_pos': [1, 2, 3]
    })

    # Create colored squares for the legend
    squares = alt.Chart(legend_data).mark_square(size=150).encode(
        x='x_pos:O',
        color=alt.Color('color:N', scale=None)
    )

    # Create text labels for the legend with added spacing
    text = alt.Chart(legend_data).mark_text(align='left', dx=15).encode(
        x=alt.X('x_pos:O', axis=alt.Axis(title=None, labels=False)),
        text='category:N'
    )

    # Combine squares and text into one legend chart
    legend = alt.layer(squares, text).properties(
        width=300,
        height=50
    )

    # Combine the main chart with the legend
    final_chart = alt.vconcat(
        main_chart,
        legend,
        spacing=10
    )

    return final_chart




# Streamlit app
def app():
    st.title("Multi Category Waterfall  - WIP")

    dimension_data = st_dimensions(key="main")
    try:
        chart_width = int(dimension_data["width"] * 0.9)
    except: 
        chart_width = 1100

    df = create_dataframe()
    chart = create_chart(df, chart_width)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.altair_chart(chart, use_container_width=True)

if __name__ == "__main__":
    app()
