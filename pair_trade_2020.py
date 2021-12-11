from my_libs_py3 import *
import multiprocessing

########################
# Screen for candidate of momentum trade
########################

def pair_screen(start,end):
    for i in ALL_TICKER[start:end]:
        for j in ALL_TICKER:
            if i == j:
                continue
            # mongod = mongo("all_symbol")
            # get = mongod.conn.get_data("select * from all_symbol.pair_trade_screen_save where ticker_1 = '%s' and ticker_2 = '%s'"%(i,j))
            # if len(get) > 0:
            #     continue

            if i in TICKER_1 and j in TICKER_2:
                continue

            try:
                # test if the stock has volume
                volume1 = get_price_data([i], robinhood=robinhood, method=trade_scale).Volume.iloc[0]
                volume2 = get_price_data([j], robinhood=robinhood, method=trade_scale).Volume.iloc[0]

                # test if stock has in house data
                try:
                    price1 = get_price_data([i], robinhood=robinhood, method=trade_scale,
                                            back_day=backdays).Return.fillna(method="bfill")
                    price2 = get_price_data([j], robinhood=robinhood, method=trade_scale,
                                            back_day=backdays).Return.fillna(method="bfill")
                except:
                    # set to the same length
                    print("no data, using realtime method")
                    price1 = get_price_data([i], method="realtimeday", robinhood=robinhood,
                                            back_day=backdays).Return.fillna(method="bfill")
                    price2 = get_price_data([j], method="realtimeday", robinhood=robinhood,
                                            back_day=backdays).Return.fillna(method="bfill")

                # test if stock has same length of historical data
                if len(price2) != len(price1):
                    print("*****")
                    print("price1 and price2 not the same length")
                    mongod = mongo("all_symbol", "pair_not_same_length")
                    mongod.conn.frame_to_mongo(pd.DataFrame([(i, j, len(price1), len(price2), today)],
                                                            columns=["Ticker_1", "Ticker_2", "T1_Len", "T2_Len",
                                                                     "Refresh_Date"]))

                    price1 = get_price_data([i], method="realtimeday", robinhood=robinhood,
                                            back_day=backdays).Return.fillna(method="bfill")
                    price2 = get_price_data([j], method="realtimeday", robinhood=robinhood,
                                            back_day=backdays).Return.fillna(method="bfill")

                cor, pval = scipy.stats.pearsonr(np.array(price1), np.array(price2))
                mongod = mongo("all_symbol", "pair_trade_screen_save")
                mongod.frame_to_mongo(pd.DataFrame([(i, j, round(cor, 4), round(pval, 4), today)],
                                                   columns=["Ticker_1", "Ticker_2", "Per_Cor", "P_Val",
                                                            "Refresh_Date"]))

                print("Cor:%s,P_Val:%s" % (round(cor, 4), round(pval, 4)))

                if volume1 != None and volume2 != None and cor > 0.5 and pval < 0.05:
                    print("start")
                    end_value, avg_retrun, sharpratio, min_return, max_return = backtest_pair(i, j, capital=2000,
                                                                                              method=trade_scale,
                                                                                              back_day=80, window=5)
                    temp = pd.DataFrame([(i, j, end_value, avg_retrun, sharpratio, min_return, max_return)] \
                                        , columns=["Ticker_1", "Ticker_2", "End_Value", "Avg_Return", "Sharp_Ratio",
                                                   "Min_Return", "Max_Return"])
                    temp["Refresh_Date"] = today
                    result = result.append(temp)
                    mongod = mongo("all_symbol", "pair_trade_sharp")
                    mongod.conn.frame_to_mongo(temp)

            except Exception as e:
                print("--------------")
                print(e)
                print("--------------")





## multiprocessing




if __name__ == "__main__":
    # try:

    mongod = mongo("all_symbol", "screener")
    ## This line gets the max refresh_date
    tos = pd.DataFrame(mongod.conn.table.find({}, {"Refresh_Date": 1}).sort("Refresh_Date", -1).limit(1))[
        "Refresh_Date"].iloc[0]
    ALL_TICKER = pd.DataFrame(mongod.conn.table.find({"Refresh_Date": tos}))

    # ## Initialization
    # mongod.conn.conn.cursor().execute("truncate table all_symbol.pair_trade_sharp")
    # mongod.conn.conn.cursor().execute("truncate table all_symbol.pair_trade_screen_save")
    # mongod.conn.conn.commit()

    # ALL_TICKER = pd.DataFrame(mongod.db["cantrade"].find()).Ticker.tolist()
    result = pd.DataFrame()

    ALL_TICKER = ALL_TICKER[ALL_TICKER.Volume > ALL_TICKER.Volume.quantile(0.5)]
    ALL_TICKER = ALL_TICKER[ALL_TICKER["Institutional Ownership"] > ALL_TICKER["Institutional Ownership"].quantile(0.5)]

    ALL_TICKER = ALL_TICKER.Ticker.to_list()

    today = datetime.today().date()
    robinhood = robingateway()
    trade_scale = "day"
    backdays = 80

    mongod = mongo("all_symbol", "pair_trade_screen_save")
    get = pd.DataFrame(mongod.conn.table.find({}, {"Ticker_1": 1, "Ticker_2": 1}))
    TICKER_1 = get.Ticker_1.to_list()
    TICKER_2 = get.Ticker_2.to_list()

    ## CP Id
    START = 0
    END = len(ALL_TICKER)
    n_thread = 5
    steps = int((START-END )/ n_thread)
    print ("each length:%s"%steps)
    # pro = multiprocessing.get_context("spawn")
    with multiprocessing.Pool(n_thread) as pool:
        pool.starmap(pair_screen(),
                 [(start,start+steps) for start in range(START,END,steps)])



send_email("Finished screen for momentum trade")

# except Exception as e:
#     send_email("Error! screen for momentum trade: %s"%str(e))
