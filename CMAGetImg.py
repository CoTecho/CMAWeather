from json import loads
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from socket import timeout
from csv import reader

from bs4 import BeautifulSoup

import os


def getImgs():
    # 用于爬取所有天气图标
    # 实际上废弃
    url = 'https://weather.cma.cn/static/img/w/icon/w{}.png'
    i = 0
    os.makedirs('./image/', exist_ok=True)

    def urllib_download(i):
        from urllib.request import urlretrieve
        urlretrieve(url.format(i), './image/img{}.png'.format(i))

    while i < 100:
        try:
            urllib_download(i)
            print('download img{}'.format(i))
            i += 1
        except:
            print("不存在" + str(i))
            i += 1
            continue


def getImgs_Weather(city):
    # 思路：遍历所有城市，获取当前所有天气并与图片标号对应
    CMAAddr = 'https://weather.cma.cn/web/weather/{}.html'.format(city[0])
    try:
        html = urlopen(CMAAddr.format(city[0]), timeout=3)
        bsObj = BeautifulSoup(html)
        img_Weather = []
        dayList = bsObj.find("div", {"id": "dayList"}).findAll("div", {"class": "pull-left day actived"})
        dayList += bsObj.find("div", {"id": "dayList"}).findAll("div", {"class": "pull-left day"})
        for rawday in dayList:
            imgs = rawday.findAll("img")
            weathers = rawday.findAll("div", {"class": "day-item"})
            img_Weather.append([imgs[0].attrs["src"][20:-4], weathers[2].text.strip().strip('\\n')])
            img_Weather.append([imgs[1].attrs["src"][20:-4], weathers[7].text.strip().strip('\\n')])
        return img_Weather
    except HTTPError:
        # print("不存在编号" + str(cityNum))
        return ''
    except URLError:
        # print("超时重试")
        getImgs_Weather(city)
    except timeout:
        # print("超时重试")
        getImgs_Weather(city)


citys_file_read = open('citys.txt', mode='r', encoding='utf-8')
citys = [city for city in reader(citys_file_read)]
img_weather = [['1', '多云'], ['0', '晴'], ['8', '中雨'], ['14', '小雪'], ['2', '阴'], ['15', '中雪'], ['13', '阵雪'], ['7', '小雨'],
               ['6', '雨夹雪'], ['18', '雾'], ['26', '小到中雪'], ['23', '大到暴雨'], ['10', '暴雨'], ['4', '雷阵雨'], ['9', '大雨']]
errCity = [['50527', '国内', '内蒙古', '海拉尔'], ['52656', '国内', '甘肃', '民乐'], ['53685', '国内', '山西', '盂县'],
           ['53869', '国内', '山西', '霍州'], ['54603', '国内', '河北', '高阳'], ['56885', '国内', '云南', '弥勒'],
           ['57113', '国内', '陕西', '凤县'], ['57389', '国内', '湖北', '云梦'], ['57680', '国内', '湖南', '汨罗'],
           ['57966', '国内', '湖南', '宁远'], ['58361', '国内', '上海', '闵行'], ['042299', '国外', '不丹', '廷布'],
           ['G05014', '国外', '密克罗尼西亚联邦', '帕利基尔']]
counter = 0
for city in errCity:
    print(city[-1])
    rows = getImgs_Weather(city)
    # print(img_weather)
    counter += 1
    print(counter)
    if rows:
        for row in rows:
            if row not in img_weather:
                img_weather.append(row)
                print(row)
    else:
        errCity.append(city)
        print(city)
print(img_weather)
print(errCity)
citys_file_read.close()
