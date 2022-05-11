from .my_libs_py3 import *

TRADE_CASH = 500

def record_not_shortable(ticker):
    mongod = mongo("all_symbol","td_not_shortable")
    mongod.conn.table.insert_one({"TimeStamp":datetime.now(),"symbol":ticker})

def get_not_shortables():
    mongod = mongo("all_symbol", "td_not_shortable")
    not_shortables = pd.DataFrame(mongod.conn.table.find())
    return list(set(not_shortables.symbol.to_list()))

def pair_trade_action(ticker1,ticker2,cash=TRADE_CASH,close_action=False):
    today_trade = self_pair_trade(ticker1,ticker2,method = "realtimeday",cash = cash).iloc[-1]

    # ticker_combo = ticker1+"_"+ticker2
    myLog = pair_trade_log(ticker1,ticker2)

    # day_diff = log["TimeStamp"].astimezone(mytz) - datetime.now(mytz)

    new_size1 = today_trade["size1"]
    new_size2 = today_trade["size2"]

    current_size1 = myLog.outstanding_shares_ticker1
    current_size2 = myLog.outstanding_shares_ticker2

    trade_size1 = new_size1 - current_size1
    trade_size2 = new_size2 - current_size2

    now_cash = client.accountsDF().loc[0,"currentBalances.availableFunds"]
    try:
        td_trade = order_equity(order_type.LIMIT)

        ## need to trade the short sell first to test whether it's shortable or not
        ## check signal
        if (trade_size1 != 0 or trade_size2 != 0) and (now_cash>TRADE_CASH or close_action):
            send_email("",title="!Important! Pair Trade Order Placing for %s and %s"%(ticker1,ticker2))
            ## if one of them trade_size == 0
            if trade_size1 == 0:
                orderid = td_trade.place(ticker2, trade_size2)
                if get_order_by_id(orderid)["status"] != "REJECTED":
                    log_pair_trade(ticker1, ticker2, trade_size1, trade_size2, None, None)
                    send_email("Trade process done.",
                               title="!Important! Pair Trade Order Placed for %s and %s" % (ticker1, ticker2))
                else:
                    # if not cancel_order(orderid):
                    #     send_email("Please manually cancel order for %s",
                    #                title="!Important! Cancel Order Failed" % orderid)
                    raise Exception("{ticker2} not filled for {ticker1} and {ticker2}".format(ticker1=ticker1,
                                                                                                    ticker2=ticker2))
            elif trade_size2 == 0:
                orderid = td_trade.place(ticker1, trade_size1)
                if get_order_by_id(orderid)["status"] != "REJECTED":
                    log_pair_trade(ticker1, ticker2, trade_size1, trade_size2, None, None)
                    send_email("Trade process done.",
                               title="!Important! Pair Trade Order Placed for %s and %s" % (ticker1, ticker2))
                else:
                    # if not cancel_order(orderid):
                    #     send_email("Please manually cancel order for %s",
                    #                title="!Important! Cancel Order Failed" % orderid)
                    raise Exception("{ticker1} not filled for {ticker1} and {ticker2}".format(ticker1=ticker1,
                                                                                                    ticker2=ticker2))
            ## short ticker1
            elif trade_size1 < 0:
                orderid = td_trade.place(ticker1,trade_size1)
                if get_order_by_id(orderid)["status"] != "REJECTED":
                    time.sleep(45)
                    if get_order_by_id(orderid)["status"] == "FILLED":
                        orderid = td_trade.place(ticker2,trade_size2)
                        if get_order_by_id(orderid)["status"] != "REJECTED":
                            log_pair_trade(ticker1,ticker2,trade_size1,trade_size2,None,None)
                            send_email("Trade process done.",title="!Important! Pair Trade Order Placed for %s and %s"%(ticker1,ticker2))
                    else:
                        if not cancel_order(orderid):
                            send_email("Please manually cancel order for %s",title="!Important! Cancel Order Failed"%orderid)
                        raise Exception("{ticker2} short not filled for {ticker1} and {ticker2}".format(ticker1=ticker1,ticker2=ticker2))
                        
                else:
                    record_not_shortable(ticker1)
                    raise Exception("{ticker1} probably not shortable for {ticker1} and {ticker2}".format(ticker1=ticker1,ticker2=ticker2))
            
            ## long ticker1
            elif trade_size1 > 0:
                orderid = td_trade.place(ticker2,trade_size2)
                if get_order_by_id(orderid)["status"] != "REJECTED":
                    time.sleep(45)
                    if get_order_by_id(orderid)["status"] == "FILLED":
                        orderid = td_trade.place(ticker1,trade_size1)
                        if get_order_by_id(orderid)["status"] != "REJECTED":
                            log_pair_trade(ticker1,ticker2,trade_size1,trade_size2,None,None)
                            send_email("Trade process done.",title="!Important! Pair Trade Order Placed for %s and %s"%(ticker1,ticker2))
                    else:
                        if not cancel_order(orderid):
                            send_email("Please manually cancel order for %s",title="!Important! Cancel Order Failed"%orderid)
                        raise Exception("{ticker1} short not filled for {ticker1} and {ticker2}".format(ticker1=ticker1,ticker2=ticker2))
                        
                else:
                    record_not_shortable(ticker2)
                    raise Exception("{ticker2} probably not shortable for {ticker1} and {ticker2}".format(ticker1=ticker1,ticker2=ticker2))
        ## no signal to trade   
        else:
            print("No trade or no cash, skiped for %s and %s"%(ticker1,ticker2))
    except Exception as e:
        send_email(str(e),title="!Important! Pair Trade Place Order Error for {ticker1} and {ticker2}".format(ticker1=ticker1,ticker2=ticker2))

