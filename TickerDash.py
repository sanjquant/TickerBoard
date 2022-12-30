import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import json as js
import datetime
from datetime import date, timedelta
from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews
from pyChatGPT import ChatGPT

news_count = 10
# set a default date :
today = date.today()
default_date_yesterday = today - timedelta(days=90)

# add title to the dasboard :
st.title("Stock Lookup")

# Read the list of tickers for a json file
ticket_file = open("ticket.json", "r")
ticker_name = js.load(ticket_file)
ticker_list = tuple(ticker_name["tickers"])
session_token = ticker_name["session_token"]

# """
# Get Ticket:
# Start Date:
# End Date  :
# """
ticker = st.sidebar.selectbox("Select the ticker", ticker_list)
start_date = st.sidebar.date_input("Start Date", default_date_yesterday)
end_date = st.sidebar.date_input("End Date", today)

# """
# Get Data and Plot
# """

ticker_data = yf.download(ticker, start=start_date, end=end_date)
fig = px.line(
    ticker_data, x=ticker_data.index, y=ticker_data["Adj Close"], title=ticker
)
st.plotly_chart(fig)

# """
# Get Pricing , fundamentals and news :

# """
pricing_data, fundamentals, news, openaix = st.tabs(
    ["Pricing Data", "Fundamentals", "Top 10 News", "OpenAI GPT"]
)

with pricing_data:
    st.header("Price Change")
    price_change = ticker_data
    price_change["Percentage Change"] = (
        price_change["Adj Close"] / price_change["Adj Close"].shift(1)
    ) - 1

    price_change.dropna(inplace=True)
    st.write(price_change)
    return_annual = price_change["Percentage Change"].mean() * 252 * 100
    st.write(f"Annual return is :  {return_annual} %")
    std_dev = np.std(price_change["Percentage Change"]) * np.sqrt(252)
    st.write(f"Standard Deviation is :  {std_dev*100} %")
    st.write("Risk Adj. Return is : ", return_annual / (std_dev * 100))

with fundamentals:
    st.write("Fundamentals")
    key = "6BM21Y50WJLN2VBF"
    fun_data = FundamentalData(key, output_format="pandas")
    st.subheader("Balance Sheet")
    balance_sheet = fun_data.get_balance_sheet_annual(ticker)[0]
    bs = balance_sheet.T[2:]
    bs.columns = list(balance_sheet.T.iloc[0])
    st.write(bs)

    st.subheader("Income Statement")
    income_statement = fun_data.get_income_statement_annual(ticker)[0]
    ist = income_statement.T[2:]
    ist.columns = list(income_statement.T.iloc[0])
    st.write(ist)

    st.subheader("Cash Flow Statement")
    cash_flow = fun_data.get_cash_flow_annual(ticker)[0]
    cf = cash_flow.T[2:]
    cf.columns = list(cash_flow.T.iloc[0])
    st.write(cf)

with news:
    st.header(f"Current News on - {ticker}")
    ticker_news = StockNews(ticker, save_news=False)
    read_news_dframe = ticker_news.read_rss()

    for i in range(news_count):
        st.subheader(f"News {i+1}")
        st.write(read_news_dframe['published'][i])
        st.write(read_news_dframe["title"][i])
        st.write(read_news_dframe["summary"][i])
        sentiment_title = read_news_dframe['sentiment_title'][i]
        st.write(f"Title Sentiment - {sentiment_title}")
        sentiment_news = read_news_dframe['sentiment_summary'][i]
        st.write(f"News Sentiment - {sentiment_news}")


# """ChatGPT"""
api_chatGpt = ChatGPT(session_token)
buy_reason = api_chatGpt.send_message(f"3 Reasons to buy {ticker} stock")
sell_reason = api_chatGpt.send_message(f"3 Reasons to sell {ticker} stock")
swot_analysis = api_chatGpt.send_message(f"SWOT analysis of {ticker} stock")

with openaix:
    buy_tab, sell_tab, swot_tab = st.tabs(
        ['3 Reasons to buy', '3 Reasons to sell', 'SWOT analysis'])
    with buy_tab:
        st.subheader(f"3 Reasons on why to BUY {ticker} stock")
        st.write(buy_reason["message"])

    with sell_tab:
        st.subheader(f"3 Reasons on why to SELL {ticker} stock")
        st.write(sell_reason["message"])

    with swot_tab:
        st.subheader(f"SWOT analysis of {ticker} stock")
        st.write(swot_analysis["message"])
