import sys
import streamlit as st
import altair as alt
from yahooquery import Ticker
import datetime


AVAILABLE_DICTIONARIES = {
    'asset_profile': 'Asset Profile',
    'calendar_events': 'Calendar Events',
    'esg_scores': 'ESG Scores',
    'financial_data': 'Financial Data',
    'fund_profile': 'Fund Profile',
    'key_stats': 'Key Statistics',
    'major_holders': 'Major Holders',
    'price': 'Pricing',
    'quote_type': 'Quote Type',
    'share_purchase_activity': 'Share Purchase Activity',
    'summary_detail': 'Summary Detail',
    'summary_profile': 'Summary Profile'
}

AVAILABLE_DATAFRAMES = {
    'balance_sheet': 'Balance Sheet',
    'cash_flow': 'Cash Flow',
    'company_officers': 'Company Officers',
    'earning_history': 'Earning History',
    'fund_ownership': 'Fund Ownership',
    'grading_history': 'Grading History',
    'income_statement': 'Income Statement',
    'insider_holders': 'Insider Holders',
    'insider_transactions': 'Insider Transactions',
    'institution_ownership': 'Institution Ownership',
    'recommendation_trend': 'Recommendation Trends',
    'sec_filings': 'SEC Filings'
}

FUND_SPECIFIC = {
    'fund_bond_holdings': 'Bond Holdings',
    'fund_bond_ratings': 'Bond Ratings',
    'fund_equity_holdings': 'Equity Holdings',
    'fund_holding_info': 'Holding Information',
    'fund_performance': 'Performance',
    'fund_sector_weightings': 'Sector Weightings',
    'fund_top_holdings': 'Top Holdings',
}


def format_func_dicts(option):
    return AVAILABLE_DICTIONARIES[option]


def format_func_df(option):
    return AVAILABLE_DATAFRAMES[option]


def format_fund(option):
    return FUND_SPECIFIC[option]


@st.cache
def get_data(ticker, attribute):
    try:
        data = getattr(ticker, attribute)()
    except TypeError:
        data = getattr(ticker, attribute)
    return data


def main():
    symbols = st.sidebar.text_input(
        "Enter symbol or list of symbols (comma separated)", value="aapl")
    symbols = [x.strip() for x in symbols.split(',')]
    yq = Ticker(symbols)

    page = st.sidebar.selectbox("Choose a page", [
        "Homepage", "Dictionaries", "Dataframes", "Option Chain",
        "Historical Pricing", "Mutual Funds"])

    st.title("Welcome to YahooQuery")

    if page == "Homepage":
        st.write("""
            Enter a symbol or list of symbols and select a page from the left
            to the data available to you.""")
        st.markdown("[View code here](https://github.com/dpguthrie/yahooquery)")
    elif page == "Dictionaries":
        st.header("Dictionaries")
        st.write("""
            Some data is returned as python dictionaries; use the dropdown
            below to view some of the data available to you through yahooquery.
        """)
        d_endpoint = st.selectbox(
            "Select Dictionary Endpoint",
            options=list(AVAILABLE_DICTIONARIES.keys()),
            format_func=format_func_dicts)
        with st.spinner():
            data = get_data(yq, d_endpoint)
            st.json(data)
    elif page == "Dataframes":
        st.header("Dataframes")
        st.write("""
            Some data is returned as pandas DataFrames; use the dropdown
            below to view some of the data available to you through yahooquery.
        """)
        df_endpoint = st.selectbox(
            "Select DataFrame Endpoint",
            options=list(AVAILABLE_DATAFRAMES.keys()),
            format_func=format_func_df)
        with st.spinner():
            data = get_data(yq, df_endpoint)
            st.write(data)
    elif page == "Option Chain":
        st.header("Option Chain")
        st.write("""
            Yahooquery also gives you the ability to view option chain data
            for all expiration dates for a given symbol(s)
        """)
        with st.spinner():
            data = get_data(yq, 'option_chain')
            st.write(data)
    elif page == "Historical Pricing":
        st.header("Historical Pricing")
        st.write("""
            Retrieve historical pricing data for a given symbol(s)
        """)
        st.markdown("""
            1. Select a period **or** enter start and end dates.  **This
               application defaults both start and end dates at today's
               date.  If you don't change them, None will be used for both.**
            2. Select interval (**note:  some intervals are not available for
                certain lengths of time**)
        """)
        period = st.selectbox(
            "Select Period", options=Ticker._PERIODS, index=5)
        st.markdown("**OR**")
        start = st.date_input("Select Start Date")
        end = st.date_input("Select End Date")
        st.markdown("**THEN**")
        interval = st.selectbox(
            "Select Interval", options=Ticker._INTERVALS, index=8)
        print(start==datetime.datetime.today().date())

        with st.spinner("Retrieving data..."):
            today = datetime.datetime.today().date()
            if start == today:
                start = None
            if end == today:
                end = None
            df = yq.history(
                period=period, interval=interval, start=start, end=end)

        if isinstance(df, dict):
            st.write(df)
        else:
            if len(symbols) > 1:
                chart = (
                    alt.Chart(df.reset_index()).mark_line().encode(
                        alt.Y('close:Q', scale=alt.Scale(zero=False)),
                        x='dates',
                        color='symbol'
                    )
                )
            else:
                chart = (
                    alt.Chart(df.reset_index()).mark_line().encode(
                        alt.Y('close:Q', scale=alt.Scale(zero=False)),
                        x='dates:T',
                    )
                )
            st.write("", "", chart)
            st.dataframe(df)
    else:
        st.header("Mutual Funds")
        st.write("""
            There's additional data available to mutual funds, etfs, etc.
            Use the dropdown below to view additional data available to these
            security types.
        """)
        fund_endpoint = st.selectbox(
            "Select Fund Endpoint",
            options=list(FUND_SPECIFIC.keys()),
            format_func=format_fund)
        with st.spinner():
            data = get_data(yq, fund_endpoint)
            st.write(data)


if __name__ == "__main__":
    main()