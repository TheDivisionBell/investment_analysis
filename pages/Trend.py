import datetime
import plotly.express as px
import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

tickers = pd.read_html(
    'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
ticker_dict = dict(zip(tickers['Security'], tickers['Symbol']))

today = datetime.datetime.now()
s_date = datetime.date(1990,1,1)
e_date = datetime.date(today.year,1,1)


if __name__=='__main__':
    st.set_page_config(layout='wide')
    st.title('Investment Strategies Comparison')
    st.subheader('', divider=True)
    with st.form('t_filter'):
        t_col, sp_1, d_col, = st.columns([1, .5, 1,])
        with t_col:
            ticker = st.selectbox('Choose a Stock', ticker_dict.keys(), index=None, placeholder='Select a Ticker')
        with d_col:
            date_range = st.date_input('Date Range', [s_date, e_date])
        button = st.form_submit_button('Enter')

    if button:
        data = yf.download(ticker_dict[ticker], date_range[0], date_range[1])

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig.add_trace(
            go.Scatter(x=data.index, y=data['Adj Close'], name="price"),
            secondary_y=False,
        )

        fig.add_trace(
            go.Bar(x=data.index, y=data['Volume'], name="volume"),
            secondary_y=True,
        )
        # Add figure title
        fig.update_layout(
            title_text=f"{ticker} Price and Volume"
        )

        # Set x-axis title
        fig.update_xaxes(title_text="date")
        # Set y-axes titles
        fig.update_yaxes(title_text="<b>price</b>", secondary_y=False)
        fig.update_yaxes(title_text="<b>volume</b>", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(data, use_container_width=True)




