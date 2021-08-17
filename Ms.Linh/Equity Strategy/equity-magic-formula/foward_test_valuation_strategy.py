import pandas as pd
from urllib.parse import urlencode
import requests
from requests import Response
import plotly.graph_objects as go
import sqlalchemy
from datetime import datetime, date, time
import os, sys
import datetime as dt
from dateutil.relativedelta import relativedelta
from math import ceil
import numpy as np

import datetime as dt


def get_rest(url, body={}, headers=None, print_log=False):
    if print_log:
        print("GET REQUEST - url={}, parameters={}".format(url, body))

    response: Response = requests.get(url, params=body, headers=headers)
    if response.status_code != 200:
#         print(response.text)
        content = None
    else:
        try:
            content = response.json()
        except ValueError:
            print(response.text)
            content = None

    if print_log:
        print("{} - GET RESPONSE - url={}, data={}".format(response.status_code, url, content))

    return content


def post_rest(url, body, headers, print_log=False, encode_require=False):
    if print_log:
        print("POST REQUEST - url={}, body={}".format(url, body))
    if encode_require:
        response: Response = requests.post(url, data=urlencode(body), headers=headers)
    else:
        response: Response = requests.post(url, json=body, headers=headers)
    if response.status_code != 200:
#         print(response.text)
        content = None
    else:
        try:
            content = response.json()
        except ValueError:
            print(response.text)
            content = None
    if print_log:
        print("{} - POST RESPONSE - url={}, data={}".format(response.status_code, url, content))

    return content


def get_stock_price(stock_arr: list, to_date: str, from_date='2010-01-01', pivot_type=True, price=True):
    user = 'admin'
    pwd = 'mB17VfhA9gBaWXFaaYSFda2La4ULD12DaZTapt'
    host = 'vinance-prod.coo1pelwmlwz.ap-southeast-1.rds.amazonaws.com'
    port = '3306'
    db = 'vinance'
    db_engine = sqlalchemy.engine.create_engine(
#         'mysql+mysqlconnector://{0}:{1}@{2}:{3}/{4}?charset=utf8mb4'.format(user, pwd, host, port, db))
        'mysql://{0}:{1}@{2}:{3}/{4}?charset=utf8mb4'.format(user, pwd, host, port, db))
    cursor = db_engine.connect()
    query_price = 'SELECT date,code, close FROM price where code in {} and date >= \'{}\' and date<= \'{}\''.format(
        tuple(stock_arr), from_date, to_date)
    price_stock = pd.read_sql(query_price, con=cursor)
    price_stock.date = price_stock.date.apply(lambda x: str(x))
    price_stock = price_stock.loc[price_stock['date'] != '2018-01-24']
    price_stock = price_stock.loc[price_stock['date'] != '2018-01-23']
    price_stock = price_stock.pivot(index='date', columns='code', values='close').fillna(method='ffill')
    cursor.close()
    if pivot_type:
        return price_stock
    else:
        price_stock = pd.melt(price_stock.reset_index(), id_vars=['date'], value_vars=price_stock.columns.tolist()[:],
                              var_name='code', value_name='close')
        return price_stock.dropna()

