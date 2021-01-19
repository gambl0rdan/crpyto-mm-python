import pandas as pd
import datetime

# date = pd.to_datetime("4th of July, 2015")
# print(date)
pd.set_option('display.max_columns', 10)

class TimeSeriesContainer:
    COLS = ('datetime', 'last price','Avg Px Bid', 'Avg Px Ask', 'VWAP Bid', 'VWAP Ask', 'VWAP Px Diff Bid', 'VWAP Px Diff Ask',
            "bid_1", "bid_2", "ask_1", "ask_2")
    ticks = 0

    def __init__(self, firebase_conn):
        self.ts_data = pd.DataFrame({}, columns = self.COLS)
        self.firebase_conn = firebase_conn
        self.enabled = True

    def update(self, row):
        self.ts_data = self.ts_data.append(row, True)
        self.ts_data = self.ts_data.set_index('datetime')
        self.ticks+=1
        if (self.ticks % 4000) == 0:
            self.export_to_firebase(self.ts_data[-2:-1].to_dict('records'), 'marketdata', 'l2')
            self.ts_data = self.ts_data[0:0]

    def update_order(self, row):
        self.export_to_firebase([row], 'orders', 'filled')

    def update_ticker(self, row):
        self.export_to_firebase([row], 'marketdata', 'ticker')

    def update_balance(self, row):
        self.export_to_firebase([row], 'position', 'balance')

    def update_alert(self, row):

        try:
            self.export_to_firebase([row], 'alerts', 'main')
        except Exception as ex:
            print(ex)

    def display(self):
        # print(['%s=%.2f' % (k, v) for (k, v) in results.items()])
        from pprint import pprint
        pprint(self.ts_data[-1:])

    def export_to_firebase(self, data, collection_name, sub_collection_name):
        if not self.enabled:
            return

        for row in data:
            now = datetime.datetime.now()
            dt = now.strftime('%Y%m%d')
            ts = now.strftime('%Y%m%d-%H%M%S')

            date_ref = self.firebase_conn.collection(collection_name).document(dt)
            doc_ref = date_ref.collection(sub_collection_name).document(ts)
            row['datetime'] = now
            doc_ref.set(row)
            # print('tickers', row)


    def export_to_csv(self):
        self.ts_data.to_csv(r'./crypto-mm-data.csv', index=True)
