# 从CMA获取天气的模块
# 挪威奥斯陆页面无信息故忽略
from json import loads
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from socket import timeout
from csv import reader

from bs4 import BeautifulSoup


def transKey2Str(jsonDict):
    # 将键值转为str
    for key in jsonDict:
        if isinstance(jsonDict[key], dict):
            transKey2Str(jsonDict[key])
        else:
            jsonDict[key] = str(jsonDict[key])
            # print(type(jsonDict[key]))
    return jsonDict


def transImg2Weather(data):
    # 将天气图像转为文字
    # 部分转换不确定
    weatherList = ['晴', '多云', '阴', '阵雨', '雷阵雨', '雷阵雪', '雨夹雪', '小雨', '中雨', '大雨', '暴雨', '大暴雨', '特大暴雨', '阵雪', '小雪', '中雪',
                   '大雪', '暴雪', '雾', '冻雨', '浮尘', '小到中雨', '中到大雨', '大到暴雨', '暴雨到大暴雨', '大到特大暴雨', '小到中雪', '中到大雪', '大到暴雪',
                   '日间浮尘', '夜空晴', '浮尘夜', '夜雾', '大雨夜', '中雪夜', '夜间浮沉', '大雨夜', '雾', '霾', '霾', '霾', '霾', '雾', '雾']

    weather = data.find("img").attrs["src"][20:-4]
    return weatherList[int(weather)]


def getCMATable(rawTable):
    # 此函数将CMA网站上的每日天气表读取为数组
    # 格式为 [时间,天气,气温,降水,风速,风向,气压,湿度,云量]
    table = [[], [], [], [], [], [], [], []]
    # print(table)
    rows = rawTable.findAll("tr")
    for row in range(9):
        datas = rows[row].findAll("td")
        for i in range(8):
            table[i].append(datas[i + 1].text)
            if row == 1: table[i][1] = transImg2Weather(datas[i + 1])
            # print(datas[i+1].text)
        # print('换行')
    return table


def getCMARealWeather(cityNum,times=5):
    if times<=0:return
    times-=1
    url = 'https://weather.cma.cn/api/now/{}'.format(cityNum)
    try:
        data = urlopen(url).read()
        # data = decompress(data).decode('utf-8')
        dict = loads(data)
        return dict
    except HTTPError:
        # print("不存在编号" + str(cityNum))
        return ''
    except URLError:
        # print("超时重试")
        CMAWeatherTable(cityNum,times)
    except timeout:
        # print("超时重试")
        CMAWeatherTable(cityNum,times)


def CMAWeatherTable(cityNum, times=5):
    if times<=0:return
    times-=1
    CMAAddr = 'https://weather.cma.cn/web/weather/{}.html'
    try:
        html = urlopen(CMAAddr.format(cityNum), timeout=3)
        weather = {}
        weatherTable = []
        bsObj = BeautifulSoup(html)
        #print(bsObj)
        weather["city"] = bsObj.find("div", {"id": "cityPosition"}).findAll("button")[-1].text
        rawTables = bsObj.findAll("table", {"class": "hour-table"})
        # weatherTable=read_html(CMAAddr.format(cityNum))
        for rawTable in rawTables:
            weatherTable.append(getCMATable(rawTable))
        return weatherTable
    except HTTPError:
        # print("不存在编号" + str(cityNum))
        return ''
    except URLError:
        # print("超时重试")
        CMAWeatherTable(cityNum,times)
    except timeout:
        # print("超时重试")
        CMAWeatherTable(cityNum,times)