def get_stock_volume(stock_arr: list, to_date: str, from_date='2010-01-01', pivot_type=True, price=True):
    user = 'admin'
    pwd = 'mB17VfhA9gBaWXFaaYSFda2La4ULD12DaZTapt'
    host = 'vinance-prod.coo1pelwmlwz.ap-southeast-1.rds.amazonaws.com'
    port = '3306'
    db = 'vinance'
    db_engine = sqlalchemy.engine.create_engine(
#         'mysql+mysqlconnector://{0}:{1}@{2}:{3}/{4}?charset=utf8mb4'.format(user, pwd, host, port, db))
        'mysql://{0}:{1}@{2}:{3}/{4}?charset=utf8mb4'.format(user, pwd, host, port, db))
    cursor = db_engine.connect()
    query_price = 'SELECT date, code, volume FROM price where code in {} and date >= \'{}\' and date<= \'{}\''.format(
        tuple(stock_arr), from_date, to_date)
    price_stock = pd.read_sql(query_price, con=cursor)
    price_stock.date = price_stock.date.apply(lambda x: str(x))
    price_stock = price_stock.loc[price_stock['date'] != '2018-01-24']
    price_stock = price_stock.loc[price_stock['date'] != '2018-01-23']
    price_stock = price_stock.pivot(index='date', columns='code', values='volume').fillna(0)
    cursor.close()
    if pivot_type:
        return price_stock
    else:
        price_stock = pd.melt(price_stock.reset_index(), id_vars=['date'], value_vars=price_stock.columns.tolist()[:],
                              var_name='code', value_name='volume')
        return price_stock.dropna()
    

def get_stock_oi(stock_arr: list, to_date: str, from_date='2010-01-01', pivot_type=True):
    user = 'admin'
    pwd = 'mB17VfhA9gBaWXFaaYSFda2La4ULD12DaZTapt'
    host = 'vinance-prod.coo1pelwmlwz.ap-southeast-1.rds.amazonaws.com'
    port = '3306'
    db = 'vinance'
    db_engine = sqlalchemy.engine.create_engine(
#         'mysql+mysqlconnector://{0}:{1}@{2}:{3}/{4}?charset=utf8mb4'.format(user, pwd, host, port, db))
        'mysql://{0}:{1}@{2}:{3}/{4}?charset=utf8mb4'.format(user, pwd, host, port, db))
    cursor = db_engine.connect()
    query_price = 'SELECT date,code, oi FROM price where code in {} and date >= \'{}\' and date<= \'{}\''.format(
        tuple(stock_arr), from_date, to_date)
    price_stock = pd.read_sql(query_price, con=cursor)
    price_stock.date = price_stock.date.apply(lambda x: str(x))
    price_stock = price_stock.loc[price_stock['date'] != '2018-01-24']
    price_stock = price_stock.loc[price_stock['date'] != '2018-01-23']
    price_stock = price_stock.pivot(index='date', columns='code', values='oi').fillna(method='ffill')
    cursor.close()
    if pivot_type:
        return price_stock
    else:
        price_stock = pd.melt(price_stock.reset_index(), id_vars=['date'], value_vars=price_stock.columns.tolist()[:],
                              var_name='code', value_name='oi')
        return price_stock.dropna()

def login():
    base_url = 'http://172.31.240.7:3000/api/v1'
    login_url = base_url + '/login'
    query_url = base_url + '/queryFinancialInfo'

    # Login to get acccess token
    access_token = post_rest(url=login_url, body={
                                                    "grant_type": "password_tradex",
                                                    "client_id": "tradex-admin",
                                                    "client_secret": "tradex-admin",
                                                    "username": "vinh.do@techx.vn",
                                                    "password": "123456",
                                                }, headers={
                                                    "Content-Type": "application/x-www-form-urlencoded"
                                                }, print_log=True, encode_require=True).get('accessToken')
    return access_token

def query_financial_data(year: int, quarter: int, list_stock=[], type='', access_token={}):
    base_url = 'http://172.31.240.7:3000/api/v1'
    login_url = base_url + '/login'
    query_url = base_url + '/queryFinancialInfo'

    # Login to get acccess token
#     access_token = post_rest(url=login_url, body={
#                                                     "grant_type": "password_tradex",
#                                                     "client_id": "tradex-admin",
#                                                     "client_secret": "tradex-admin",
#                                                     "username": "vinh.do@techx.vn",
#                                                     "password": "123456",
#                                                 }, headers={
#                                                     "Content-Type": "application/x-www-form-urlencoded"
#                                                 }, encode_require=True).get('accessToken')
    query_content = {"code": list_stock,
                     "year": year,
                     "quarter": quarter,
                     "type": type,
                     }
    data = get_rest(query_url, body=query_content, headers={
        'Authorization': 'jwt {}'.format(access_token),
    })
    return pd.DataFrame(data).dropna()


