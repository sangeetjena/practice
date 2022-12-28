from binance import Client
import pandas as pd
apiKey='vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A'
secretKey='NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j'


client= Client(apiKey,secretKey)
lst=(client.get_symbol_ticker())
candles = client.get_klines(symbol='BNBBTC', interval=Client.KLINE_INTERVAL_12HOUR)
print(candles)
"""Get compressed, aggregate trades. Trades that fill at the time,
       from the same order, with the same price will have the quantity aggregated.

       https://binance-docs.github.io/apidocs/spot/en/#compressed-aggregate-trades-list

       :param symbol: required
       :type symbol: str
       :param fromId:  ID to get aggregate trades from INCLUSIVE.
       :type fromId: str
       :param startTime: Timestamp in ms to get aggregate trades from INCLUSIVE.
       :type startTime: int
       :param endTime: Timestamp in ms to get aggregate trades until INCLUSIVE.
       :type endTime: int
       :param limit:  Default 500; max 1000.
       :type limit: int
"""
# lst=(client.get_aggregate_trades(symbol='BNBBTC'))
# # print(client.get_historical_trades(symbol='BNBBTC'))
# df=pd.DataFrame(lst)
# df.columns=['tradeId','Price','Quantity','First_tradeId','Last_tradeId','Timestamp','buyer_the_maker','best_price_match']
# df['date']=pd.to_datetime(df['Timestamp'],unit='ms')
# tempDf=df[['Price','date','Quantity']]
# #calculate total volume in btc = price  * quantity
# tempDf['sumbtc']=tempDf['Price'].astype(float)*tempDf['Quantity'].astype(float)
# tempDf['sumbtc'].astype(float).sum()
# print(df['Price'].astype(float).sum())