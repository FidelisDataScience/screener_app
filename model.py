class screener:
 

    def __init__(self, stock="NSE"):
        
        self.stock = stock 


    def computeRSI (self, X, time_window):
        import pandas as pd
        import numpy as np
        import datetime as dt
        import yfinance as yf
        from pandas_datareader import data as pdr

        data = X.copy()
        diff = data.diff(1).dropna()        # diff in one field(one day)

        #this preservers dimensions off diff values
        up_chg = 0 * diff
        down_chg = 0 * diff

        # up change is equal to the positive difference, otherwise equal to zero
        up_chg[diff > 0] = diff[ diff>0 ]

        # down change is equal to negative deifference, otherwise equal to zero
        down_chg[diff < 0] = diff[ diff < 0 ]

        # check pandas documentation for ewm
        # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.ewm.html
        # values are related to exponential decay
        # we set com=time_window-1 so we get decay alpha=1/time_window
        up_chg_avg   = up_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
        down_chg_avg = down_chg.ewm(com=time_window-1 , min_periods=time_window).mean()

        rs = abs(up_chg_avg/down_chg_avg)
        rsi = 100 - 100/(1+rs)
        return rsi

    def screen(self):
        import pandas as pd
        import numpy as np
        import datetime as dt
        import yfinance as yf
        from pandas_datareader import data as pdr
        
        # yfinance workaround
        yf.pdr_override()

        # ask the user what stock they want to lookup
        stocklist = pd.read_csv('ind_nifty500list.csv')

        stocks = [stocklist['Symbol'][i] + ".NS" for i in range(len(stocklist))]


        stocks_50 = stocks[:50]

        # dates
        start_year = 2015
        start_month = 1
        start_day = 1

        start = dt.datetime(start_year, start_month, start_day)

        # end
        now = dt.datetime.now()

        now = now.date()

        print("Extracting nifty500...")

        nifty500 = pdr.get_data_yahoo('^CRSLDX', start, now)
        nifty500["pct_change"] = nifty500['Adj Close'].pct_change()
        nifty_pct_change = nifty500["pct_change"][-1]

        ranks = []
        cmp = []
        stock_list = []
        rps = []
        betas = []
        sma_5 = []
        sma_20 = []
        rsi_list = []
        price_pct_change_list = []
        vol_pct_change_list = []
        sma_5_pct_change_list = []
        sma_20_pct_change_list = []

        stock_count_dict = {}

        for stock in stocks:

            print(".\n.\n.\n")
            print(f"Extracting {stock}...")

            df = pdr.get_data_yahoo(stock, start, now)

            print(f"Checking {stock}...")


            sma_list = [5, 10, 20]

            # calculating moving averages
            for sma in sma_list:
                df["SMA_" + str(sma)] = round(df.iloc[:, 4].rolling(window=sma).mean(), 2)

            # exponential moving averages
            emas_used = [12, 26, 200]

            for x in emas_used:
                ema = x
                df["EMA_"+str(ema)] = round(df.iloc[:, 4].ewm(span=ema, adjust=False).mean(), 2)


            try:

                # ranking
                current_stock_price = df['Adj Close'][-1]
                current_nifty_price = nifty500['Adj Close'][-1]
                relative_strength = current_stock_price / current_nifty_price
                moving_average_10 = df['SMA_10'][-1]
                moving_average_20 = df['SMA_20'][-1]
                rank = relative_strength / moving_average_10
                # print("Check-1")

                # change 5SMA, 20SMA
                df["SMA_5_pct_change"] = df['SMA_5'].pct_change()
                sma_5_pct_change = df["SMA_5_pct_change"][-1]
                df["SMA_20_pct_change"] = df['SMA_20'].pct_change()
                sma_20_pct_change = df["SMA_20_pct_change"][-1]
                # print("Check-2")

                # caluclating percentages and beta
                df['price_pct_change'] = df['Adj Close'].pct_change()
                df['vol_pct_change'] = df['Volume'].pct_change()

                price_pct_change = df['price_pct_change'][-1]
                vol_pct_change = df['vol_pct_change'][-1]


                beta = np.cov(df['price_pct_change'].iloc[-20:].values, nifty500["pct_change"].iloc[-20:].values)[1, 0] / np.var(df['price_pct_change'].iloc[-20:].values)

                # print("Check-3")

                # condition 1: stock price > 200 SMA
                moving_average_5 = df['SMA_5'][-1]
                moving_average_200 = df['EMA_200'][-1]

                if current_stock_price > moving_average_200:
                    cond1 = True
                else:
                    cond1 = False
                # print("Check-4")
                # condition 2: macd > 0
                ema_12 = df['EMA_12']
                ema_26 = df['EMA_26']
                df['MACD'] = ema_12 - ema_26
                macd = df['MACD'][-1]

                if macd > 0:
                    cond2 = True
                else:
                    cond2 = False

                # print("Check-5")
                # condition 3: RSI(14) > 50
                df['RSI_14'] = self.computeRSI(df['Adj Close'], 14)

                rsi = df['RSI_14'][-1]

                # print(rsi)
                if rsi > 50:
                    cond3 = True
                else:
                    cond3 = False

                # condition 4: Signal line > 0
                df['Signal'] = round(df['MACD'].ewm(span=9, adjust=False).mean(), 2)
                signal = df['Signal'][-1]

                if signal > 0:
                    cond4 = True
                else:
                    cond4 = False
                # print("Check-6")
                if cond1 and cond2 and cond3 and cond4:
                    cmp.append(current_stock_price)
                    ranks.append(rank)
                    stock_list.append(stock)
                    rsi_list.append(rsi)
                    sma_5.append(moving_average_5)
                    sma_20.append(moving_average_20)
                    price_pct_change_list.append(price_pct_change*100)
                    vol_pct_change_list.append(vol_pct_change*100)
                    betas.append(beta)
                    sma_5_pct_change_list.append(sma_5_pct_change)
                    sma_20_pct_change_list.append(sma_20_pct_change)

            except:
                print(f"No data found for {stock}...")
        
        screened_df = pd.DataFrame({'Stock':stock_list, 'Rank':ranks, "Current stock price":cmp, '5 SMA':sma_5, '5 SMA % change':sma_5_pct_change_list, '20 SMA':sma_20, '20 SMA % change':sma_20_pct_change_list,'Relative Strength Index':rsi_list, 'Price percentage change':price_pct_change_list, 'Volume percentage change': vol_pct_change_list, 'Beta':betas})
        screened_df = screened_df.sort_values(by = ["Rank", "Price percentage change"], ascending = False)

        return list(screened_df["Stock"]), list(screened_df["Rank"]), list(screened_df["Current stock price"])