def pair_trade_sample():
    mongod = mongo("all_symbol","pair_trade_sharp_2021_500")
    candid = pd.DataFrame(mongod.conn.table.find({"Sharp_Ratio":{"$exists":True}}))
    top_return = candid.describe().loc["75%","Avg_Return"]
    top_sharp = candid.describe().loc["75%","Sharp_Ratio"]

    pipeline = [
        {"$match":{"End_Value":{"$gt":TRADE_CASH},"Sharp_Ratio":{"$gt":top_sharp},"Avg_Return":{"$gt":top_return}}},
        {"$sample":{"size":10}}
    ]

    candid = pd.DataFrame(mongod.conn.table.aggregate(pipeline))
    candid = candid.drop_duplicates("Ticker_1").drop_duplicates("Ticker_2")
    candid = candid[~candid.Ticker_1.isin(candid.Ticker_2.to_list())]

    return candid

def pair_trade_top():
    mongod = mongo("all_symbol", "pair_trade_sharp_2021_500")
    candid = pd.DataFrame(mongod.conn.table.find({"Sharp_Ratio": {"$exists": True},
                                                  "Ticker_1": {"$nin": get_not_shortables()},
                                                  "Ticker_2": {"$nin": get_not_shortables()}}))
    top_return = candid.describe().loc["75%", "Avg_Return"]
    top_sharp = candid.describe().loc["75%", "Sharp_Ratio"]

    candid = pd.DataFrame(mongod.conn.table.find({"End_Value": {"$gt": 500},
                                                  "Sharp_Ratio": {"$gt": top_sharp},
                                                  "Avg_Return": {"$gt": top_return}}).sort("Sharp_Ratio", -1).limit(35))
    candid = candid.drop_duplicates("Ticker_1").drop_duplicates("Ticker_2")

    candid = candid[~candid.Ticker_1.isin(candid.Ticker_2.to_list())]

    return candid



def flat_position_by_days(ticker1,ticker2,days=7):
    try:
        myLog = pair_trade_log(ticker1,ticker2)
        # tradeLog = mongo("pair_trade_log", f"{ticker1}_{ticker2}")
        # myLog = pd.DataFrame(tradeLog.conn.table.find())
        ## It's negative here
        total_size1 = -myLog.outstanding_shares_ticker1
        total_size2 = -myLog.outstanding_shares_ticker2

        # lastTrade = myLog.sort_values("TimeStamp", ascending=True).iloc[-1]["TimeStamp"]
        lastTrade = myLog.last_trade_at

        td_trade = order_equity(order_type.LIMIT)
        if datetime.now(tz=lastTrade.tz)-lastTrade > timedelta(days=days):
            orderid = td_trade.place(ticker1, total_size1)
            if get_order_by_id(orderid)["status"] != "REJECTED":
                time.sleep(60)
                # if get_order_by_id(orderid)["status"] == "FILLED":
                orderid = td_trade.place(ticker2, total_size2)
                if get_order_by_id(orderid)["status"] != "REJECTED":
                    send_email("Trade process done.",
                               title="!Important! Pair Trade flat action Order Placed for %s and %s" % (ticker1, ticker2))
            else:
                if not cancel_order(orderid):
                    send_email("Please manually cancel order for %s for flat action",
                               title="!Important! Cancel Order Failed" % orderid)
                raise Exception("{ticker2} short not filled for \
                        {ticker1} and {ticker2} for a flat action".format(ticker1=ticker1,ticker2=ticker2))
            pair_trade_log.log_pair_trade(ticker1, ticker2,total_size1 , total_size2, None,
                   None)
            return "flatted"
    except Exception as e:
        send_email(str(e),
                   title="!Important! Pair Trade Place Order Error for {ticker1} and {ticker2}".format(ticker1=ticker1,
                                                                                                   ticker2=ticker2))



def pair_trade_action_main():


    # buy check
    candid = pair_trade_top()

    for ticker1, ticker2 in zip(candid.Ticker_1,candid.Ticker_2):
        pair_trade_action(ticker1,ticker2,cash=TRADE_CASH)
    ## position adjustment
    pos = pair_trade_log.get_pair_open_position()
    for p in pos:
        ticker1 = p[0]
        ticker2 = p[1]
        if flat_position_by_days(ticker1,ticker2) != "flatted":
            pair_trade_action(ticker1, ticker2, close_action=True)
