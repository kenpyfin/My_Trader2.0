import streamlit as st


def pair_trade_top():
    mongod = mongo("all_symbol","pair_trade_sharp_2021_500")
    candid = pd.DataFrame(mongod.conn.table.find({"Sharp_Ratio":{"$exists":True},
                                                  "Ticker_1":{"$nin":get_not_shortables()},"Ticker_2":{"$nin":get_not_shortables()}}))
    top_return = candid.describe().loc["75%","Avg_Return"]
    top_sharp = candid.describe().loc["75%","Sharp_Ratio"]

    candid = pd.DataFrame(mongod.conn.table.find({"End_Value":{"$gt":TRADE_CASH},
                                                  "Sharp_Ratio":{"$gt":top_sharp},
                                                  "Avg_Return":{"$gt":top_return}}).sort("Sharp_Ratio",-1).limit(20))
    return candid


def load_view():    
    st.title('About Page')