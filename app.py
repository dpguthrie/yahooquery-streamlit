import datetime
from typing import Dict, List

import altair as alt
import streamlit as st
from yahooquery import Ticker
import plotly.graph_objects as go

BASE_MODULES = {
    "asset_profile": "Asset Profile",
    "calendar_events": "Calendar Events",
    "esg_scores": "ESG Scores",
    "financial_data": "Financial Data",
    "fund_profile": "Fund Profile",
    "key_stats": "Key Statistics",
    "major_holders": "Major Holders",
    "price": "Pricing",
    "quote_type": "Quote Type",
    "share_purchase_activity": "Share Purchase Activity",
    "summary_detail": "Summary Detail",
    "summary_profile": "Summary Profile",
    "balance_sheet": "Balance Sheet",
    "cash_flow": "Cash Flow",
    "company_officers": "Company Officers",
    "earning_history": "Earning History",
    "earnings": "Earnings",
    "earnings_trend": "Earnings Trend",
    "index_trend": "Index Trend",
    "sector_trend": "Sector Trend",
    "industry_trend": "Industry Trend",
    "fund_ownership": "Fund Ownership",
    "grading_history": "Grading History",
    "income_statement": "Income Statement",
    "insider_holders": "Insider Holders",
    "insider_transactions": "Insider Transactions",
    "institution_ownership": "Institution Ownership",
    "recommendation_trend": "Recommendation Trends",
    "sec_filings": "SEC Filings",
    "fund_bond_holdings": "Fund Bond Holdings",
    "fund_bond_ratings": "Fund Bond Ratings",
    "fund_equity_holdings": "Fund Equity Holdings",
    "fund_holding_info": "Fund Holding Information",
    "fund_performance": "Fund Performance",
    "fund_sector_weightings": "Fund Sector Weightings",
    "fund_top_holdings": "Fund Top Holdings",
}

PREMIUM = {
    "p_balance_sheet": "Balance Sheet",
    "p_cash_flow": "Cash Flow",
    "p_income_statement": "Income Statement",
    "p_company_360": "Company 360",
    "p_portal": "Premium Portal",
    "p_reports": "Research Reports",
    "p_ideas": "Trade Ideas",
    "p_technical_events": "Technical Events",
    "p_value_analyzer": "Value Analyzer",
    "p_value_analyzer_drilldown": "Value Analyzer Drilldown",
}


def format_func(option: str) -> str:
    """Convert the BASE_MODULES key to a value

    Arguments:
        option {str} -- The key identifying the module.

    Returns:
        str -- The value. A nice module name
    """
    return BASE_MODULES[option]


def format_premium(option: str) -> str:
    """Convert the PREMIUM key to a value

    Arguments:
        option {str} -- The key identifying the module.

    Returns:
        str -- The value. A nice module name
    """
    return PREMIUM[option]


@st.cache
def get_data(ticker: Ticker, attribute: str, *args) -> Dict:
    """Gets data from yahoo

    Arguments:
        ticker {Ticker} -- an instance of Ticker
        attribute {str} -- The attribute of Ticker to call. Will return the results of a call to
            corresponding yahoo finance endpoint.

    Returns:
        Dict -- A Dictionary of data from Yahoo
    """
    try:
        data = getattr(ticker, attribute)(*args)
    except TypeError:
        data = getattr(ticker, attribute)
    return data


@st.cache(allow_output_mutation=True)
def init_ticker(symbols, **kwargs):
    return Ticker(symbols, **kwargs)


def main():
    """Run this to run the application"""
    st.sidebar.subheader("YahooQuery")
    symbols = st.sidebar.text_input(
        "Enter symbol or list of symbols (comma, space separated)", value="aapl"
    )

    asynchronous = st.sidebar.radio(
        "Make Asynchronous requests?", options=[False, True]
    )
    asynchronous_str = "" if not asynchronous else ", asynchronous=True"

    formatted = st.sidebar.radio(
        "Format data returned from API", options=[False, True])
    formatted_str = "" if not formatted else ", formatted=True"

    username = st.sidebar.text_input(
        label="Username",
        value=""
    )

    password = st.sidebar.text_input(
        label="Password",
        value="",
        type="password"
    )

    tickers = init_ticker(
        symbols,
        formatted=formatted,
        asynchronous=asynchronous,
        username=username,
        password=password)

    page = st.sidebar.selectbox(
        "Choose a page", ["Homepage", "Modules", "Options", "Historical Pricing", "Premium"]
    )

    strings = {
        'formatted_str': formatted_str,
        'asynchronous_str': asynchronous_str,
        'username': username,
        'password': password
    }

    st.markdown("# Welcome to [YahooQuery](https://github.com/dpguthrie/yahooquery)")

    if page == "Homepage":
        homepage_view(tickers, symbols, strings)
    elif page == "Premium":
        premium_view(tickers, symbols, strings)
    elif page == "Modules":
        base_view(tickers, symbols, strings)
    elif page == "Options":
        options_view(tickers, symbols, strings)
    else:
        history_view(tickers, symbols, strings)


