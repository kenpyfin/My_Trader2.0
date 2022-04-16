from .my_libs_py3 import *
from .my_libs_py3.habitica import *


def longTermInvest():
    # TODO
    # market economy check
    target_list = trading_param["longterm_target_ticker"]
    
    robinhood = robingateway()

    ##  Check buy signal
    # check we have enough buying power after reserver
    if robinhood.get_buying_power() > trading_param["cash_reserve"]:
        for i in target_list:
            price = get_price_data([i],method = 'day',back_day=20)
            quote = realtimequote(i).price.iloc[0]

            # TODO
            # can add the price range condition here for buying and use database instead of json
            if quote < price.Close.mean():
                size = np.ceil((trading_param["longterm_bench_money"]*trading_param["longterm_bench_money_increase_factor"])/quote)

            else:
                size = np.ceil((trading_param["longterm_bench_money"]*trading_param["longterm_bench_money_decrease_factor"])/quote)
            # TODO
            # place vwap price
            if robinhood.place_buy_bulk_checkup(ticker_list=[i],quantity_list=[size],skip_check= True) == "Trade Success!":
                log_trade(i,size, robinhood.get_last_price(i), strategy_name)
                send_email("Fundamental Cumulation Buy: %s"%i)

    print("pass buy signal")

    ##  Check sell signal
    tickers = get_open_opsition()

    for i in tickers:
        if i not in target_list:
            continue
        log = get_trade_log(i)
        log = log[log.Strategy==strategy_name]
        if len(log) == 0:
            continue

        quote = realtimequote(i).price.iloc[0]

        try:
            cost = robinhood.get_average_cost(i)
        except:
            send_email("%s not in portfolio"%i)
            continue
        print("pass log check")

        ## clean a portion of the position if it reaches the havest threshold    
        size = np.ceil(log["size"].sum()*trading_param["longterm_harvest_prop"])    
        if (quote - cost)/cost > trading_param["longterm_harvest"]:
            if robinhood.place_sell_bulk_checkup(ticker_list=[i],quantity_list=[size])== "Trade Success!":
                log_trade(i,-size, robinhood.get_last_price(i), strategy_name)
                send_email("Fundamental Cumulation Sell: %s"%i)

        print("pass fundamental")