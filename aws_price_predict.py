##################################################################
# Readme:
# This source file contains two parts:
# 1. getRawData: this is not part of the algorithm and should only
# be used to generate some testing data for the algorithm
# 2. PriceForecast: this is the algorithm, its input and output.
# To use the class, simply call PriceForecast.forecast(inputJson),
# with inputJson passed in and it will return results as json. The
# input and output string format is explained as below:
# Input:
#     A json string, formated as:
#     {"dates":[d1, d2, ...], "prices":[p1, p2, ...]}
#     The two arrays must be of same length
# Output:
#     A json string, formated as:
#     {
#         "status": 200,
#         "msg": error message if any,
#	      "data": 
#         [
#		      {"date": d1, "price": p, "upper": u, "lower": u},
#		      {"date": d1, "price": p, "upper": u, "lower": u},
#		      ...
#	      ]
#         // num_predicted_days, predicted_min_price, predicted_max_price, predicted_avg_price
#	      "price_range_predicted": {"days": d, "min": b, "max":e, "avg":a} 
#     }
##################################################################

import json
import pandas as pd
from fbprophet import Prophet
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

# warnings.filterwarnings("ignore")
# plt.style.use('fivethirtyeight')

# import matplotlib

def getRawData():
    url = 'https://www.fakespot.com/product/phone-charger-yunsong-3pack-6ft-nylon-braided-charging-cable-cord-usb-cable-charger-compatible-with-phone-pad-gray-6ft-3pack'
    url = 'https://www.fakespot.com/product/sandisk-ultra-32gb-class-10-sdhc-uhs-i-memory-card-up-to-80mb-sdsdunc-032g-gn6in'
    url = 'https://www.fakespot.com/product/logitech-mk270-wireless-keyboard-and-mouse-combo-keyboard-and-mouse-included-2-4ghz-dropout-free-connection-long-battery-life-frustration-free-packaging'
    url = 'https://www.fakespot.com/product/victsing-wireless-keyboard-and-mouse-combo-stylish-full-size-keyboard-and-quiet-mouse-2-4ghz-wireless-connection-with-usb-receiver-for-desktop-computer-laptop-pc-windows-black-9172e854-172f-4f84-aa56-df7ca14a34e8'
    url = 'https://www.fakespot.com/product/oculus-quest-all-in-one-vr-gaming-headset-64gb'
    url = 'https://www.fakespot.com/product/xbox-controller-cable-for-windows'
    url = 'https://www.fakespot.com/product/apple-iphone-8-4-7-64-gb-fully-unlocked-space-gray-certified-refurbished'
    url = 'https://www.fakespot.com/product/pampers-swaddlers-disposable-diapers'
    url = 'https://www.fakespot.com/product/philips-sonicare-protectiveclean-4100-electric-rechargeable-toothbrush-plaque-control-black'
    url = 'https://www.fakespot.com/product/quick-charge-2-0-ravpower-40w-4-port-usb-quick-charger-with-ismart-for-galaxy-s7-s6-edge-plus-note-5-4-lg-g4-g5-nexus-6-and-more-white'
    url = 'https://www.fakespot.com/product/hp-63-black-tri-color-original-ink-cartridges-2-pack-l0r46an'
    url = 'https://www.fakespot.com/product/hp-officejet-3830-wireless-color-photo-printer-with-scanner-and-copier'
    url = 'https://www.fakespot.com/product/xiaomi-mi-band-4-0-95-3-color-amoled-screen-smart-bracelet-smartband-heart-rate-monitor-sleep-monitor-fitness-tracker-bluetooth-sport-5atm-waterproof-smart-band-standard-version-global-version'
    url = 'https://www.fakespot.com/product/robot-vacuum-goovi-1600pa-robotic-vacuum-cleaner-with-self-charging-360-smart-sensor-protectio-multiple-cleaning-modes-vacuum-best-for-pet-hairs-hard-floor-medium-carpet'
    url = 'https://www.fakespot.com/product/xiaomi-redmi-note-7-64gb-4gb-ram-6-30-fhd-snapdragon-660-black-unlocked-global-version'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    dates_str = '' # Store all dates in string, separated by ,
    prices_str = '' # Store all prices in string, separated by ,

    for script in soup.find_all('script'):
        if 'chart-2' in script.text:
            data_begin_index = script.text.find('[', 0)
            data_end_index = script.text.find('{', 0)
            content = script.text[data_begin_index:data_end_index-2].strip()
            print(content)
            array = content.replace('],[', '][').split(']')
            for a in array:
                if len(a) == 0:
                    break
                kv = a.replace('[', '').replace('"', '').replace(']', '').split(',')
                # print(kv)
                dates_str = dates_str + ',' + '"' + kv[0] + '"'
                prices_str = prices_str + ',' + '"' + kv[1] + '"'
                
                # val = tu[3].find('.', 0) 
                # s = tu[3][0:val+3]
                # if s[-1] == '.':
                #     s = s[0:-1]    
                # raw_data.append((datetime.strptime(tu[0][0:-3], '%Y-%m-%d'), float(s)))
            break
        
    json_str = '{' + '"dates":[{0}],"prices":[{1}]'.format(dates_str[1:], prices_str[1:]) + '}'
    return json_str

# getRawData()

