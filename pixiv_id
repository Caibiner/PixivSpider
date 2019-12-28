from bs4 import BeautifulSoup
import re,os,time
import requests
from selenium import webdriver
from lxml import etree
from threading import Thread
from tqdm import tqdm

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'
        , 'Referer':'https://www.pixiv.net/ranking.php?mode=weekly_r18'
        #https://www.pixiv.net/member_illust.php?mode=medium&illust_id=70639869
    }



def sele_id(author_id,page):
    print('正在请求第%d页...'%page)
    chrome_dir = r'C:\Users\admin\AppData\Local\Google\Chrome\User Data'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("user-data-dir="+os.path.abspath(chrome_dir))
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get('https://www.pixiv.net/member_illust.php?id=%s&p=%d'%(author_id,page))
    time.sleep(3)
    html = driver.page_source
    driver.close
    return html
def req_img(html):
    print("正在寻找图片地址....")
    dom = etree.HTML(html)
    imgs = dom.xpath('//img[contains(@src,"1200")]/@src')
    
    url_list = []
    for img in imgs:

        #拼凑大图
        url = 'https://i.pximg.net/img-master/img/'+re.findall(r'/img/(.+?)_',img)[0]+'_p0_master1200.jpg'
    
        url_list.append(url)
        
    return url_list

def download(url_list,author_id,address,page):
    print("正在下载第%d页..."%page)
    #给图片取名
    name = 1

    path = address+author_id+'/'

    if not os.path.exists(path):
        os.mkdir(path)

    for url in tqdm(url_list):
        try:
            
            r = requests.get(url,headers=headers)
            with open('%s%d(%d).jpg'%(path,page,name),'wb') as f:
                f.write(r.content)
                f.close()
        except:
            print("下载失败,重试") 
            r = requests.get(url,headers=headers)
            with open('%s%d(%d).jpg'%(path,page,name),'wb') as f:
                f.write(r.content)
                f.close()
        name = name+1

def begin(author_id,address):
    page = 1
   
    while page>0:
        print("开始爬取第%d页..."%page)

        html = sele_id(author_id,page)

        url_list = req_img(html)

        #如果是空列表，证明到底了，返回

        if  len(url_list)==0:
            return
        t = Thread(target=download,args=(url_list,author_id,address,page))
        t.start()
        
        page = page+1
        time.sleep(5)
    

if __name__ == "__main__":

    
    begin('490219','I://pixivs/')
    print("下载完成")
    

