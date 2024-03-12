import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

path = r'C:\Users\Matteo\Downloads\SP500.csv'

def PosNegSegments(df, years):
    price_list = np.array(df.PriceNormalize)
    return_positive = np.empty((0,0))
    return_negative = np.empty((0,0))
    for item in df.index:
        start = item
        end = item + years*12
        if end<=df.index.max():
            variation = np.diff(price_list[start:end])
            positive = np.sum(variation>= 0, axis=0)
            negative = np.sum(variation<0, axis=0)
        else:
            positive = 0
            negative = 0
        return_positive = np.append(return_positive, positive)
        return_negative = np.append(return_negative, negative)
    df['PositiveReturn'] = return_positive
    df['NegativeReturn'] = return_negative
    df['PercentagePositive'] = df['PositiveReturn']/(df['PositiveReturn']+df['NegativeReturn'])
    df['PercentageNegative'] = df['NegativeReturn']/(df['PositiveReturn']+df['NegativeReturn'])
    return df

def YearlyReturn(df, years):
    price_list = np.array(df.PriceNormalize)
    price_end = np.empty((0,0))
    for item in df.index:
        inv_end = years*12 + item
        if inv_end <=len(df.index)-1:
            price = price_list[inv_end]
        else:
            price = 0
        price_end = np.append(price_end, price)
    df[f'Return{years}Y'] = price_end
    df[f'Return{years}YPercentage'] = df[f'Return{years}Y']/df.PriceNormalize-1
    return df

if __name__ == '__main__':
    st.set_page_config(layout='wide')
    st.title('Finance Analysis')
    st.subheader('', divider=True)
    df = pd.read_csv(path)
    df.drop(['Open', 'High', 'Low', 'Volume', 'Adj Close'], axis=1, inplace=True)
    df['Date'] = pd.to_datetime(df.Date)
    df['PriceNormalize'] = df.Close / 100
    df_metrics = df.copy()
    filtershome = st.form(key='filtershome')
    with filtershome:
        cola, colb = st.columns([1, 2])
        with cola:
            years = np.arange(1, 21)
            years_filter = st.select_slider('Investment horizon', years)
        button = filtershome.form_submit_button('Enter')

    if button:
        df_metrics = PosNegSegments(df_metrics, years_filter)
        df_metrics = YearlyReturn(df_metrics, 1)
        df_metrics[f'ReturnRolling{years_filter}Y'] = df_metrics.Return1YPercentage.rolling(years_filter).mean()
        df_metrics_filtered = df_metrics.loc[df_metrics.Return1Y != 0]

        yearly_avg_return = df_metrics.Return1YPercentage.mean()
        st.subheader('Average Yearly Return of the Index')
        st.metric(label='Average', value='{:,.2%}'.format(yearly_avg_return))

        perc_return_fig = px.bar(df_metrics_filtered, x='Date', y=['Return1YPercentage', f'ReturnRolling{years_filter}Y'],
                            title=f'{years_filter}Y Percentage Return')
        pos_neg_fig = px.line(df_metrics, x='Date', y=['PercentagePositive', 'PercentageNegative'],
                          title=f'Percentage of positive/Negative return in a {years_filter} range')
        st.plotly_chart(perc_return_fig, use_container_width=True, theme='streamlit')
        st.plotly_chart(pos_neg_fig, use_container_width=True, theme='streamlit')