class PriceForecast():
    def __init__(self):
        self.rawData = []
        # status code:
        # 200 - successful
        # 300 - dates and prices are different in lengths
        # 400 - last actual date is too far away from current date
        # 500 - other exceptions!
        self.statusCode = 200
        self.errorMsg = ''

    def readInRawData(self, inputJson):
        # print(inputJson)

        try:
            obj = json.loads(inputJson)
            dates = obj['dates']
            prices = obj['prices']
            if len(dates) != len(prices):
                self.statusCode = 300
                self.errorMsg = 'Input dates and prices are not the same in length'
                return

            for i in range(len(dates)):
                date = datetime.strptime(dates[i][0:10], '%Y-%m-%d')
                price = float(prices[i])
                self.rawData.append((date, price))
        except Exception as exp:
            self.statusCode = 500
            self.errorMsg = str(exp)
            return

        # print(self.rawData)
        
    def fillGaps(self):
        # Fill up gaps
        fullData = {}

        for i in range(1, len(self.rawData)):
            end = self.rawData[i]
            start = self.rawData[i-1]
            print('end: ', self.rawData[i])
            print('start: ', self.rawData[i - 1])
            gap = (end[0] - start[0]).days
            print('gap: ', gap)
            if gap > 0:
                delta = (end[1] - start[1]) / gap
            
                d = start[0]
                # s = start[1]
                g = 0
            
                while d < end[0]:
                    fullData[d.strftime('%Y-%m-%d')] = start[1] + g * delta
                    d = d + timedelta(days=1)
                    g = g + 1

        fullData[self.rawData[-1][0].strftime('%Y-%m-%d')] = self.rawData[-1][1]
        # print(fullData)
        return fullData

    def calDaysNeedToPredict(self):
        actualDateSpan = (self.rawData[-1][0] - self.rawData[0][0]).days
        lastActualDate = self.rawData[-1][0]
        curDate = datetime.now()
        print('actualDateGap:{0}, lastActualDate:{1}, curDate:{2}'.format(actualDateSpan, lastActualDate, curDate))
        curAndDataDateSpan = (curDate - lastActualDate).days
        print('Days between last actual and current:{0}'.format(curAndDataDateSpan))
        if curAndDataDateSpan > actualDateSpan:
            self.statusCode = 400
            self.errorMsg = 'Last actual date is too far away from today'

        # Return number of days to predict
        if actualDateSpan > 90:
            return curAndDataDateSpan + 90
        elif actualDateSpan > 30:
            return curAndDataDateSpan + 30
        elif actualDateSpan > 10: 
            return curAndDataDateSpan + 10
        
        return 1
        
    def forecast(self, inputJson):
        self.readInRawData(inputJson)

        if self.statusCode != 200:
            return '{{"status":{0}, "msg":{1}}}'.format(self.statusCode, self.errorMsg)

        last_actual_date = self.rawData[-1][0]
        data = self.fillGaps()
        sales = {}

        sales['ds'] = list(data.keys())
        sales['y'] = list(data.values())

        df = pd.DataFrame(sales)
        df['ds'] = pd.DatetimeIndex(df['ds'])

        # print(df)

        my_model = Prophet(interval_width=0.95, changepoint_range=1.0, changepoint_prior_scale=0.0026, weekly_seasonality=True, yearly_seasonality=True, daily_seasonality=True)
        my_model.fit(df)

        daysToPredict = self.calDaysNeedToPredict()
        futureDates = my_model.make_future_dataframe(periods=daysToPredict, freq='D')

        forecast = my_model.predict(futureDates)
        forecast['yhat'][forecast['yhat'] <= 0] = forecast['yhat'][forecast['yhat'] > 0].min()
        
        predicts = forecast[forecast['ds'] > last_actual_date].values.tolist()
        print('Forecast result:')
        print(predicts)

        for p in predicts:
            print('ds:{0}, yhat:{1}, yhat_lower:{2}, yhat_upper:{3}'.format(p[0], p[-1], p[2], p[3]))

        forecastMean = round(forecast[forecast['ds'] > last_actual_date]['yhat'].mean(), 2)
        forecastMin = round(forecast[forecast['ds'] > last_actual_date]['yhat'].min(), 2)
        forecastMax = round(forecast[forecast['ds'] > last_actual_date]['yhat'].max(), 2)
        print('Price range of actual sample: (${0}, ${1})'.format(df['y'].min(), df['y'].max()))
        print("Price range of the next 90 days: (${0}, ${1}), with an average of ${2}".format(forecastMin, forecastMax, forecastMean))

        # Construct final results: mix actual and predict together
        dataStr = []
        
        # First goes in raw data
        for raw in self.rawData:
            dataStr.append('{"date":"' + str(raw[0]) + '","price":' + str(round(raw[1],4)) + ',"upper":' + str(round(raw[1],4)) + ',"lower":' + str(round(raw[1],4)) + '}')
            
        # Then goes in predicted data
        for p in predicts:
            dataStr.append('{"date":"' + str(p[0]) + '","price":' + str(round(p[-1],4)) + ',"upper":' + str(round(p[3],4)) + ',"lower":' + str(round(p[2],4)) + '}')

        statusStr = '"status":{0},"msg":"{1}"'.format(self.statusCode, self.errorMsg)
        predictedPriceRangeStr = '"price_range_predicted":{{"days":{0},"min":{1},"max":{2},"avg":{3}}}'.format(daysToPredict, round(forecastMin,4), round(forecastMax,4), round(forecastMean,4))

        retJson = '{' + statusStr + ',"data":[' + ','.join(dataStr) + '],' + predictedPriceRangeStr + '}'
        # print(retJson)
        return retJson

if __name__ == '__main__':
    o = PriceForecast()
    with open('test_output', 'w', newline='', encoding='utf-8') as outfile:
        outfile.write(o.forecast(getRawData()))