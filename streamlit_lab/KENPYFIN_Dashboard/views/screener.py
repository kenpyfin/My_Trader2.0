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
    candid = candid.drop("_id", axis=1)
    return candid

@st.cache(ttl=1800)
def ranking_model(limit=50):
    mongod = mongo("all_symbol", "screenerModel")

    ## This line gets the max refresh_date
    tos = pd.DataFrame(mongod.conn.table.find({}, {"Refresh_Date": 1, "_id": 0}).sort("Refresh_Date", -1).limit(1))[
        "Refresh_Date"].iloc[0]

    fun_table = pd.DataFrame(mongod.conn.table.find({"Refresh_Date": tos}, {"_id": 0}))

    target = ["P/Cash", "Analyst Recom", "P/S", "Total Debt/Equity", "P/Free Cash Flow", "P/E", "Insider Ownership",
              "Gross Margin", "Current Ratio", "Sales growth quarter over quarter", "Profit Margin", "Quick Ratio",
              "Performance (Week)", "Institutional Ownership", "EPS (ttm)", "Operating Margin"]

    fun_table["sum_rank"] = pd.DataFrame.sum(fun_table[target], axis=1, skipna=True, numeric_only=True)

    fun_table["avg_rank"] = pd.DataFrame.mean(fun_table[target], axis=1, skipna=True, numeric_only=True)

    # fun_table = fun_table.sort_values("avg_rank")

    for i in fun_table.index:
        relative_rank = fun_table.loc[i, "avg_rank"] / fun_table.loc[
            fun_table.Sector == fun_table.loc[i, "Sector"], "Sector"].count()
        #     relative_rank = fun_table.loc[i,"avg_rank"]/fun_table.loc[fun_table.Sector == fun_table.loc[i,"Sector"],"Market Cap"].mean()
        #     relative_rank = fun_table.loc[i,"avg_rank"]*(1- (1/fun_table.loc[fun_table.Sector == fun_table.loc[i,"Sector"],"Market Cap"].mean()))
        #     relative_rank = fun_table.loc[i,"avg_rank"]/fun_table.loc[fun_table.Sector == fun_table.loc[i,"Sector"],"Market Cap"].mean()

        fun_table.loc[i, "relative_rank"] = relative_rank
    #     fun_table.loc[i,"relative_rank"] = fun_table.loc[i,"avg_rank"]

    fun_table = fun_table.sort_values("relative_rank")
    return fun_table[:limit]

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


    st.title('Pair Trade Candidate')

    candid = asyncio.run(pair_trade_top())
    st.dataframe(candid)

    table = ranking_model()
    st.title("Stock Ranking Model")
    cols_ticker = st.multiselect("Display Columns", table.columns)
    with st.expander("Filters"):
        col1, col2 = st.columns(2)
        with col1:
            filter1 = st.multiselect("Industry", table.Industry.unique(), default=table.Industry.unique())
        with col2:
            filter2 = st.multiselect("Sector", table.Sector.unique(), default=table.Sector.unique())
    st.dataframe(table[(table.Sector.isin(filter2)) & \
                            (table.Industry.isin(filter1))
                            ][cols_ticker], height=500)