# def get_quarter(month: int):
#     if month in [1, 2, 3]:
#         return 1
#     if month in [4, 5, 6]:
#         return 2
#     if month in [7, 8, 9]:
#         return 3
#     else:
#         return 4


# month_in_yr = range(1, 13)


# def get_lag(yr: int, mth: int, lag: int):
#     #     print(month_in_yr.index(mth)-lag)
#     month_lag = month_in_yr[month_in_yr.index(mth) - lag]
#     quarter = get_quarter(month=month_lag)
#     if mth <= lag:
#         year = yr - 1
#     else:
#         year = yr
#     return str(year) + str(quarter)


# def get_growth_data(start_year: int, end_year: int, universe: list, type='net profit after tax'):
#     data = pd.DataFrame()
#     for yr in range(start_year, end_year):
#         for quar in range(1, 5):
#             each_quar = query_financial_data(list_stock=universe, year=yr, quarter=quar,
#                                              type=type)
#             data = pd.concat([data, each_quar])
#     data['yr_quar'] = data['year'].apply(lambda x: str(x)) + data['quarter'].apply(
#         lambda x: str(x))

#     data_value = data[['code', type, 'yr_quar']].pivot(index='yr_quar', columns='code',
#                                                        values=type)
#     #     print(data_value)
#     data_sum4q = data_value.copy(deep=True)
#     for col in data_sum4q.columns:
#         data_sum4q[col] = data_sum4q[col].rolling(4).sum()
#     data_sum4q = data_sum4q[data_sum4q > 0]
#     data_growth = data_sum4q.copy(deep=True)
#     for col in data_growth.columns:
#         data_growth[col] = data_growth[col] / data_growth[col].shift(1) - 1
#     # missing_code
#     return data_growth


# def strategy(strategy_name: str, start_date: str, end_date: str, pct_stock: float, lag: int, universe: list, chart=True,
#              growth_filter=True, filter_type='net profit after tax'):
#     oi = get_stock_oi(stock_arr=universe, from_date=start_date, to_date=end_date, pivot_type=True).reset_index()
#     oi['yr_month'] = oi['date'].apply(lambda x: x.split('-')[0] + x.split('-')[1])
#     monthly_oi = oi.groupby('yr_month').agg(['last']).stack().reset_index().set_index('yr_month').drop(
#         columns=['level_1', 'date'])

#     price = get_stock_price(stock_arr=universe, from_date=start_date, to_date=end_date, pivot_type=True).reset_index()
#     price['yr_month'] = price['date'].apply(lambda x: x.split('-')[0] + x.split('-')[1])
#     monthly_p = price.groupby('yr_month').agg(['last']).stack().reset_index().set_index('yr_month').drop(
#         columns=['level_1', 'date'])

#     monthly_ret = monthly_p / monthly_p.shift(1) - 1
#     market_cap = (monthly_oi * monthly_p).reset_index()
#     market_cap = pd.melt(market_cap, id_vars=['yr_month'], value_vars=market_cap.columns.tolist()[1:], var_name='code',
#                          value_name='market_cap')
#     market_cap['yr_quar'] = market_cap['yr_month'].apply(lambda x: get_lag(yr=int(x[:4]), mth=int(x[-2:]), lag=lag))

#     start_yr = int(start_date[:4]) - 1
#     end_yr = int(end_date[:4]) + 1
#     financial_data = pd.DataFrame()
#     for yr in range(start_yr, end_yr):
#         for quar in range(1, 5):
#             each_quar = query_financial_data(list_stock=universe, year=yr, quarter=quar, type=strategy_name)
#             financial_data = pd.concat([financial_data, each_quar])
#     financial_data['yr_quar'] = financial_data['year'] + financial_data['quarter']

