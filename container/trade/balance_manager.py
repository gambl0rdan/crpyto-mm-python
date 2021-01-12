
# 25/6200
#0.00403225806

approx_max = 25./6200. # £25
approx_trade_unit = approx_max / 25 # £1 # 0.000161 BTC

MAX_NTL_BTC = 0.001
MAX_NTL_GBP = 7.
MAX_NTL_USD = 10.

BTC = 'BTC'
GBP = 'GBP'
USD = 'USD'

from _collections import defaultdict

class BalanceManager:

    def __init__(self):
        self.__currencies = defaultdict(float)

    def update_balances(self, exchange_msg):
        if 'balances' not in exchange_msg:
            return

        for row in exchange_msg['balances']:
            self.__currencies[row['currency']] = row['available']

        if 'USD' not in self.__currencies:
            self.__currencies['USD'] = 0.

    def get_balances(self):
        return dict(self.__currencies)

if __name__ == "__main__":
    # {'seqnum': 6, 'event': 'snapshot', 'channel': 'balances', 'balances': [
    #     {'currency': 'GBP', 'balance': 12.45, 'available': 6.24, 'balance_local': 12.45, 'available_local': 6.24,
    #      'rate': 1.0},
    #     {'currency': 'BTC', 'balance': 0.002, 'available': 0.001, 'balance_local': 12.38, 'available_local': 6.19,
    #      'rate': 6190.0}], 'total_available_local': 12.43, 'total_balance_local': 24.83}

    balances = BalanceManager()
    print(balances.currencies)

