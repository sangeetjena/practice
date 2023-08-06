import pandas as pd
import datetime

#read all order whish status is ordered
# orderdf = pd.read_csv("/Users/sajena/PycharmProjects/practice/resource/sales.csv")

orderdf = pd.DataFrame([{'order_id':'1','status':'ordered','datte':'2023-08-01 11:00:00'},
                    {'order_id':'1','status':'delivered','datte':'2023-08-01 13:00:00'},
                    {'order_id':'2','status':'ordered','datte':'2023-08-01 14:14:00'},
                    {'order_id':'3','status':'ordered','datte':'2023-08-01 13:00:00'},
                    {'order_id':'3','status':'delivered','datte':'2023-08-04 15:14:00'},
                    {'order_id':'4','status':'ordered','datte':'2023-08-01 18:00:00'},])

order_only_df = orderdf[orderdf['status'] == 'ordered']
deliver_only_df = orderdf[orderdf['status'] == 'delivered']

# left join
join_df = pd.merge(order_only_df, deliver_only_df, left_on='order_id', right_on='order_id', how='left')

#null handling
join_df['datte_y'] = join_df['datte_y'].fillna(datetime.datetime.now())
join_df['diff'] = (pd.to_datetime(join_df['datte_y']) - pd.to_datetime(join_df['datte_x'])).dt.total_seconds()/60
print(join_df[join_df['diff'] > 24*12*2])