#
#
#注意自备梯子，自行修改路径。
#
#coder Bin
#
import os,re,time,requests
from threading import Thread
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from tqdm import tqdm

#获取内容模块
# url = 'https://i.pximg.net/img-original/img/2019/12/18/18/06/53/78354921_p0.jpg'
# https://i.pximg.net/c/240x480/img-master/img/2019/12/19/00/05/19/78361447_p0_master1200.jpg'
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'
        , 'Referer':'https://www.pixiv.net/ranking.php?mode=weekly_r18'
        #https://www.pixiv.net/member_illust.php?mode=medium&illust_id=70639869
    }

# import os

# os.system ("cd C:\Program Files (x86)\Google\Chrome\Application")
# os.system= ("chrome.exe --remote-debugging-port=9222 --user-data-dir=\"C:\selenum\AutomationProfile\"")
# 1.先打开windows cmd 进入chrome安装目录，一般在C:\Program Files (x86)\Google\Chrome\Application下，然后运行

# chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\selenum\AutomationProfile"
def selenium_re(content,type,date):
    year =date[:4] 
    month = date[4:6]
    day =date[6:]
    print("正在寻找页面。。。")

    #下面四行 为了启动已经打开的浏览器，绕过P站的reChat人机验证
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    chrome_driver = "C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
    driver = webdriver.Chrome(chrome_driver, options=chrome_options)

    driver.get("https://www.pixiv.net")
    driver.find_element_by_link_text('每日排行榜').click()#打开每日排行榜
    time.sleep(2)
    driver.find_element_by_link_text('排行榜日历').click()

    #如果设置了日期
    if date:
        #年
        count = 2019-int(year)
        while count!=0: 
            driver.find_element_by_link_text("<").click()
            count = count -1 
        time.sleep(1)

        #月
        driver.find_element_by_link_text(month+'月').click() 
        time.sleep(1)

        #日
        rank = driver.find_element_by_tag_name("tbody")
        td = rank.find_elements_by_tag_name('tr')[0].find_elements_by_css_selector("td[class='active']")
        num =7-len(td)
        ahref = rank.find_elements_by_tag_name('tr')[int((int(day)+num)/7)].find_elements_by_css_selector("td[class='active']")[(int(day)+num)%7-1]
        ahref.find_element_by_tag_name('a').click()
        time.sleep(1)
    
    #本周 本月 等
    driver.find_element_by_link_text(content).click()
    time.sleep(1)

    #找类型 R18 R18-G等
    if content !='本月':
        a = driver.find_element_by_css_selector("nav[class='column-menu']")
        a.find_element_by_link_text(type).click()
        time.sleep(1)

    #拉到最底 加载出所有文件
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #以免网速不够页面加载不全 等10s
    time.sleep(10)      
    #返回页面
    html  = driver.page_source 
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
 
    big_url = []

    # original_url=[]
    #把 data-src的url拼凑成original的url
    # for rurl in img_url:
    #     rea = re.findall(r"img/(.+?)_master",rurl)[0]
    #     url = 'https://i.pximg.net/img-original/img/'+rea+'.jpg'
    #     if rea :
    #         original_url.append(url)

    for ur in img_url:
        #把url中的大小去掉，比如https://i.pximg.net/img-master/img/2019/12/15/21/57/24/78312861_p0_master1200.jpg
        a = re.sub(r"c(.+?)/",'',ur)
        big_url.append(a)

    return big_url

#下载模块
def download(big_url,content,type,date):
    print("正在下载...")
    #P给图片取名
    p = 1
    address = 'I://pixivranks/'+date+content+type+'/'
    if not os.path.exists(address):
        os.mkdir(address)

    for url in tqdm(big_url):
        try:
            
            r = requests.get(url,headers=headers)
            with open('%s%d.jpg'%(address,p),'wb') as f:
                f.write(r.content)
                f.close()
        except:
            print("下载失败,重试") 
            r = requests.get(url,headers=headers)
            with open('%s%d.jpg'%(address,p),'wb') as f:
                f.write(r.content)
                f.close()
        p = p+1

def begin(content,type,date):
    html = selenium_re(content,type,date)
    bigimg_list = html_re(html)
    t = Thread(target=download,args=(bigimg_list,content,type,date))
    t.start()
    

if __name__ == "__main__":

#content：今日 本周 本月 新人 原创 受男性欢迎 受女性欢迎
#type ： 一般 R-18 R-18G 
#date :日期 若填空字符串，则默认当前日期。
#注意R18 时，content 只有今日和本周
#
   begin('本周','R-18','20180804')
















#回顾思路用，就是上面的html
# def htmlcankao():
#     <a href="/artworks/78331555"class="work  _work multiple  "target="_blank"><div class="_layout-thumbnail"><img src="https://s.pximg.net/www/images/common/transparent.gif"alt=""class="_thumbnail ui-scroll-view"data-filter="thumbnail-filter lazy-image"data-src="https://i.pximg.net/c/240x480/img-master/img/2019/12/17/00/06/16/78331555_p0_master1200.jpg"data-type="illust"data-id="78331555"data-tags="R-18 ポケモン剣盾 ユウリ(トレーナー) ポケモン人間絵 身体に落書き 仰け反り絶頂 腹ボコ ポケモン5000users入り"data-user-id="17929545"><div class="_one-click-bookmark js-click-trackable  "data-click-category="abtest_www_one_click_bookmark"data-click-action="illust"data-click-label="78331555"data-type="illust"data-id="78331555"></div></div><div class="page-count"><div class="icon"></div><span>4</span></div></a></div><h2><a href="/artworks/78331555"class="title"target="_blank"rel="noopener">ユウリちゃん1</a></h2><a class="user-container ui-profile-popup"href="/member.php?id=17929545&amp;ref=rn-b-3-user-3"title="床音"data-user_id="17929545"data-user_name="床音"data-profile_img="https://i.pximg.net/user-profile/img/2016/10/25/06/18/39/11664953_3c4533a7e9b87b66ac3fc3a6a82fab61_50.jpg">

