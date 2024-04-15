import streamlit as st
import datetime
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import contextlib
from functools import partialmethod

import requests
## Analysis for S&P500
## tetst
# path = r'C:\Users\Matteo\Downloads\SP500.csv'

today = datetime.datetime.now()
s_date = datetime.date(1960,1,1)
e_date = datetime.date(today.year,1,1)
def ReturnLumpSum(df, years, investment):
    date_array = df['Date'].values
    len_date_array = len(date_array)
    max_iteration = len_date_array - years * 365
    sell_price_dict = np.zeros(len_date_array)
    max_date = df.Date.max()
    price_dict = {date: price for date, price in zip(date_array, df['PriceNormalize'])}
    for i, item in enumerate(date_array):
        if i < max_iteration:
            target_date = np.datetime64(item) + np.timedelta64(years*365, 'D')
            if target_date<max_date:
                while target_date not in price_dict:
                    target_date += np.timedelta64(1, 'D')
                sell_price = price_dict[target_date]
            else:
                sell_price = None
            sell_price_dict[i] = sell_price
        else:
            break
    df['SellPriceLS'] = sell_price_dict
    df['NumSharesLS'] = investment//df.PriceNormalize
    df['ReturnLS'] = df['SellPriceLS']*df['NumSharesLS']
    df['VariationLS'] = df['SellPriceLS']/df['PriceNormalize'] - 1
    return df

# def ReturnPAC(df, years, tot_inv, quotes):
#     price_list = df.PriceNormalize.to_list()
#     n_month = tot_inv//quotes
#     inv_pac = np.full(n_month,quotes)
#     tot_shares = np.empty((0,0))
#     tot_value = np.empty((0,0))
#     for item in df.index:
#         start = item
#         end = start+n_month
#         inv_end = years*12 + start
#         if inv_end <=len(df.index)-1:
#             price_end = df.loc[df.index==inv_end, 'PriceNormalize']
#             prices = price_list[start:end]
#             shares = inv_pac//prices
#             shares_tot = shares.sum()
#             tot_shares = np.append(tot_shares, shares_tot)
#             value_end = shares_tot*price_end
#     #         if isinstance(value_end, float):
#             tot_value = np.append(tot_value, value_end)
#     #         else:
#     #             tot_value = np.append(tot_value, 0)
#         else:
#             tot_shares = np.append(tot_shares, 0)
#             tot_value = np.append(tot_value, 0)
#     df['NumSharesPAC'] = tot_shares
#     df['ReturnPAC'] = tot_value
#     return df

def ReturnPAC(df, years, tot_inv, quotes):
    date_array = df['Date'].values
    len_date_array = len(date_array)
    max_iteration = len_date_array - years * 365
    price_dict = {date: price for date, price in zip(date_array, df['PriceNormalize'])}
    tot_return = np.zeros(len_date_array)
    shares_owned = np.zeros(len_date_array)
    for i, item in enumerate(date_array):
        tot_shares = 0
        cap_invested = 0
        target_date = np.datetime64(item)
        date_sell = target_date + np.timedelta64(365 * years, 'D')

        while date_sell not in price_dict:
            date_sell += np.timedelta64(1, 'D')

        if i < max_iteration:

            while cap_invested < tot_inv:

                while target_date not in price_dict:
                    target_date += np.timedelta64(1, 'D')
                shares = quotes // price_dict[target_date]

                tot_shares += shares

                target_date += np.timedelta64(30, 'D')

                cap_invested +=quotes

            tot_return[i] = tot_shares * price_dict[date_sell]
            shares_owned[i] = tot_shares

        else:
            break

    df['ReturnPAC'] = tot_return
    df['NumSharesPAC'] = shares_owned
    return df


def ReturnSmartPAC(df, years, tot_inv, quotes):
    date_array = df['Date'].values
    len_date_array = len(date_array)
    max_iteration = len_date_array - years * 365
    price_dict = {date: price for date, price in zip(date_array, df['PriceNormalize'])}
    tot_return = np.zeros(len_date_array)
    shares_owned = np.zeros(len_date_array)
    for i, item in enumerate(date_array):
        tot_shares = 0
        cap_invested = 0
        period = 0
        target_date = np.datetime64(item)
        date_sell = target_date + np.timedelta64(365 * years, 'D')

        while date_sell not in price_dict:
            date_sell += np.timedelta64(1, 'D')

        if i < max_iteration:
            cap_val = 0

            while cap_invested < tot_inv and cap_val < tot_inv:

                while target_date not in price_dict:
                    target_date += np.timedelta64(1, 'D')

                inv_obj = (period + 1) * quotes
                cap_val = tot_shares * price_dict[target_date]
                delta_incr_val = inv_obj - cap_val

                if delta_incr_val <= 0:
                    shares = 0
                elif delta_incr_val > 0:
                    shares = delta_incr_val // price_dict[target_date]
                    cap_invested += delta_incr_val
                else:
                    shares = 0

                tot_shares += shares
                period += 1

                target_date += np.timedelta64(30, 'D')

            tot_return[i] = tot_shares * price_dict[date_sell]
            shares_owned[i] = tot_shares

        else:
            break

    df['ReturnSmartPAC'] = tot_return
    df['NumSharesSmartPAC'] = shares_owned
    return df

