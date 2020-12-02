from json import loads
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from socket import timeout

from bs4 import BeautifulSoup


def CMACitysA(cityNum):
    # 方法1：逐一尝试
    CMAAddr = 'https://weather.cma.cn/web/weather/{:06}.html'
    try:
        html = urlopen(CMAAddr.format(cityNum), timeout=3)
        # 日志写对象
        log_file_write = open('citys.txt', mode='a', encoding='utf-8')
        # 读取日志
        log_file_read = open('citys.txt', mode='r', encoding='utf-8')
        log = log_file_read.readlines()
        city = "{:06}".format(cityNum)
        bsObj = BeautifulSoup(html)
        cityAddr = bsObj.find("div", {"id": "cityPosition"}).findAll("button")
        for addr in cityAddr:
            city += "," + addr.text.strip()
        if city + '\n' not in log:
            # 打印
            print(city)
            # 保存
            log_file_write.write(city + '\n')
            # 添加到日志列表
            log.append(city + '\n')
        city = ''
    except HTTPError:
        print("不存在编号{:06}".format(cityNum))
    except URLError:
        print("超时重试")
        CMACitysA(cityNum)
    except timeout:
        print("超时重试")
        CMACitysA(cityNum)


def CMACitysB(country):
    # 方法2：根据列表请求查询,用于外国城市编号爬取
    CMAAddr = "https://weather.cma.cn/api/dict/country/"
    try:
        data = urlopen(CMAAddr + country[0], timeout=3).read()
        dict = loads(data)
        # print(data)
        citys = []
        rawCitys = dict['data'].split('|')
        for city in rawCitys:
            citys.append(city.split(','))

        for rawcity in citys:
            city = rawcity[0] + "," + '国外' + "," + country[1] + "," + rawcity[1]
            # 日志写对象
            log_file_write = open('citys.txt', mode='a', encoding='utf-8')
            # 读取日志
            log_file_read = open('citys.txt', mode='r', encoding='utf-8')
            log = log_file_read.readlines()
            if city + '\n' not in log:
                # 打印
                print(city)
                # 保存
                log_file_write.write(city + '\n')
                # 添加到日志列表
                log.append(city + '\n')
        city = ''
    except HTTPError:
        print("不存在编号{}".format(country))
    except URLError:
        print("超时重试")
        CMACitysB(country)
    except timeout:
        print("超时重试")
        CMACitysB(country)


def getCountrys():
    # 获取国家列表
    url = "https://weather.cma.cn/api/dict/country"
    data = urlopen(url).read()
    dict = loads(data)
    # print(data)
    countrys = []
    rawCountrys = dict['data'].split('|')
    for country in rawCountrys:
        countrys.append(country.split(','))
    return countrys

# countrys=getCountrys()
# for country in countrys:
#    CMACitysB(country)