#     value_df = financial_data[['code', 'yr_quar', strategy_name]].merge(market_cap, on=['yr_quar', 'code'], how='right')

#     value_df['value'] = value_df[strategy_name] / value_df['market_cap']

#     monthly_data = value_df[['code', 'value', 'yr_month']].pivot(index='yr_month', columns='code', values='value')

#     #     monthly_data.to_csv('valuation_check.csv')
#     # monthly_data

#     monthly_rank = monthly_data.rank(axis=1, ascending=False, pct=True)

#     # monthly_rank

#     signal = monthly_rank[monthly_rank <= pct_stock].dropna(axis=1, how='all')
#     signal[signal > 0] = 1
#     signal.to_csv('raw_signal.csv')

#     if growth_filter:
#         growth_data = get_growth_data(start_year=start_yr - 1, end_year=end_yr, universe=universe, type=filter_type)
#         growth_data = growth_data[growth_data > 0]
#         growth_data[growth_data > 0] = 1
#         growth_data = growth_data.reset_index()
#         growth_data = pd.melt(growth_data, id_vars=['yr_quar'], value_vars=growth_data.columns.tolist()[1:],
#                               var_name='code', value_name='growth')

#         value_df = value_df.merge(growth_data, on=['code', 'yr_quar'], how='left')
#         growth_signal = value_df[['code', 'yr_month', 'growth']].pivot(index='yr_month', columns='code',
#                                                                        values='growth')
#         signal = (signal * growth_signal).dropna(axis=1, how='all')
#         signal.to_csv('growth_filtered.csv')

#     #     print(" number of columns_____________{}".format(len(signal.columns)))

#     signal = signal.shift(1)
#     mm_hold = signal.count(axis=1).max()
#     profit_arr = signal * monthly_ret[signal.columns.tolist()].dropna(axis=1, how='all')

#     #     profit_arr

#     profit_arr['daily_ret'] = profit_arr.mean(axis=1)

#     profit_arr['profit'] = (profit_arr['daily_ret'] + 1).cumprod()
#     daily_profit = profit_arr['daily_ret'].tolist()
#     cumulative = profit_arr['profit'].dropna().tolist()

#     win_arr = [x for x in daily_profit if x > 0]
#     loss_arr = [x for x in daily_profit if x < 0]
#     win_rate = len(win_arr) / (len(loss_arr) + len(win_arr))
#     dd_arr = []
#     for i in range(len(cumulative)):
#         if i > 0:
#             dd_arr.append((max(cumulative[:i]) - cumulative[i - 1]) / max(cumulative[:i]))
#     max_dd = max(dd_arr)
#     print("mm_holding:{}------winrate:{}-----profit/MDD:{}".format(mm_hold, round(win_rate, 4),
#                                                                    round(cumulative[-1] / max_dd, 4)))
#     profit_arr.to_csv('profit_valuation.csv')
#     profit_arr = profit_arr.reset_index()
#     if chart:
#         #         benchmark=(daily_ret.mean(axis=1)+ 1).cumprod().tolist()
#         fig = go.Figure()
#         fig.add_trace(
#             go.Scatter(x=profit_arr.yr_month.apply(lambda x: dt.datetime.strptime(x, '%Y%m')).tolist(), y=cumulative,
#                        mode='lines',
#                        name='cumulative'))
#         #         fig.add_trace(go.Scatter(x=profit_arr.index.tolist(), y=benchmark[99:],
#         #                                  mode='lines',
#         #                                  name='benchmark'))
#         #         if chart_title:
#         #             fig.update_layout(title_text=chart_title)

#         fig.show()
#     return profit_arr


# list_stock_link = 'https://trading.vcsc.com.vn/restapi/api/v1/market/stock/listed?marketType=HOSE&securitiesType=ALL&fetchCount=1000'
# hose_list = pd.DataFrame(get_rest(url=list_stock_link, body={}))
# hose_list['len'] = hose_list['code'].apply(lambda x: len(x))
# hose_list = hose_list[hose_list['len'] == 3].code.tolist()
# print(len(hose_list))
# strategy_list = ['net profit after tax', 'revenue', 'operating profit', 'gross profit',
#                  'net cash flow from operating activities']