if __name__ == '__main__':
    st.set_page_config(layout='wide')
    st.title('Investment Strategies Comparison')
    st.subheader('', divider=True)
    # df = pd.read_csv(path)
    # df.drop(['Open', 'High', 'Low', 'Volume', 'Adj Close'], axis=1, inplace=True)
    # df['Date'] = pd.to_datetime(df.Date)
    # df['PriceNormalize'] = df.Close / 100
    # df_pac = df.copy()

    filters = st.form(key='filters')
    with filters:
        colt, space0,cola, space1, colb, space2, colc = st.columns([1, .5, 1,.5,1,.5,1])
        with colt:
            ticker = st.text_input('Please insert a ticker')
            print(ticker)
        with cola:
            years = np.arange(1, 21)
            years_filter = st.selectbox('Investment horizon', years)
        with colb:
            amount = np.arange(0, 105000, 5000)
            amount_filter = st.select_slider('Amount to be invested', amount)
        with colc:
            pac_quotes = np.arange(0, 5100, 100)
            pac_filter = st.select_slider('Monthly quotes for accumulation plan', pac_quotes)
        button = filters.form_submit_button('Enter')

    if button:
        @contextlib.contextmanager
        def ssl_verification_disabled():
            old_request = requests.Session.request
            requests.Session.request = partialmethod(old_request, verify=False)
            yield
            requests.Session.request = old_request


        with ssl_verification_disabled():
            df = yf.download(ticker, s_date, e_date)

        # df = yf.download(ticker, s_date, e_date)
        df.reset_index(inplace=True)
        st.dataframe(df.head(10))
        df.drop(['Open', 'High', 'Low', 'Volume', 'Adj Close'], axis=1, inplace=True)
        df['Date'] = pd.to_datetime(df.Date)
        df['PriceNormalize'] = df.Close / 100
        df_pac = df.copy()
        df_pac = ReturnLumpSum(df_pac, years_filter, amount_filter)
        df_pac = ReturnPAC(df_pac, years_filter, amount_filter, pac_filter)
        df_pac = ReturnSmartPAC(df_pac, years_filter, amount_filter, pac_filter)
        # df_merge = pd.merge(df_lsum, df_pac, on='Date', how='inner')
        # df_merge = pd.merge(df_merge, df_spac, on='Date', how='inner')
        df_pac_filtered_0 = df_pac.dropna(subset=['ReturnLS'])
        df_pac_filtered = df_pac_filtered_0[df_pac_filtered_0['ReturnLS'] != 0]
        # st.dataframe(df_pac_filtered)

        # Return
        return_mean_ls = df_pac_filtered.ReturnLS.mean()
        return_stdev_ls = df_pac_filtered.ReturnLS.std(skipna=True)

        return_mean_pac = df_pac_filtered.ReturnPAC.mean()
        return_stdev_pac = df_pac_filtered.ReturnPAC.std(skipna=True)

        return_mean_spac = df_pac_filtered.ReturnSmartPAC.mean()
        return_stdev_spac = df_pac_filtered.ReturnSmartPAC.std(skipna=True)

        col01,space01, col02, space02, col03,space03, col04 = st.columns([1, .5, 1, .5, 1, .5, 1])
        with col01:
            st.metric(label='', value='Metrics')
            st.metric(label='', value='Avg. Return')
            st.metric(label='', value='% Return')
            st.metric(label='', value='StDev')

        with col02:
            st.metric(label='', value='Lump Sum')
            st.metric(label='', value="{:,.0f}".format(return_mean_ls))
            st.metric(label='', value="{:,.2%}".format(return_mean_ls/amount_filter))
            st.metric(label='', value="{:,.0f}".format(return_stdev_ls))

        with col03:
            st.metric(label='', value='PAC')
            st.metric(label='', value="{:,.0f}".format(return_mean_pac))
            st.metric(label='', value="{:,.2%}".format(return_mean_pac / amount_filter))
            st.metric(label='', value="{:,.0f}".format(return_stdev_pac))

        with col04:
            st.metric(label='', value='Smart PAC')
            st.metric(label='', value="{:,.0f}".format(return_mean_spac))
            st.metric(label='', value="{:,.2%}".format(return_mean_spac / amount_filter))
            st.metric(label='', value="{:,.0f}".format(return_stdev_spac))

        price_fig = px.line(df_pac_filtered, x='Date', y='Close', title='Average Monthly Price')
        return_fig = px.line(df_pac_filtered, x='Date', y=['ReturnLS', 'ReturnPAC', 'ReturnSmartPAC'],
                      title=f'Return after {years_filter}Y investment')

        # Histogram
        # filtered = df_pac_filtered[df_pac_filtered['ReturnLS'] != 0]
        return_pac = df_pac_filtered.ReturnPAC.to_list()
        return_lsum = df_pac_filtered.ReturnLS.to_list()
        return_spac = df_pac_filtered.ReturnSmartPAC.to_list()
        return_hist_fig = go.Figure()
        return_hist_fig.add_trace(go.Histogram(x=return_pac, name='PAC'))
        return_hist_fig.add_trace(go.Histogram(x=return_lsum, name='LumpSum'))
        return_hist_fig.add_trace(go.Histogram(x=return_spac, name='SmartPac'))
        # Overlay both histograms
        return_hist_fig.update_layout(barmode='overlay')
        # Reduce opacity to see both histograms
        return_hist_fig.update_traces(opacity=0.45)



        shares_fig = px.line(df_pac_filtered, x='Date', y=['NumSharesLS', 'NumSharesPAC', 'NumSharesSmartPAC'],
                             title=f'Shares owned {years_filter}Y investment')
        st.plotly_chart(price_fig, use_container_width=True, theme='streamlit')
        st.plotly_chart(return_fig, use_container_width=True, theme='streamlit')
        st.plotly_chart(return_hist_fig, use_container_width=True, theme='streamlit')
        st.plotly_chart(shares_fig, use_container_width=True, theme='streamlit')
        st.subheader('Raw Data')
        st.dataframe(df_pac_filtered)
