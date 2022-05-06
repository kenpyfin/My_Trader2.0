from .view_lib import *


def load_view():

    st.title("Stock Screener Table")

    mongod = mongo("all_symbol", "screener")
    ## This line gets the max refresh_date
    tos = pd.DataFrame(mongod.conn.table.find({}, {"Refresh_Date": 1}).sort("Refresh_Date", -1).limit(1))[
        "Refresh_Date"].iloc[0]
    all_ticker = pd.DataFrame(mongod.conn.table.find({"Refresh_Date": tos}))
    all_ticker = all_ticker[all_ticker.Volume > all_ticker.Volume.quantile(0.5)]
    all_ticker = all_ticker[all_ticker["Institutional Ownership"] > all_ticker["Institutional Ownership"].quantile(0.5)]
    all_ticker = all_ticker.drop("_id", axis=1)

    cols_ticker = st.multiselect("Display Columns", all_ticker.columns)
    with st.expander("Filters"):
        col1, col2 = st.columns(2)
        with col1:
            filter1 = st.multiselect("Industry", all_ticker.Industry.unique(),default=all_ticker.Industry.unique())
        with col2:
            filter2 = st.multiselect("Sector", all_ticker.Sector.unique(),default=all_ticker.Sector.unique())
    st.dataframe(all_ticker[(all_ticker.Sector.isin(filter2)) & \
                            (all_ticker.Industry.isin(filter1))
                     ][cols_ticker], height=500)


    st.title("Financial Statement Lookup")
    ## get all column name
    col_name_fs = financial_statements_growth("AAPL", "annual").columns
    col1, col2 = st.columns(2)
    with col1:
        ticker = st.text_input("Ticker you want to lookup", "AAPL")
    with col2:
        cols_fs = st.multiselect("Display Columns", col_name_fs)

    st.dataframe(financial_statements_growth(ticker, "quarter")[cols_fs],height=500,width=500)

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
    st.write(dcf(ticker,"quarter"))