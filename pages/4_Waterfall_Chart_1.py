import streamlit as st
import pandas as pd
import altair as alt

# Streamlit page configuration for a wide layout
st.set_page_config(page_title="Waterfall Chart - Placeholder ", layout='wide')

# Create and prepare the DataFrame
def create_dataframe():
    data = {
        "label": ["2023-12", "2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06", "2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12", "2025-01"],
        "amount": [4000, 1707, -1425, -1030, 1812, -1067, -1481, 1228, 1176, 1146, 1205, -1388, 1492, 1000]
    }

    df = pd.DataFrame(data)

    # Display the DataFrame after initiation
    st.dataframe(df, use_container_width=True)

    df['sum'] = df['amount'].cumsum()
    df['previous_sum'] = df['sum'] - df['amount']
    df['text_amount'] = df['amount'].apply(lambda x: f"{x:,.0f}")
    df['center'] = (df['sum'] + df['previous_sum']) / 2
    df['sum_inc'] = df.apply(lambda x: f"{x['sum']:,.0f}" if x['amount'] > 0 else '', axis=1)
    df['sum_dec'] = df.apply(lambda x: f"{x['sum']:,.0f}" if x['amount'] < 0 else '', axis=1)
    df['lead_label'] = df['label'].shift(-1).fillna(method='ffill')

    # Display the DataFrame after calculations
    st.dataframe(df, use_container_width=True)

    return df

# Function to create the Altair chart
def create_chart(df):
    bars = alt.Chart(df).mark_bar(size=45).encode(
        x=alt.X('label:N', axis=alt.Axis(labelAngle=0, title=None)),  # Removed x-axis title
        y=alt.Y('previous_sum:Q', axis=alt.Axis(title=None)),
        y2='sum:Q',
        color=alt.condition(
            alt.datum.amount < 0,
            alt.value("#ee7777"),  # Color for decrease
            alt.value("#88b988")   # Color for increase
        )
    )

    rules = alt.Chart(df).mark_rule(color="#707070", opacity=1, strokeWidth=1, xOffset= -22.5, x2Offset = 22.5).encode(
        x='label:N',
        x2='lead_label:N',
        y='sum:Q',
        y2='sum:Q'
    )

    text_increase = alt.Chart(df[df['amount'] > 0]).mark_text(fontWeight='bold', dy=-10).encode(
        x='label:N',
        y='sum:Q',
        text='sum_inc:N'
    )

    text_decrease = alt.Chart(df[df['amount'] < 0]).mark_text(fontWeight='bold', dy=10).encode(
        x='label:N',
        y='sum:Q',
        text='sum_dec:N'
    )

    text_amount = alt.Chart(df).mark_text(fontWeight='bold', baseline='middle', angle=270).encode(
        x='label:N',    
        y='center:Q',
        text='text_amount:N',
        color=alt.condition(
            alt.datum.amount < 0,
            alt.value("black"),
            alt.value("black")
        )
    )

    return (bars + rules + text_increase + text_decrease + text_amount).properties(
        width=800,
        height=450
    )

# Streamlit app
def app():
    st.title("Single Category Waterfall - WIP")
    df = create_dataframe()
    chart = create_chart(df)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.altair_chart(chart, use_container_width=True)

if __name__ == "__main__":
    app()