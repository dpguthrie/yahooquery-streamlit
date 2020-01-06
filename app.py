import sys
import streamlit as st
import altair as alt
from yahooquery import Ticker
import datetime


BASE_ENDPOINTS = {
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
    'summary_profile': 'Summary Profile',
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
    'sec_filings': 'SEC Filings',
    'fund_bond_holdings': 'Fund Bond Holdings',
    'fund_bond_ratings': 'Fund Bond Ratings',
    'fund_equity_holdings': 'Fund Equity Holdings',
    'fund_holding_info': 'Fund Holding Information',
    'fund_performance': 'Fund Performance',
    'fund_sector_weightings': 'Fund Sector Weightings',
    'fund_top_holdings': 'Fund Top Holdings',
}

def format_func(option):
    return BASE_ENDPOINTS[option]


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
    tickers = Ticker(symbols)

    page = st.sidebar.selectbox("Choose a page", [
        "Homepage", "Base", "Options", "Historical Pricing"])

    st.markdown("# Welcome to [YahooQuery](https://github.com/dpguthrie/yahooquery)")

    if page == "Homepage":
        st.markdown("""
            ## Streamlit

            ### Instructions
            Enter a symbol or list of symbols in the box to the left (**comma
            separated**).  Then select different pages in the dropdown to view
            the data available to you.

            ### Data
            The data is broken up into three different pages:  Base, Options,
            and Historical Pricing.  These correspond to three different urls
            the package utilizes to retrieve data.

            ## Short ReadMe

            ### Install
            ```python
            pip install yahooquery
            ```

            ### Ticker
            The `Ticker` class provides the access point to data residing on
            Yahoo Finance.  It accepts either a symbol or list of symbols.
            Additionally, you can supply `formatted` as a keyword argument
            to the class to format the data returned from the API (default is
            `True`)

            ```python
            from yahooquery import Ticker

            aapl = Ticker('aapl')
            # or
            tickers = Ticker(['aapl', 'msft', 'fb'])
            ```
        """)
        st.help(tickers)
    elif page == "Base":
        st.header("Base Endpoints")
        st.write("""
            Select an option below to see the data available through
            the base endpoints.""")
        endpoint = st.selectbox(
            "Select Endpoint", options=sorted(list(BASE_ENDPOINTS.keys())),
            format_func=format_func)
        st.help(getattr(Ticker, endpoint))
        st.code(f"Ticker({symbols}).{endpoint}", language="python")
        with st.spinner():
            data = get_data(tickers, endpoint)
            st.write(data)
    elif page == "Options":
        st.header("Option Chain")
        st.help(getattr(Ticker, 'option_chain'))
        st.code(f"Ticker({symbols}).option_chain", language="python")
        st.write("""
            Yahooquery also gives you the ability to view option chain data
            for all expiration dates for a given symbol(s)
        """)
        with st.spinner():
            data = get_data(tickers, 'option_chain')
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
            df = tickers.history(
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


if __name__ == "__main__":
    main()