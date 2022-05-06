from .view_lib import *
import asyncio

def get_not_shortables():
    mongod = mongo("all_symbol", "td_not_shortable")
    not_shortables = pd.DataFrame(mongod.conn.table.find())
    return list(set(not_shortables.symbol.to_list()))

async def pair_trade_top():
    mongod = mongo("all_symbol","pair_trade_sharp_2021_500")
    candid = pd.DataFrame(mongod.conn.table.find({"Sharp_Ratio":{"$exists":True},
                                                  "Ticker_1":{"$nin":get_not_shortables()},"Ticker_2":{"$nin":get_not_shortables()}}))
    top_return = candid.describe().loc["75%","Avg_Return"]
    top_sharp = candid.describe().loc["75%","Sharp_Ratio"]

    candid = pd.DataFrame(mongod.conn.table.find({"End_Value":{"$gt":500},
                                                  "Sharp_Ratio":{"$gt":top_sharp},
                                                  "Avg_Return":{"$gt":top_return}}).sort("Sharp_Ratio",-1).limit(20))
    return candid



def load_view():

    st.title("Portfolio Stats")
    mongod = mongo("all_symbol", "minute_beta")
    tos = pd.DataFrame(mongod.conn.table.find({}, {"Refresh_Date": 1}).sort("Refresh_Date", -1).limit(1))[
        "Refresh_Date"].iloc[0]
    my_beta_mins = pd.DataFrame(mongod.conn.table.find({"Refresh_Date": tos}))

    st.dataframe(my_beta_mins)
    st.write("The sum Day VaR of this portfolio is {:.2f}".format((my_beta_mins.Day_VaR).sum()))
    st.write("The sum Minute VaR of this portfolio is {:.2f}".format((my_beta_mins.Mins_VaR).sum()))
    st.write("The Day ES of this portfolio is {:.2f}".format(es_day))
    st.write("The Minute ES of this portfolio is {:.2f}".format(es_mins))


    st.title('Pair Trade Candidate')

    candid = asyncio.run(pair_trade_top())
    st.dataframe(candid)

