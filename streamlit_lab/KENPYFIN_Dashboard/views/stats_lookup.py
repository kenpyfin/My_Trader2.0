from .view_lib import *
import asyncio


def load_view():
    st.title("Financial Statement Lookup")
    ## get all column name
    col_name_fs = financial_statements_growth("AAPL", "annual").columns
    col1, col2 = st.columns(2)
    with col1:
        ticker = st.text_input("Ticker you want to lookup", "AAPL")
    with col2:
        cols_fs = st.multiselect("Display Columns", col_name_fs)

    st.dataframe(financial_statements_growth(ticker, "quarter")[cols_fs], height=500, width=500)

    st.title("Key Metric Lookup")
    ## get all column name
    col_name_fs = key_metrics("AAPL", "annual").columns
    col1, col2 = st.columns(2)
    with col1:
        ticker = st.text_input("Ticker you want to lookup for key metric", "AAPL")
    with col2:
        cols_fs = st.multiselect("Display Columns", col_name_fs)

    st.dataframe(key_metrics(ticker, "quarter")[cols_fs], height=500, width=500)

    st.title("Stock Peer")
    ticker = st.text_input("Ticker you want to lookup for stock peer", "AAPL")
    st.write(stock_peer(ticker))

    st.title("DCF")
    ticker = st.text_input("Ticker you want to lookup for dcf", "AAPL")
    st.write(dcf(ticker, "quarter"))