# # # not using filter example
# # c = fwd_test(strategy_name=strategy_list[-1], start_date='2020-01-01', end_date='2020-11-30', pct_stock=0.1, lag=4,
# #              universe=hose_stocks, growth_filter=False)

# # DELAY PRICE FOR STRATEGY --------------------
# def get_delay_price(daily_data: pd.DataFrame, date_delay: int):
#     daily_data = daily_data.set_index('date').shift(-date_delay).dropna(how='all', axis=0).reset_index()
#     daily_data['yr_month'] = daily_data['date'].apply(lambda x: x.split('-')[0] + x.split('-')[1])
#     monthly_data = daily_data.groupby(['yr_month']).agg(['last']).stack().reset_index().set_index('yr_month').drop(
#         columns=['level_1', 'date'])
#     return monthly_data


# def fwd_test_delay_buy(strategy_name: str, start_date: str, end_date: str, pct_stock: float, lag: int, universe: list,
#                        delay: int, chart=True, growth_filter=True, filter_type='net profit after tax'):
#     oi = get_stock_oi(stock_arr=universe, from_date=start_date, to_date=end_date, pivot_type=True).reset_index()
#     #     oi['yr_month']=oi['date'].apply(lambda x: x.split('-')[0]+x.split('-')[1])
#     monthly_oi = get_delay_price(daily_data=oi, date_delay=delay)

#     price = get_stock_price(stock_arr=universe, from_date=start_date, to_date=end_date, pivot_type=True).reset_index()
#     #     price['yr_month']=price['date'].apply(lambda x: x.split('-')[0]+x.split('-')[1])
#     monthly_p = get_delay_price(daily_data=price, date_delay=delay)

#     monthly_ret = monthly_p / monthly_p.shift(1) - 1
#     market_cap = (monthly_oi * monthly_p).reset_index()
#     market_cap = pd.melt(market_cap, id_vars=['yr_month'], value_vars=market_cap.columns.tolist()[1:], var_name='code',
#                          value_name='market_cap')
#     market_cap['yr_quar'] = market_cap['yr_month'].apply(lambda x: get_lag(yr=int(x[:4]), mth=int(x[-2:]), lag=lag))

#     start_yr = int(start_date[:4]) - 1
#     end_yr = int(end_date[:4]) + 1
#     financial_data = pd.DataFrame()
#     for yr in range(start_yr, end_yr):
#         for quar in range(1, 5):
#             each_quar = query_financial_data(list_stock=universe, year=yr, quarter=quar, type=strategy_name)
#             financial_data = pd.concat([financial_data, each_quar])
#     financial_data['yr_quar'] = financial_data['year'] + financial_data['quarter']

#     value_df = financial_data[['code', 'yr_quar', strategy_name]].merge(market_cap, on=['yr_quar', 'code'], how='right')

#     value_df['value'] = value_df[strategy_name] / value_df['market_cap']

#     monthly_data = value_df[['code', 'value', 'yr_month']].pivot(index='yr_month', columns='code', values='value')

#     monthly_data.to_csv('valuation_check_test_{}.csv'.format(delay))
#     # monthly_data

#     monthly_rank = monthly_data.rank(axis=1, ascending=False, pct=True)

#     # monthly_rank

#     signal = monthly_rank[monthly_rank <= pct_stock].dropna(axis=1, how='all')
#     signal[signal > 0] = 1
#     # signal.to_csv('raw_signal.csv')

#     if growth_filter:
#         growth_data = get_growth_data(start_year=start_yr - 1, end_year=end_yr, universe=universe, type=filter_type)
#         growth_data = growth_data[growth_data > 0]
#         growth_data[growth_data > 0] = 1
#         growth_data = growth_data.reset_index()
#         growth_data = pd.melt(growth_data, id_vars=['yr_quar'], value_vars=growth_data.columns.tolist()[1:],
#                               var_name='code', value_name='growth')

