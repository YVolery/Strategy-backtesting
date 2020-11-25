# import needed libraries for data reader and date time support
from pandas_datareader import data as dr
from pandas_datareader._utils import RemoteDataError
from datetime import date, timedelta
# import outsourced graphics functionality from graphics.py
from graphics import graphics
# import sys for abort functionality
import sys

while True:
    try:
        # user interaction
        # ask for initial capital and ticker
        start_capital = float(input("Enter your initial capital:\n"))
        ticker = input("Enter some ticker available at finance.yahoo.com:\n")
        # ask for testing range and convert to date objects
        date_entry = input('Enter begin of testing range in YYYY-MM-DD format:\n')
        date_entry2 = input('Enter end of testing range in YYYY-MM-DD format\n')
        year1, month1, day1 = map(int, date_entry.split('-'))
        year2, month2, day2 = map(int, date_entry2.split('-'))
        start_date = date(year1, month1, day1)
        end_date = date(year2, month2, day2)
        # data import: read and parse file containing OHLC data into dataframe using pandas datareader
        # strftime is used to convert from datetime to string in specific format wanted by datareader
        chart_data = dr.DataReader(str(ticker),
                                   start=start_date.strftime('%Y-%m-%d'),
                                   end=str(date.today()),
                                   data_source='yahoo')
        # convert index column to normal column and add standard numbered index column
        chart_data.reset_index(inplace=True, drop=False)
        break
    # error handling for wrong ticker input
    except RemoteDataError:
        print("Error. No information for ticker '{}'. Only enter tickers available on Yahoo Finance.".format(ticker))
    # error handling for wrong date/starting capital input
    except ValueError:
        print("Error. Enter correct dates and numeric start capital.")

# indicators: starting with simple moving average, indicating trend
# important: needs given number of previous periods in order to be calculated
def SMA(periodSMA):
    sma = []
    # Make a list called sma with length of chart_data, containing moving average of Close column
    for _ in chart_data["Close"]:
        # .rolling takes a window of values, here we do a new list containing results of mean function
        sma = chart_data.Close.rolling(periodSMA).mean()
    # Declare new "result" list as a new column of the dataframe
    chart_data['SMA%s' %periodSMA] = sma


# relative strength index is an oscillator that indicates if asset is potentially overbought/oversold
def RSI(periodRSI):
    rsi = []
    # define new list containing the difference of 2 consecutive values in close prices
    delta = chart_data.Close.diff()
    window = periodRSI
    # copies delta values to new list
    up_days = delta.copy()
    # for all negative values in delta list, make value 0 in up_days
    up_days[delta <= 0] = 0.0
    # make all values positive with absolute function
    down_days = abs(delta.copy())
    # when value in delta (not down_days!) is positive, make value 0 in down_days
    down_days[delta > 0] = 0.0
    # calculate averages of up_days and down_days list to obtain relative strength
    RS_up = up_days.rolling(window).mean()
    RS_down = down_days.rolling(window).mean()
    for _ in chart_data["Close"]:
        rsi = (100 - 100 / (1 + RS_up / RS_down))
    # declare new "result2" list as a new column of the dataframe
    chart_data['RSI%s' % periodRSI] = rsi


# strategy and back testing starting here
# initialize variables:
# shows if there is an open position (True) or not (False)
in_buy = False
# list saves buy and sell dates, also used for graphics later (green/red lines for annotation)
buy_date_list = []
sell_date_list = []
# list saves duration of trades open
deltadays = []
winners_deltadays = []
losers_deltadays = []
# list saves relative and absolute gain/loss of trade
profit_loss_rel = []
profit_loss_abs = []

# here we choose the period length of the indicators and execute the indicator functions to calculate them
periodRSI = 10
RSI(periodRSI)
periodSMA = 200
SMA(periodSMA)
# get a glance at the whole dataframe
print(chart_data)

# back testing a strategy on every candle in chart_data
for candle in chart_data.index:
    # buy strategy condition: if not already in a buy (in_buy=-1), and conditions fulfilled (price above SMA and RSI below 30)
    if not in_buy and chart_data.Close[candle] > chart_data['SMA%s' % periodSMA][candle] \
                    and chart_data['RSI%s' % periodRSI][candle] < 30:
        # save buy at next days open after signal
        buy_date = chart_data.Date[candle + 1]
        buy_date_list.append(buy_date)
        buy_price = chart_data.Open[candle + 1]
        # we're in a buy now
        in_buy = True
    # sell strategy condition: if in a buy (in_buy=1) and either RSI above 70 or 10 days passed
    if in_buy and (chart_data.RSI10[candle] > 70 or chart_data.Date[candle] - buy_date > timedelta(days=100)):
        # all necessary trade stats get saved here when trade gets closed
        sell_date = chart_data.Date[candle + 1]
        sell_price = chart_data.Open[candle + 1]
        sell_date_list.append(sell_date)
        pl_rel = (sell_price - buy_price) / buy_price
        trade_duration = int((chart_data.Date[candle] - buy_date).days)
        deltadays.append(trade_duration)
        if pl_rel >= 0:
            winners_deltadays.append(trade_duration)
        else:
            losers_deltadays.append(trade_duration)
        profit_loss_rel.append(pl_rel)
        in_buy = False

