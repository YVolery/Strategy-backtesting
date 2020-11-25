# Separate file that plots the results of the main.py or main_alternative.py
# to structure the project in a better way and make it easy to read

# import plotly package used for extensive graphing
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# puts whole graphing part into function
def graphics(ticker, chart_data, buy_date_list, sell_date_list, periodSMA, periodRSI,net_profit_p,annual_return):
    # Define figure with 2 subplots in 2 rows
    fig = make_subplots(rows=2,
                        cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.05,
                        row_width=[0.15, 0.85])

    # Set title and don't display range slider on graph
    tit="{}           |          percentage gain is: {} %          |           annual gain is: {} %".format(str(ticker), str(round(net_profit_p,2)), str(round(annual_return,2)))
    fig.update_layout(title_text=tit,
                      xaxis=dict(rangeslider=dict(visible=False)))




    # Set the data from our chart data as a candlestick chart, also add moving averages as a scatter chart
    fig.add_trace(go.Candlestick(x=chart_data.Date,
                                 open=chart_data.Open,
                                 high=chart_data.High,
                                 low=chart_data.Low,
                                 close=chart_data.Close,
                                 name="Chart",
                                 showlegend=False),
                  row=1,
                  col=1)
    # Adding SMA values with a green line on the same graph as the Candlestick ( row = 1)
    fig.add_trace(go.Scatter(x=chart_data.Date,
                             y=chart_data['SMA%s' % periodSMA],
                             line=dict(color='green', width=1),
                             name='SMA%s' % periodSMA),
                  row=1,
                  col=1)
    # Adding RSI values with black lines on the 2nd graph (row = 1)
    fig.add_trace(go.Scatter(x=chart_data.Date,
                             y=chart_data['RSI%s' % periodRSI],
                             line=dict(color='black', width=1),
                             name='RSI%s' % periodRSI),
                  row=2,
                  col=1)

    # Annotation function: add green and red vertical lines when buy/sell occurs
    def annotator(date, color):
        # add shape to plotly figure, vertical line, xref and yref make line continuous, not only from y0 to y1
        fig.add_shape(dict(type="line",
                           x0=date,
                           y0=0,
                           x1=date,
                           # "xref" convert the x0 to x1 block to a continuous block --> a point in this case
                           xref='x',
                           y1=1,
                           # "yref" convert y0 to y1 to a continous line, by specifying with 'paper'
                           # a position that is always relative to the plot
                           yref='paper',
                           line=dict(color=color,
                                     width=1)))

    # Execute annotator function for every buy_date and sell_date
    for i in range(len(buy_date_list)):
        annotator(buy_date_list[i], "green")
    for i in range(len(sell_date_list)):
        annotator(sell_date_list[i], "red")

    # Display figure in browser, remove plotly buttons that seem to be unfunctional for our purposes
    fig.show(config={'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d']})