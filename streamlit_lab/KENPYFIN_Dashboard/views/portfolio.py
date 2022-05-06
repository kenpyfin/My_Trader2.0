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


async def stats():
    robinhood = robingateway()

    hedge = robinhood.hedge()
    mongod = mongo("all_symbol", "minute_beta")
    tos = pd.DataFrame(mongod.conn.table.find({}, {"Refresh_Date": 1}).sort("Refresh_Date", -1).limit(1))[
        "Refresh_Date"].iloc[0]
    mb = pd.DataFrame(mongod.conn.table.find({"Refresh_Date": tos}))

    ## ES Calculation
    var_table_mins = []
    var_table_day = []
    for i in range(500, 0, -5):
        i = i / 1000.0
        beta_table = robinhood.get_my_position_beta_minute(sv=i)
        var_table_mins.append((i, beta_table.Mins_VaR.sum()))
        var_table_day.append((i, beta_table.Day_VaR.sum()))
    var_table_mins = pd.DataFrame(var_table_mins)
    var_table_day = pd.DataFrame(var_table_day)
    var_table_mins.columns = ["sv", "Mins_VaR"]
    var_table_day.columns = ["sv", "Day_VaR"]
    es_mins = var_table_mins["Mins_VaR"].mean()
    es_day = var_table_day["Day_VaR"].mean()
    return mb, es_mins, es_day

def load_view():

    st.title("Portfolio Stats")
    my_beta_mins, es_mins, es_day = asyncio.run(stats())

    st.dataframe(my_beta_mins)
    st.write("The sum Day VaR of this portfolio is {:.2f}".format((my_beta_mins.Day_VaR).sum()))
    st.write("The sum Minute VaR of this portfolio is {:.2f}".format((my_beta_mins.Mins_VaR).sum()))
    st.write("The Day ES of this portfolio is {:.2f}".format(es_day))
    st.write("The Minute ES of this portfolio is {:.2f}".format(es_mins))


    st.title('Pair Trade Candidate')

    candid = asyncio.run(pair_trade_top())
    st.dataframe(candid)