# if no trades were taken, display error and exit
if len(profit_loss_rel) == 0:
    print("Error: No trades were placed. Enter a shorter period")
    sys.exit(0)


# Quantitative results
# absolute p/l and capital development calculation
# assumption: we invest our whole available capital in every trade
capital = start_capital
capital_development = [start_capital]
for value in profit_loss_rel:
    # calculate and save absolute gain
    absolute = (capital * (1+value)) - capital
    profit_loss_abs.append(absolute)
    # calculate and save capital after trade
    capital = capital + absolute
    capital_development.append(capital)
end_capital = start_capital + sum(profit_loss_abs)

# calculation of overall statistics
net_profit = end_capital - start_capital
net_profit_p = net_profit/start_capital*100
testing_range = end_date - start_date
annual_return = net_profit/(testing_range.days/365)/start_capital * 100
trades_taken = len(profit_loss_rel)
avg_pl = sum(profit_loss_abs)/trades_taken
avg_pl_p = sum(profit_loss_rel)/trades_taken*100
avg_bars_held = sum(deltadays)/trades_taken

# calculation of winning trades stats
# lambda filters negative/positive values of profit_loss list
winners_number = len(list(filter(lambda x: (x >= 0), profit_loss_rel)))
winners_number_p = winners_number/trades_taken*100
winners_total = sum(list(filter(lambda x: (x >= 0), profit_loss_abs)))
winners_avg_profit = winners_total/winners_number
winners_avg_profit_p = sum(list(filter(lambda x: (x >= 0), profit_loss_rel)))/winners_number*100
winners_avg_bars_held = sum(winners_deltadays)/winners_number
winners_largest = max(profit_loss_abs)

# calculation of losing trades stats
losers_number = len(list(filter(lambda x: (x < 0), profit_loss_rel)))
losers_number_p = losers_number/trades_taken*100
losers_total = sum(list(filter(lambda x: (x < 0), profit_loss_abs)))
losers_avg_loss = losers_total/losers_number
losers_avg_loss_p = sum(list(filter(lambda x: (x < 0), profit_loss_rel)))/losers_number*100
losers_avg_bars_held = sum(losers_deltadays)/losers_number
losers_largest = min(profit_loss_abs)

# calculation of max. consecutive p/l
# worth of consecutive trades
cons_gain_rel = []
cons_loss_rel = []
gain = 0
loss = 0
# number of consecutive trades
cons_gain_num = []
cons_loss_num = []
gainnum = 0
lossnum = 0
# boolean variable saves if loss or win occured
win_before = True
# check all entries of P/L list
for pl in profit_loss_rel:
    # there is a gain
    if pl >= 0:
        gain += pl
        gainnum += 1
        # if its the first gain after one or more losses, save sum of accumulated losses
        if not win_before:
            cons_loss_rel.append(loss)
            cons_loss_num.append(lossnum)
            loss = 0
            lossnum = 0
        win_before = True
    # there is a loss
    elif pl < 0:
        loss += pl
        lossnum += 1
        # if its the first loss after gains, save sum of accumulated wins
        if win_before:
            cons_gain_rel.append(gain)
            cons_gain_num.append(gainnum)
            gain = 0
            gainnum = 0
        win_before = False

# Display strategy performance results, rounded to two digits after decimal
print("Statistics: \n--------------------")
print("Initial capital: {}".format(start_capital))
print("Ending capital: {}".format(round(end_capital, 2)))
print("Net profit: {}".format(round(net_profit, 2)))
print("Net profit %: {} %".format(round(net_profit_p), 2))
print("Annual return %: {} %".format(round(annual_return), 2))
print("-------------------")
print("Number of total trades taken: {}".format(trades_taken))
print("Average P/L: {} %".format(round(avg_pl, 2)))
print("Average P/L %: {} %".format(round(avg_pl_p, 2)))
print("Average Bars Held: {}".format(round(avg_bars_held, 2)))
print("-------------------")
print("Winners: {} ({} %)".format(winners_number, round(winners_number_p, 2)))
print("Total profit: {}".format(round(winners_total, 2)))
print("Average profit: {}".format(round(winners_avg_profit, 2)))
print("Average profit %: {} %".format(round(winners_avg_profit_p, 2)))
print("Average bars held: {}".format(round(winners_avg_bars_held, 2)))
print("Max. number of consecutive gains: {}".format(max(cons_gain_num)))
print("Max. consecutive gain %: {} %".format(round(max(cons_gain_rel)*100, 2)))
print("Largest single win: {}".format(round(winners_largest, 2)))
print("-------------------")
print("Losers: {} ({} %)".format(losers_number, round(losers_number_p, 2)))
print("Total loss: {}".format(round(losers_total, 2)))
print("Average loss: {}".format(round(losers_avg_loss, 2)))
print("Average loss %: {} %".format(round(losers_avg_loss_p, 2)))
print("Average bars held: {}".format(round(losers_avg_bars_held, 2)))
print("Max. number of consecutive losses: {}".format(max(cons_loss_num)))
print("Max. consecutive loss {} %".format(round(max(cons_loss_rel)*100, 2)))
print("Largest single loss: {}".format(round(losers_largest, 2)))

# Plot graphics results
graphics(ticker, chart_data, buy_date_list, sell_date_list, periodSMA, periodRSI,net_profit_p,annual_return)