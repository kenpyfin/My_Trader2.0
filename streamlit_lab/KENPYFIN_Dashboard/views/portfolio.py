from .view_lib import *
import asyncio

@st.cache(ttl=1800)
def mb():

    mongod = mongo("all_symbol", "minute_beta")
    tos = pd.DataFrame(mongod.conn.table.find({}, {"Refresh_Date": 1}).sort("Refresh_Date", -1).limit(1))[
        "Refresh_Date"].iloc[0]
    my_beta_mins = pd.DataFrame(mongod.conn.table.find({"Refresh_Date": tos}))
    my_beta_mins = my_beta_mins.drop("_id", axis=1)
    return my_beta_mins

@st.cache(ttl=1800)
def es():
    mongod = mongo("all_symbol", "var_es")
    tos = pd.DataFrame(mongod.conn.table.find({}, {"Refresh_Date": 1}).sort("Refresh_Date", -1).limit(1))[
        "Refresh_Date"].iloc[0]
    es = pd.DataFrame(mongod.conn.table.find({"Refresh_Date": tos}))
    es = es.drop("_id", axis=1)
    return es

@st.cache(ttl=1800)
def td_broker_action_item():
    shares = {}
    pos_split = pair_trade_log.get_pair_open_position()

    for pos in pos_split:
        myLog = pair_trade_log(pos[0], pos[1])
        for i, tic in enumerate(pos):
            if tic in shares.keys():
                shares[tic] += getattr(myLog, f"outstanding_shares_ticker{i + 1}")
            else:

                shares[tic] = getattr(myLog, f"outstanding_shares_ticker{i + 1}")

    open_position = client.current_positions()
    open_position = open_position.set_index("symbol")
    open_position = open_position.join(pd.DataFrame([shares], index=["log_size"]).T)
    open_position = open_position.dropna(subset=["log_size"])
    open_position["trade_action_diff"] = open_position.log_size - open_position.quantity

    return open_position


def load_view():
    st.title("Action needed to adjust pair trade manually")
    st.write("The trade_action_diff column is the number of shares need to trade to rebalance")
    st.dataframe(td_broker_action_item())

    st.title("Portfolio Stats")
    my_beta_mins = mb()
    st.dataframe(my_beta_mins)
    st.write("The sum Day VaR of this portfolio is {:.2f}".format((my_beta_mins.Day_VaR).sum()))
    st.write("The sum Minute VaR of this portfolio is {:.2f}".format((my_beta_mins.Mins_VaR).sum()))

    es_value = es()
    st.write("The Day ES of this portfolio is {:.2f}".format(es_value.es_day.iloc[0]))
    st.write("The Minute ES of this portfolio is {:.2f}".format(es_value.es_mins.iloc[0]))



