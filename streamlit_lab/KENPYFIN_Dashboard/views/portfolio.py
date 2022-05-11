from .view_lib import *
import asyncio

@st.cache(ttl=1800)
def mb():
    st.title("Portfolio Stats")
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


def load_view():
    my_beta_mins = mb()
    st.dataframe(my_beta_mins)
    st.write("The sum Day VaR of this portfolio is {:.2f}".format((my_beta_mins.Day_VaR).sum()))
    st.write("The sum Minute VaR of this portfolio is {:.2f}".format((my_beta_mins.Mins_VaR).sum()))


    es_value = es()
    st.write("The Day ES of this portfolio is {:.2f}".format(es_value.es_day.iloc[0]))
    st.write("The Minute ES of this portfolio is {:.2f}".format(es_value.es_mins.iloc[0]))



