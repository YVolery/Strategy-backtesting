# Backtesting of a trading strategy
***
This Python program allows to evaluate the performance of an uncomplicated trading strategy based on two different technical analysis indicators: [Relative Strength Index](https://www.investopedia.com/terms/r/rsi.asp), an oscillator and Simple Moving Average from [investopedia](https://www.investopedia.com/terms/s/sma.asp), a trend indicator. As historical ticker data is imported from [Yahoo Finance](https://finance.yahoo.com/), using the pandas-datareader package, an extensive selection of assets is available on the daily timeframe. The aim was not to create the most profitable strategy but provide a framework that allows further development. Results are displad in various popular ratios as well as a graphical illustration of entries/exits on a candlestick chart using the Plotly package.
WARNING: We decline all responsibility if someone decides to invest money using our strategy.

## Prerequisites
***
The following technologies were used running the project:
* [Python v3.8](https://www.python.org/downloads/release/python-380/)
* [pandas-datareader v0.9.0rc1](https://pandas-datareader.readthedocs.io/en/latest/index.html)
* [Plotly v4.12.0](https://plotly.com/python/getting-started/)
* an internet browser such as [Safari v14.0](https://support.apple.com/de-ch/safari)
We used the following IDE that allows a simple installation of packages in preferences:
* [PyCharm v2020.2.3](https://www.jetbrains.com/de-de/pycharm/)
Alternatively, follow the installation instructions provided in the links.
For your understanding, basic knowledge of trading in capital markets and technical analysis is beneficial.

## Usage
***
### Setup
Run main.py with Python in your favored way. Enter your starting capital, start and end dates of your desired testing period and a ticker symbol from [Yahoo Finance](https://finance.yahoo.com/).

### Strategy
In order to modify your strategy, you can change the lines containing the entry/exit conditions:

Price closing above the SMA indicates an uptrend while the RSI being below 30 is defined as an oversold condition. Combined, this results in our buy signal (line 100 in main.py):
```python
if not in_buy and chart_data.Close[candle] > chart_data['SMA%s' % periodSMA][candle] \
                    and chart_data['RSI%s' % periodRSI][candle] < 30:
```

If either the RSI is above 70, indicating an oversold condition or 100 days have passed since the buy signal, the sell signal is issued (line 109 in main.py):
```Python
if in_buy and (chart_data.RSI10[candle] > 70 or chart_data.Date[candle] - buy_date > timedelta(days=100)):
```

### Results
Quantitative statistics of the strategy are displayed in the terminal and the corresponding candlestick chart is opened in a new browser tab. For more information on

## Contributing
***
The current program offers various options for further development. For example, short selling, leverage, capital risked per trade or trading fees could be implemented. Furthermore, lower timeframes would be worthy to consider but would need a different data source, as Yahoo Finance doesn't provide anything below the daily timeframe. More indicators would also be helpful in order to develop more refined strategies.

## Credits
***
Project created by Joschija Eberl and Yan Volery in autumn semester 2020 at University of St. Gallen, mentored by Dr. Mario Silic.

## Sources/Acknowledgements
***
We considered the following websites quite helpful for our project:
* [information on SMA](https://www.datacamp.com/community/tutorials/moving-averages-in-pandas)
* [information on RSI](https://towardsdatascience.com/algorithmic-trading-with-rsi-using-python-f9823e550fe0)
* [useful statistics parameters](https://www.amibroker.com/guide/w_report.html#old)

## License
MIT