def homepage_view(tickers: Ticker, symbols: List[str], strings: dict):
    """Provides the view of the Home Page

    Arguments:
        tickers {Ticker} -- A yahaooquery Ticker object
        symbols {List[str]} -- A list of symbols
        strings {dict} -- Dictionary containing strings used in Ticker init
    """

    st.markdown(
        f"""
        This app demonstrates the use of the [YahooQuery]\
            (https://github.com/dpguthrie/yahooquery) package

        ### Instructions

        Enter a symbol or list of symbols in the box to the left.  Then select
        different pages in the dropdown to view the data available to you.

        ### Ticker Usage

        The `Ticker` class provides one of the access points to data residing on
        Yahoo Finance.  It accepts either a symbol or list of symbols.
        Additionally, you can supply `formatted` as a keyword argument
        to the class to return formatted data from the API (default is
        `False`).  Another keyword argument you can supply is `asynchronous`.
        This will allow the `Ticker` class to make asynchronous requests when
        multiple symbols are passed.  The default value is `False`.

        ```python
        from yahooquery import Ticker

        tickers = Ticker('{symbols}'{strings['formatted_str']}{strings['asynchronous_str']})
        ```
    """
    )
    st.help(tickers)


def premium_view(tickers: Ticker, symbols: List[str], strings: dict):
    """A view of the basic functionality of Ticker.

    The user can select a module and the help text, code and result will be presented.

    Arguments:
        tickers {Ticker} -- A yahaooquery Ticker object
        symbols {List[str]} -- A list of symbols
        strings {dict} -- Dictionary containing strings used in Ticker init
    """

    st.header("Premium Data")
    st.write(
        """
        Select an option below to see the premium data available"""
    )
    module = st.selectbox(
        "Select Data", options=sorted(list(PREMIUM.keys())), format_func=format_premium
    )
    st.help(getattr(Ticker, module))
    is_property = isinstance(getattr(Ticker, module), property)
    if is_property:
        st.code(f"Ticker('{symbols}'{strings['formatted_str']}{strings['asynchronous_str']}).{module}", language="python")
        data = get_data(tickers, module)
    else:
        frequency = st.selectbox("Select Frequency", options=["Annual", "Quarterly"])
        arg = frequency[:1].lower()
        st.code(f"Ticker('{symbols}'{strings['formatted_str']}{strings['asynchronous_str']}).{module}(frequency='{arg}')")
        data = get_data(tickers, module, arg)
    st.write(data)


def base_view(tickers: Ticker, symbols: List[str], strings: dict):
    """A view of the basic functionality of Ticker.

    The user can select a module and the help text, code and result will be presented.

    Arguments:
        tickers {Ticker} -- A yahaooquery Ticker object
        symbols {List[str]} -- A list of symbols
        strings {dict} -- Dictionary containing strings used in Ticker init
    """

    st.header("Modules")
    method = st.selectbox("Select Method", options=["Single Module", "Multiple Modules", "All Modules"])
    if method == "Single Module":
        module = st.selectbox(
            "Select Module", options=sorted(list(BASE_MODULES.keys())), format_func=format_func
        )
        st.help(getattr(Ticker, module))
        is_property = isinstance(getattr(Ticker, module), property)
        if is_property:
            st.code(f"Ticker('{symbols}'{strings['formatted_str']}{strings['asynchronous_str']}).{module}", language="python")
            data = get_data(tickers, module)
        else:
            frequency = st.selectbox("Select Frequency", options=["Annual", "Quarterly"])
            arg = frequency[:1].lower()
            st.code(f"Ticker('{symbols}'{strings['formatted_str']}{strings['asynchronous_str']}).{module}(frequency='{arg}')")
            data = get_data(tickers, module, arg)
        st.write(data)
    else:
        st.markdown(
            """
            Two methods to the `Ticker` class allow you to obtain multiple
            modules with one call.

            - the `get_modules` method takes a list
            of allowable modules, which you can view through `Ticker.MODULES`
            - the `all_modules` property retrieves all Base modules"""
        )
        if method == "All Modules":
            st.help(getattr(Ticker, "all_modules"))
            st.code(f"Ticker('{symbols}'{strings['formatted_str']}{strings['asynchronous_str']}).all_modules", language="python")
            data = get_data(tickers, "all_modules")
            st.json(data)
        else:

            default_modules = ["assetProfile"]
            modules = st.multiselect(
                "Select modules",
                options=sorted(Ticker.MODULES),  # pylint: disable=protected-access
                default=default_modules,
            )
            st.help(getattr(Ticker, "get_modules"))
            st.code(f"Ticker('{symbols}'{strings['formatted_str']}).get_modules({modules})", language="python")
            if not modules:
                st.warning("You must select at least one module")
            else:
                data = get_data(tickers, "get_modules")(modules)
                st.json(data)
    

