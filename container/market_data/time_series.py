import pandas as pd
import datetime
# date = pd.to_datetime("4th of July, 2015")
# print(date)
pd.set_option('display.max_columns', 10)

class TimeSeriesContainer:
    COLS = ('datetime', 'last price','Avg Px Bid', 'Avg Px Ask', 'VWAP Bid', 'VWAP Ask', 'VWAP Px Diff Bid', 'VWAP Px Diff Ask', "bid_1", "bid_2", "ask_1", "ask_2")
    ticks = 0


    def __init__(self):

        self.ts_data = pd.DataFrame({}, columns = self.COLS)

    def update(self, row):
        self.ts_data = self.ts_data.append(row, True)
        # self.ts_data = self.ts_data.set_index('datetime')
        self.ticks+=1

        if (self.ticks % 1000) == 0:
            self.export()        
            self.ts_data = self.ts_data[0:0]
    
    def display(self):
        # print(['%s=%.2f' % (k, v) for (k, v) in results.items()])
        from pprint import pprint
        pprint(self.ts_data[-1:])

    def export(self):
        self.ts_data.to_csv(r'./crypto-mm-data.csv', index=True)
