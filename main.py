import requests
import pickle
from pprint import pprint
import json
import pandas as pd
import time
from tqdm import tqdm
from datetime import datetime
import talib
import matplotlib.pyplot as plt
from mpl_finance import candlestick2_ochl, volume_overlay

class Sina(object):
    def __init__(self):
        self.url1 = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol='
        self.url2 = '&scale=5&ma=5&datalen='
        with open('data/symbol_ind.pkl', 'rb') as f:
            self.symbol = pickle.load(f)
        self.df = pd.DataFrame()
        self.timedict = {9: {35: 0, 40: 1, 45: 2, 50: 3, 55: 4},
                         10: {0: 5, 5: 6, 10: 7, 15: 8, 20: 9, 25: 10, 30: 11, 35: 12, 40: 13, 45: 14, 50: 15, 55: 16},
                         11: {0: 17, 5: 18, 10: 19, 15: 20, 20: 21, 25: 22, 30: 23},
                         13: {35: 24, 40: 25, 45: 26, 50: 27, 55: 28},
                         14: {0: 29, 5: 30, 10: 31, 15: 32, 20: 33, 25: 34, 30: 35, 35: 36, 40: 37, 45: 38, 50: 39,
                              55: 40},
                         15: {0: 41, 5: 42, 10: 43, 15: 44, 20: 45, 25: 46, 30: 47}
                         }

    def now_pos(self):
        now = datetime.datetime.now()
        cur_h, cur_m = now.hour, now.minute // 5
        try:
            pos = self.timedict[cur_h][cur_m] + 1
        except:
            if cur_h < 10:
                pos = 0
            elif cur_h < 14:
                pos = 24
            else:
                pos = 48
        return pos

    def reload(self, days=24):
        self.df = pd.DataFrame()
        for ind, ls in tqdm(self.symbol.items()):
            for s in ls:
                url = self.url1 + s + self.url2 + str(self.now_pos() + days)
                df = requests.get(url).text
                df = json.loads(df)
                df = pd.DataFrame(df)
                df['datetime'] = pd.to_datetime(df.day)
                df = df.set_index(['datetime'])
                df['day'] = df.index.date
                df['ukey'] = s
                df['industry'] = ind
                time.sleep(1)
                self.df = self.df.append(df)
        self.df = self.df.reset_index()
        self.df.set_index(['ukey', 'datetime'])

    def show(self):
        print(self.df.head())

    @staticmethod
    def candleplot(df, name, freq='5min'):
        df = df.resample(freq).last().dropna(axis=0)
        sma_5 = talib.SMA(df.close.values.astype('float'), 5)
        sma_20 = talib.SMA(df.close.values.astype('float'), 20)
        sma_60 = talib.SMA(df.close.values.astype('float'), 60)

        fig = plt.figure(figsize=(16, 12))
        ax = fig.add_axes([0, 0.2, 1, 0.5])
        ax2 = fig.add_axes([0, 0, 1, 0.2])

        candlestick2_ochl(ax, df['open'].astype('float'), df['close'].astype('float'), df['high'].astype('float'),
                          df['low'].astype('float'),
                          width=0.5, colorup='r', colordown='g', alpha=0.6)
        ax.set_xticks(range(0, len(df['day']), 48))
        ax.plot(sma_5, linewidth=0.5, label='MA 5')
        ax.plot(sma_20, linewidth=0.5, label='MA 20')
        ax.plot(sma_60, linewidth=0.5, label='MA 60')
        ax.legend(loc='upper left')
        plt.title(name)
        ax.grid(True)

        volume_overlay(ax2, df['open'].astype('float'), df['close'].astype('float'), df['volume'].astype('float'),
                       colorup='r', colordown='g', width=0.5, alpha=0.8)
        ax2.set_xticks(range(0, len(df['day']), 48))
        ax2.set_xticklabels(df['day'][::48], rotation=45)
        ax2.grid(True)
        plt.savefig('pics/'+name+'.png', bbox_inches='tight')
        plt.show(bbox_inches='tight')

    def show_all(self, days=20):
        for ind, ls in tqdm(self.symbol.items()):
            for s in ls:
                url = self.url1 + s + self.url2 + str(48*days)
                df = requests.get(url).text
                df = json.loads(df)
                df = pd.DataFrame(df)
                df['datetime'] = pd.to_datetime(df.day)
                df = df.set_index(['datetime'])
                df['day'] = df.index.date
                df['ukey'] = s
                df['industry'] = ind
                self.candleplot(df, s, freq='10min')
                time.sleep(1)

if __name__=='__main__':
    sina = Sina()
    sina.show_all()