def getCMAWeekWeather(cityNum, times=5):
    if times<=0:return
    times-=1
    #此函数用于获取当天最高温与最低温及天气，同时为没有实时信息的城市返回天气数据
    # 返回值为一个含有七天天气数据的列表，每天天气用字典存储(也可能是六天)
    CMAAddr = 'https://weather.cma.cn/web/weather/{}.html'.format(cityNum)
    try:
        html = urlopen(CMAAddr.format(cityNum), timeout=3)
        bsObj = BeautifulSoup(html)
        dayList = bsObj.find("div", {"id": "dayList"}).findAll("div", {"class": "pull-left day actived"})
        dayList += bsObj.find("div", {"id": "dayList"}).findAll("div", {"class": "pull-left day"})
        weekWeather=[{},{},{},{},{},{},{}]
        for dayN in range(len(dayList)):
            day=dayList[dayN]
            dayDetailes=day.findAll("div")
            weekWeather[dayN]["day"]=dayDetailes[0].text.replace(" ","").replace("\n"," ").strip(" ")
            weekWeather[dayN]["weatherA"]=dayDetailes[2].text.replace(" ","").strip("\n")
            weekWeather[dayN]["windA"]=dayDetailes[3].text.replace(" ","").strip("\n")
            weekWeather[dayN]["forceA"]=dayDetailes[4].text.replace(" ","").strip("\n")
            weekWeather[dayN]["weatherB"]=dayDetailes[10].text.replace(" ","").strip("\n")
            weekWeather[dayN]["windB"]=dayDetailes[11].text.replace(" ","").strip("\n")
            weekWeather[dayN]["forceB"]=dayDetailes[12].text.replace(" ","").strip("\n")
            weekWeather[dayN]["high"]=day.find("div",{"class": "high"}).text.replace('\n','').strip()
            weekWeather[dayN]["low"]=day.find("div",{"class": "low"}).text.replace('\n','').strip()
            #i=0
            #for day in dayDetailes:
            #    print(str(i)+": "+day.text.replace(" ","").strip("\n"))
            #    i+=1
        return weekWeather
    except HTTPError:
        # print("不存在编号" + str(cityNum))
        return ''
    except URLError:
        # print("超时重试")
        getCMAWeekWeather(cityNum,times)
    except timeout:
        # print("超时重试")
        getCMAWeekWeather(cityNum,times)
        return

def getCityNum(name):
    # 将城市名转换为编号
    citys_file_read = open('citys.txt', mode='r', encoding='utf-8')
    citys = [city for city in reader(citys_file_read)]
    for city in citys:
        if name == city[3]:
            return int(city[0])
    else:
        return 0


def getWeather(city):
    # 获取天气--完善
    global weather
    cityNum = getCityNum(city)
    if not cityNum:
        return ""
    jsondict = getCMARealWeather(cityNum)
    dayWeather=getCMAWeekWeather(cityNum)[0]
    # print(type(str(jsondict.get("name"))))
    if jsondict:
        # 判断get请求是否成功
        if jsondict["data"]:
            # 判断是否返回正确数据
            weatherDict = transKey2Str(jsondict)["data"]["now"]
            if weatherDict.get("temperature")=="9999.0":
                #说明没有该城市详细天气，使用整日天气代替
                weather="该城市无实时天气信息，以下为当日预报\n"
                weather += '城市：' + city + '\n'
                if dayWeather['weatherA']==dayWeather['weatherB']:
                    weather+='天气：'+dayWeather["weatherA"] + '\n'
                else:
                    weather+='天气：'+dayWeather["weatherA"]+"转"+dayWeather["weatherB"] + '\n'
                weather += '高温：' + dayWeather["high"] + '\n'
                weather += '低温：' + dayWeather["low"] + '\n'
                if dayWeather['windA']==dayWeather['windB']:
                    weather+='风向：'+dayWeather["windA"] + '\n'
                else:
                    weather+='风向：'+dayWeather["windA"]+"转"+dayWeather["windB"] + '\n'
                if dayWeather['forceA']==dayWeather['forceB']:
                    weather+='风力：'+dayWeather["forceA"] + '\n'
                else:
                    weather+='风力：'+dayWeather["forceA"]+"到"+dayWeather["forceB"] + '\n'
                weather+='日期：'+dayWeather["day"]+'\n'
                return weather
            weather = '城市：' + city + '\n'
            # print(weatherDict)
            if dayWeather['weatherA']==dayWeather['weatherB']:
                weather+='天气：'+dayWeather["weatherA"] + '\n'
            else:
                weather+='天气：'+dayWeather["weatherA"]+"转"+dayWeather["weatherB"] + '\n'
            weather += '温度：' + weatherDict.get("temperature") + '℃\n'
            weather += '高温：' + dayWeather["high"] + '\n'
            weather += '低温：' + dayWeather["low"] + '\n'
            weather += '湿度：' + weatherDict.get("humidity") + '%\n'
            weather += '气压：' + weatherDict.get("pressure") + 'hPa\n'
            if weatherDict.get("precipitation")=="9999.0":
                weather += '降水量：' + '-\n'
            else:
                weather += '降水量：' + weatherDict.get("precipitation") + 'mm\n'
            weather += '风向：' + weatherDict.get("windDirection") + '\n'
            weather += '风力：' + weatherDict.get("windScale") + '\n'
            weather += '风速：' + weatherDict.get("windSpeed") + 'm/s\n'
            weather += '更新时间：' + jsondict.get("data").get("lastUpdate")
        else:

            weather = "城市编码出错。"
    else:
        return "get请求出错。"
    return weather


#cityNum = "57083"
#print(getCMAWeekWeather(cityNum))
#print(getWeather("高雄"))
print(getWeather("七台河"))
