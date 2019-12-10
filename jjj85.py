import time

import requests
from bs4 import BeautifulSoup

import re

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    ,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
}

def writepage(urating, page):
    import pandas as pd
    dataframe = pd.DataFrame(urating)
    dataframe.to_csv('jjj85.csv', mode='a', index=True, sep=',', header=False)
    print("已爬%s个连接" % page)


if __name__ == '__main__':
    for page in range(1000):
        url = 'http://40ppn.com/mlshow.x?stype=mlmovie&movieid=' + str(page)
        try:
            r = requests.get(url, headers=headers)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            soup = BeautifulSoup(r.text, 'lxml')
            content = soup.find('a', oncontextmenu='ThunderNetwork_SetHref(this)')

            thunder = content['thunderhref']
            name = content.string
            thunder_list = []
            thunder_list.append(name)
            thunder_list.append(thunder)
            print(thunder_list)
            writepage(thunder_list,page)
        except:
            print("失败了")


