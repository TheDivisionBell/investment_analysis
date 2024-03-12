import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

## Analysis for S&P500
## tetst
path = r'C:\Users\Matteo\Downloads\SP500.csv'
def ReturnLumpSum(df, years, investment):
#     for years in years:
    sell_price_dict = {}
    n_shares_dict = {}
    for item in df.Date:
        date_sell = item + pd.DateOffset(years = years)
        if date_sell <= df.Date.max():
            n_shares = investment//df.loc[df['Date']==item, 'PriceNormalize'].values[0]
            sell_price = df.loc[df['Date']==date_sell, 'PriceNormalize'].values[0]
        else:
            sell_price = None
        n_shares_dict[item] = n_shares
        sell_price_dict[item] = sell_price
    df['SellPriceLS'] = df.Date.map(sell_price_dict)
    df['NumSharesLS'] = df.Date.map(n_shares_dict)
    df['ReturnLS'] = df['SellPriceLS']*df['NumSharesLS']
    df['VariationLS'] = df['SellPriceLS']/df['PriceNormalize'] - 1
    return df


def ReturnPAC(df, years, tot_inv, quotes):
    price_list = df.PriceNormalize.to_list()
    n_month = tot_inv//quotes
    inv_pac = np.full(n_month,quotes)
    tot_shares = np.empty((0,0))
    tot_value = np.empty((0,0))
    for item in df.index:
        start = item
        end = start+n_month
        inv_end = years*12 + start
        if inv_end <=len(df.index)-1:
            price_end = df.loc[df.index==inv_end, 'PriceNormalize']
            prices = price_list[start:end]
            shares = inv_pac//prices
            shares_tot = shares.sum()
            tot_shares = np.append(tot_shares, shares_tot)
            value_end = shares_tot*price_end
    #         if isinstance(value_end, float):
            tot_value = np.append(tot_value, value_end)
    #         else:
    #             tot_value = np.append(tot_value, 0)
        else:
            tot_shares = np.append(tot_shares, 0)
            tot_value = np.append(tot_value, 0)
    df['NumSharesPAC'] = tot_shares
    df['ReturnPAC'] = tot_value
    return df


def ReturnSmartPAC(df, years, tot_inv, quotes):
    price_list = df.PriceNormalize.to_list()
    tot_return = np.empty((0, 0))
    shares_owned = np.empty((0, 0))
    for item in df.index:
        end = item + 12 * years
        cap_invested = 0
        n_shares = np.empty((0, 0))
        i = item
        period = 1
        tot_shares = 0
        while cap_invested < tot_inv:
            inv_obj = period * quotes
            cap_val = tot_shares * price_list[i]
            delta_incr_val = inv_obj - cap_val
            if delta_incr_val <= 0:
                shares = 0
            else:
                shares = delta_incr_val // price_list[i]
                cap_invested = cap_invested + delta_incr_val
            tot_shares = shares + tot_shares

            if i < len(df.index) - 1:
                i += 1
                period += 1
            else:
                break
        if end <= len(df.index) - 1:
            price_end = df.loc[df.index == end, 'PriceNormalize']
        else:
            price_end = 0
        tot_return = np.append(tot_return, tot_shares * price_end)
        shares_owned = np.append(shares_owned, tot_shares)

    df['ReturnSmartPAC'] = tot_return
    df['NumSharesSmartPAC'] = shares_owned
    return df

if __name__ == '__main__':
    st.set_page_config(layout='wide')
    st.title('Investment Strategies Comparison')
    st.subheader('', divider=True )
    df = pd.read_csv(path)
    df.drop(['Open', 'High', 'Low', 'Volume', 'Adj Close'], axis=1, inplace=True)
    df['Date'] = pd.to_datetime(df.Date)
    df['PriceNormalize'] = df.Close / 100
    df_pac = df.copy()

    filters = st.form(key='filters')
    with filters:
        cola, space1, colb, space2, colc = st.columns([1,.5,1,.5,1])
        with cola:
            years = np.arange(1,21)
            years_filter = st.selectbox('Investment horizon', years)
        with colb:
            amount = np.arange(0,105000,5000)
            amount_filter = st.select_slider('Amount to be invested', amount)
        with colc:
            pac_quotes = np.arange(0,5100,100)
            pac_filter = st.select_slider('Monthly quotes for accumulation plan', pac_quotes)
        button = filters.form_submit_button('Enter')

    if button:
        df_pac = ReturnLumpSum(df_pac, years_filter, amount_filter)
        df_pac = ReturnPAC(df_pac, years_filter, amount_filter, pac_filter)
        df_pac = ReturnSmartPAC(df_pac, years_filter, amount_filter, pac_filter)
        df_pac_filtered = df_pac.dropna(subset=['SellPriceLS'])
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