#         value_df = value_df.merge(growth_data, on=['code', 'yr_quar'], how='left')
#         growth_signal = value_df[['code', 'yr_month', 'growth']].pivot(index='yr_month', columns='code',
#                                                                        values='growth')
#         signal = (signal * growth_signal).dropna(axis=1, how='all')
#         # signal.to_csv('growth_filtered.csv')

#     #     print(" number of columns_____________{}".format(len(signal.columns)))

#     signal = signal.shift(1)
#     mm_hold = signal.count(axis=1).max()
#     profit_arr = signal * monthly_ret[signal.columns.tolist()].dropna(axis=1, how='all')

#     #     profit_arr

#     profit_arr['daily_ret'] = profit_arr.mean(axis=1)

#     profit_arr['profit'] = (profit_arr['daily_ret'] + 1).cumprod()
#     daily_profit = profit_arr['daily_ret'].tolist()
#     cumulative = profit_arr['profit'].dropna().tolist()

#     win_arr = [x for x in daily_profit if x > 0]
#     loss_arr = [x for x in daily_profit if x < 0]
#     win_rate = len(win_arr) / (len(loss_arr) + len(win_arr))
#     dd_arr = []
#     for i in range(len(cumulative)):
#         if i > 0:
#             dd_arr.append((max(cumulative[:i]) - cumulative[i - 1]) / max(cumulative[:i]))
#     max_dd = max(dd_arr)
#     print('CUMULATIVE PROFIT: {}'.format(round(cumulative[-1], 4)))
#     print("mm_holding:{}------winrate:{}-----profit/MDD:{}".format(mm_hold, round(win_rate, 4),
#                                                                    round(cumulative[-1] / max_dd, 4)))
#     #     profit_arr.to_csv('profit_valuation.csv')
#     profit_arr = profit_arr.reset_index()
#     if chart:
#         #         benchmark=(daily_ret.mean(axis=1)+ 1).cumprod().tolist()
#         fig = go.Figure()
#         fig.add_trace(
#             go.Scatter(x=profit_arr.yr_month.apply(lambda x: dt.datetime.strptime(x, '%Y%m')).tolist(), y=cumulative,
#                        mode='lines',
#                        name='cumulative'))
#         #         fig.add_trace(go.Scatter(x=profit_arr.index.tolist(), y=benchmark[99:],
#         #                                  mode='lines',
#         #                                  name='benchmark'))
#         #         if chart_title:
#         #             fig.update_layout(title_text=chart_title)

#         fig.show()
#     return profit_arr


# # example with delay of 2 days
# a = fwd_test_delay_buy(strategy_name='gross profit', start_date='2020-01-01', end_date='2021-01-06', pct_stock=0.1,
#                        lag=4, universe=hose_list, delay=2)
# print(a)


def get_group_market_cap(date: str, lst_code=[]):
    price = get_stock_price(stock_arr=lst_code, 
                               to_date=date, 
                               from_date=date, pivot_type=False, price=True)
    oi = get_stock_oi(stock_arr=lst_code, to_date=date, from_date=date, pivot_type=False)
    
    price_oi = pd.merge(price, oi, on=['date', 'code'], how='left')
    price_oi['marcap'] = price_oi['close'] * 1000 * price_oi['oi']
    price_oi = price_oi.sort_values(by='marcap', ascending=False).reset_index(drop=True).reset_index()
    price_oi['type'] = np.nan
    price_oi.loc[price_oi['index']<50, 'type'] = 'largeCap'
    price_oi.loc[(price_oi['index']>=50)&(price_oi['marcap']>1000000), 'type'] = 'midCap'
    price_oi.loc[price_oi['type'].isna(), 'type'] = 'smallCap'
    return price_oi[['code', 'type']]