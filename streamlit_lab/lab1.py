import sys,os
sys.path.append(os.path.dirname(os.getcwd()))
from my_libs_py3 import *
pd.set_option("display.max_rows",100)
import streamlit as st

st.title("Stock Screener Table")

mongod = mongo("all_symbol","screener")
## This line gets the max refresh_date
tos = pd.DataFrame(mongod.conn.table.find({},{"Refresh_Date":1}).sort("Refresh_Date",-1).limit(1))["Refresh_Date"].iloc[0]
all_ticker = pd.DataFrame(mongod.conn.table.find({"Refresh_Date":tos}))
all_ticker = all_ticker[all_ticker.Volume > all_ticker.Volume.quantile(0.5)]
all_ticker = all_ticker[all_ticker["Institutional Ownership"] > all_ticker["Institutional Ownership"].quantile(0.5)]
all_ticker = all_ticker.drop("_id",axis=1)

st.selectbox("Display Columns",)


st.dataframe(all_ticker,height=500)

st.title("Financial Statement Lookup")

ticker = st.text_input("Ticker you want to lookup", "AAPL")

st.write( financial_statements_growth(ticker,"quarter"))