# Ideas for Improvements
# Reset index to get column headers
# Buttons under Table to download data
# Some kind of chart that helps me understand the data/ get insights.
def options_view(tickers: Ticker, symbols: List[str], strings: dict):
    """Provides an illustration of the `option_chain` method

    Arguments:
        tickers {Ticker} -- A yahaooquery Ticker object
        symbols {List[str]} -- A list of symbols
    """
    st.header("Option Chain")
    st.write(
        """
        Yahooquery also gives you the ability to view [option chain]\
            (https://www.investopedia.com/terms/o/optionchain.asp) data for all expiration
            dates for a given symbol(s)
    """
    )
    st.code(f"Ticker('{symbols}'{strings['formatted_str']}{strings['asynchronous_str']}).option_chain", language="python")
    data = get_data(tickers, "option_chain")
    st.write(data)


def history_view(tickers: Ticker, symbols: List[str], strings: dict):
    """Provides an illustration of the `Ticker.history` method

    Arguments:
        tickers {Ticker} -- A yahaooquery Ticker object
        symbols {List[str]} -- A list of symbols
    """
    st.header("Historical Pricing")
    st.write(
        """
        Retrieve historical pricing data for a given symbol(s)
    """
    )
    st.help(getattr(Ticker, "history"))
    st.markdown(
        """
        1. Select a period **or** enter start and end dates.
        2. Select interval (**note:  some intervals are not available for
            certain lengths of time**)
    """
    )
    history_args = {
        "period": "1y",
        "interval": "1d",
        "start": datetime.datetime.now() - datetime.timedelta(days=365),
        "end": None,
    }
    option_1 = st.selectbox("Select Period or Start / End Dates", ["Period", "Dates"], 0)
    if option_1 == "Period":
        history_args["period"] = st.selectbox(
            "Select Period", options=Ticker.PERIODS, index=5  # pylint: disable=protected-access
        )

        history_args["start"] = None
        history_args["end"] = None
    else:
        history_args["start"] = st.date_input("Select Start Date", value=history_args["start"])
        history_args["end"] = st.date_input("Select End Date")
        history_args["period"] = None

    st.markdown("**THEN**")
    history_args["interval"] = st.selectbox(
        "Select Interval", options=Ticker.INTERVALS, index=8  # pylint: disable=protected-access
    )
    args_string = [str(k) + "='" + str(v) + "'" for k, v in history_args.items() if v is not None]
    st.code(f"Ticker('{symbols}'{strings['formatted_str']}{strings['asynchronous_str']}).history({', '.join(args_string)})", language="python")
    dataframe = tickers.history(**history_args)

    if isinstance(dataframe, dict):
        st.write(dataframe)
    else:
        if len(tickers.symbols) > 1:
            chart = (
                alt.Chart(dataframe.reset_index())
                .mark_line()
                .encode(alt.Y("adjclose:Q", scale=alt.Scale(zero=False)), x="date", color="symbol").properties(
                    width=660,
                    height=400
                )
            )
            st.write("", "", chart)
        else:
            fig = go.Figure(data=go.Ohlc(
                x=dataframe.index,
                open=dataframe['open'],
                high=dataframe['high'],
                low=dataframe['low'],
                close=dataframe['close']
            ))
            fig.layout.xaxis.type = 'category'
            st.plotly_chart(fig)
            
        st.dataframe(dataframe)


main()
