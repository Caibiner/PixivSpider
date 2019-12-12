import os
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
from threading import Thread


def login(username, password):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'
        , 'Referer': ""
    }
    session = requests.session()
    response = session.get('https://accounts.pixiv.net/login?lang=zh')
    soup = BeautifulSoup(response.text, 'lxml')
    for i in soup.find_all('input'):
        if i.get('name') == 'post_key':
            post_key = i.get('value')
    data = {
        'pixiv_id': username,
        'password': password,
        'post-key': post_key
    }
    session.post('https://accounts.pixiv.net/login?lang=zh', data=data, headers=headers)
    return session


def get_author_img_dic(author_id, username, password):
  
    session = login(username, password)
    response = session.get('https://www.pixiv.net/ajax/user/' + author_id + '/profile/all')
    
    global false, null, true
    false = 'False'
    null = 'None'
    true = 'True'
    author_img_dic = eval(response.content)['body']
    return author_img_dic


def get_author_illusts(author_img_dic):  
    author_illusts_dic = author_img_dic['illusts']
    illusts_list = [key for key, value in author_illusts_dic.items()]
    return illusts_list


def get_author_manga(author_img_dic):  
    author_manga_dic = author_img_dic['manga']
    manga_list = [key for key, value in author_manga_dic.items()]
    return manga_list


def get_author_mangaSeries(author_img_dic): 
    author_mangaSeries_dic = author_img_dic['mangaSeries']
    mangaSeries_list = [key for key, value in author_mangaSeries_dic.items()]
    return mangaSeries_list


def get_img_dic(img_id, username, password):  
   
    img_dic = {}
  
    session = login(username, password)

   
    url_1 = 'https://www.pixiv.net/ajax/illust/' + img_id
    response_1 = session.get(url_1)
   
    global false, null, true
    false = 'False'
    null = 'None'
    true = 'True'
    response_1 = eval(response_1.content)['body']
    img_dic['illustID'] = response_1['illustId']  
    img_dic['illustTitle'] = response_1['illustTitle']  
    img_dic['illustDescription'] = response_1['illustComment'] 
    img_dic['createDate'] = response_1['createDate']  
    img_dic['uploadDate'] = response_1['uploadDate']  
    img_dic['tags'] = [] 
    for tag in response_1['tags']['tags']:
        img_dic['tags'].append(tag['tag'])
    img_dic['authorID'] = response_1['tags']['tags'][0]['userId']
    img_dic['authorName'] = response_1['tags']['tags'][0]['userName']

    
    url_2 = 'https://www.pixiv.net/ajax/illust/' + img_id + '/pages'

    response_2 = session.get(url_2)
    response_2 = eval(response_2.content)['body']
    img_dic['imgUrl'] = []  
    for img_url in response_2:
        img_dic['imgUrl'].append(img_url['urls']['original'].replace('\\', ''))

    return img_dic



def get_img_imformation(img_dic):
    img_imformation = {}
    img_imformation['img_url'] = img_dic['imgUrl']
    img_imformation['img_id'] = img_dic['illustID']
    img_imformation['img_title'] = img_dic['illustTitle']
    return img_imformation


def download(img_imformation, address):
    n = 0
    head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
        'Referer': 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=' + img_imformation['img_id']
    }
    for img_url in img_imformation['img_url']:
        img_response = requests.get(img_url, headers=head)
        image = img_response.content

        try:
            if n == 0:
                with open(address + '/' + img_imformation['img_title'] + '.jpg', 'wb') as jpg:
                    jpg.write(image)
            else:
                with open(address + '/' + img_imformation['img_title'] + '(' + str(n) + ')' + '.jpg', 'wb') as jpg:
                    jpg.write(image)
            jpg.close()
        except IOError:
            print("download error tring again \n")

        n = n + 1

if __name__ == '__main__':
    
    file = open(r'id', encoding='utf-8')
    while True:
       
        author_id = file.readline().replace('\n', '')
      
        author_img_dic = get_author_img_dic(author_id, 'aomiao9311z@qq.com', 'zhejiushimima')
        illusts_list = get_author_illusts(author_img_dic)
       
        print("ID%sprogress：\n"%author_id)
        for img_id in tqdm(illusts_list):
            img_dic = get_img_dic(img_id, 'aomiao9311z@qq.com', 'zhejiushimima')
            address = 'I://pixivs/' + img_dic['authorName']

            
            try:
                os.mkdir(address)
            except:
                img_imformation = get_img_imformation(img_dic)
                
                list_t = []
                for i in img_imformation:
                    t1 = Thread(target=download, args=(img_imformation, address))
                    t1.start()
                    list_t.append(t1)
                for j in list_t:
                    j.join()
            else:
                img_imformation = get_img_imformation(img_dic)
                for i in img_imformation:
                    t1 = Thread(target=download, args=(img_imformation, address))
                    t1.start()
                    list_t.append(t1)
                for j in list_t:
                    j.join()
        if author_id == '':
            break
    file.close()
