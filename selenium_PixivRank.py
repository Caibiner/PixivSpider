from bs4 import BeautifulSoup
import re,os,time
import requests
from selenium import webdriver
from lxml import etree
from threading import Thread
from tqdm import tqdm
import arrow


def isLeapYear(years):
    '''
    通过判断闰年，获取年份years下一年的总天数
    :param years: 年份，int
    :return:days_sum，一年的总天数
    '''
    # 断言：年份不为整数时，抛出异常。
    assert isinstance(years, int), "请输入整数年，如 2018"

    if ((years % 4 == 0 and years % 100 != 0) or (years % 400 == 0)):  # 判断是否是闰年
        # print(years, "是闰年")
        days_sum = 366
        return days_sum
    else:
        # print(years, '不是闰年')
        days_sum = 365
        return days_sum


def getAllDayPerYear(years):
    '''
    获取一年的所有日期
    :param years:年份
    :return:全部日期列表
    '''
    start_date = '%s-1-1' % years
    a = 0
    all_date_list = []
    days_sum = isLeapYear(int(years))
    print()
    while a < days_sum:
        b = arrow.get(start_date).shift(days=a).format("YYYYMMDD")
        a += 1
        all_date_list.append(b)
    # print(all_date_list)
    return all_date_list

#获取内容模块
# url = 'https://i.pximg.net/img-original/img/2019/12/18/18/06/53/78354921_p0.jpg'
# https://i.pximg.net/c/240x480/img-master/img/2019/12/19/00/05/19/78361447_p0_master1200.jpg'
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'
        , 'Referer':'https://www.pixiv.net/ranking.php?mode=weekly_r18'
        #https://www.pixiv.net/member_illust.php?mode=medium&illust_id=70639869
    }

# os.startfile("C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe")

# import os
# os.system("cd C:\\Program Files (x86)\\Google\\Chrome\\Application")
# os.system("chrome.exe --remote-debugging-port=9222 --user-data-dir=\"C:\\selenum\\AutomationProfile\"")
# 1.先打开windows cmd 进入chrome安装目录，一般在C:\Program Files (x86)\Google\Chrome\Application下，然后运行
# chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\selenum\AutomationProfile"


def selenium_re(content,type,date):

    
    if content=='本周':
        ucontent = 'weekly'
    elif content =='本月':
        ucontent = 'monthly'
    elif content =='受男性欢迎':
        ucontent =='male'
    elif content=='受女性欢迎':
        ucontent='female'
    elif content=='原创':
        ucontent='original'
    else:
        ucontent ='daily'

    if type=='R-18':
        utype = '_r18'
    elif content =='R-18G':
        utype = '_r18g'
    else:
        utype ='' 
    
    chrome_dir = r'C:\Users\aomia\AppData\Local\Google\Chrome\User Data'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("user-data-dir="+os.path.abspath(chrome_dir))
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get('https://www.pixiv.net/ranking.php?mode=%s%s&date=%s'%(ucontent,utype,date))
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    html = driver.page_source
    driver.close()
    return html
def html_re(html):
    print("正在获取页面信息。。。")
    soup = BeautifulSoup(html,'lxml')
    div = soup.find(id="wrapper")
    #经过观察，找出本页里有的图片
    #如果是动图，就找出span中有多少张，然后通过 class = work _work multiple 来为url加标记
    img_url=[]
    for script in div.find_all('img'):
        img_url.append(script['data-src'])

    url_list = []

    for ur in img_url:
        url_png ='https://i.pximg.net/img-original/img/'+re.findall(r'/img/(.+?)_',ur)[0]+'_p0.png'
    
        url_list.append(url_png)
        url_jpg ='https://i.pximg.net/img-original/img/'+re.findall(r'/img/(.+?)_',ur)[0]+'_p0.jpg'
        url_list.append(url_jpg)
        
    return url_list
#下载模块
def download(url_list,content,type,date,address):
    print("正在下载...")
    #P给图片取名
    p = 1
    path = address+date+content+type+'/'
    if not os.path.exists(path):
        os.mkdir(path)
    for url in tqdm(url_list):
        try:
            r = requests.get(url,headers=headers)
            if r.status_code ==200:
                with open('%s%d.jpg'%(path,p),'wb') as f:
                    f.write(r.content)
                    f.close()
        except:
            print("下载失败,重试")
            r = requests.get(url,headers=headers)
            if r.status_code==200:
                with open('%s%d.jpg'%(path,p),'wb') as f:
                    f.write(r.content)
                    f.close()
        p = p+1
def begin(t_list,content,type,date,address):
    html = selenium_re(content,type,date)
    url_list = html_re(html)
    t = Thread(target=download,args=(url_list,content,type,date,address))
    t_list.append(t)
    
if __name__ == "__main__":
#content：今日 本周 本月 新人 原创 受男性欢迎 受女性欢迎
#type ： 一般 R-18 R-18G
#date :日期 若填空字符串，则默认当前日期。
#注意R18 时，content 只有今日和本周
#address 地址
#今日只有 没有R18G 
# 本月 其他都填默认值 
    address ='D://pixiv/201803R18/'
    t_list = []

    day_list = getAllDayPerYear("2018")
    
    days = day_list[59:90]
    for day in days: 
        print("正在开始第%s"%day)
        begin(t_list,'今日','R-18',day,address)

    for t in t_list:
        t.start()
    for t in t_list:
        t.join()
