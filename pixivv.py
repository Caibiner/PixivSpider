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
    # 获取作者的全部作品字典
    # 登录用户
    session = login(username, password)
    response = session.get('https://www.pixiv.net/ajax/user/' + author_id + '/profile/all')
    # 不加以下这些会报错，似乎是因为eval()不能处理布尔型数据
    global false, null, true
    false = 'False'
    null = 'None'
    true = 'True'
    author_img_dic = eval(response.content)['body']
    return author_img_dic


def get_author_illusts(author_img_dic):  # 从author_img_dic中获取作者的插画与动图ID
    author_illusts_dic = author_img_dic['illusts']
    illusts_list = [key for key, value in author_illusts_dic.items()]
    return illusts_list


def get_author_manga(author_img_dic):  # 从author_img_dic中获取作者的漫画ID
    author_manga_dic = author_img_dic['manga']
    manga_list = [key for key, value in author_manga_dic.items()]
    return manga_list


def get_author_mangaSeries(author_img_dic):  # 从author_img_dic中获取作者的漫画系列ID
    author_mangaSeries_dic = author_img_dic['mangaSeries']
    mangaSeries_list = [key for key, value in author_mangaSeries_dic.items()]
    return mangaSeries_list


def get_img_dic(img_id, username, password):  # 传入图片ID，返回该图片ID下的信息，具体信息见注释
    '''
    img_dic = {
        'illustID' : 插画ID
        'illustTitle' : 插画标题
        'illustDescription' : 插画简介
        'createDate' : 插画创建时间
        'uploadDate' : 插画更新时间
        'tags' : 插画tag,值为列表
        'authorID' : 作者ID
        'authorName' : 作者昵称
        'imgUrl' : 插画原始大小url,值为列表
    }
    '''
    img_dic = {}
    # 登录用户
    session = login(username, password)

    # 获取第一个文件的信息，把除了图片url以外的东西先拿到
    url_1 = 'https://www.pixiv.net/ajax/illust/' + img_id
    response_1 = session.get(url_1)
    # 不加以下这些会报错，似乎是因为eval()不能处理布尔型数据
    global false, null, true
    false = 'False'
    null = 'None'
    true = 'True'
    response_1 = eval(response_1.content)['body']
    img_dic['illustID'] = response_1['illustId']  # 图片ID
    img_dic['illustTitle'] = response_1['illustTitle']  # 图片标题
    img_dic['illustDescription'] = response_1['illustComment']  # 图片简介
    img_dic['createDate'] = response_1['createDate']  # 创建时间
    img_dic['uploadDate'] = response_1['uploadDate']  # 更新时间
    img_dic['tags'] = []  # 因为有多个tag，所以'tags'的值用列表形式保存
    for tag in response_1['tags']['tags']:
        img_dic['tags'].append(tag['tag'])
    img_dic['authorID'] = response_1['tags']['tags'][0]['userId']
    img_dic['authorName'] = response_1['tags']['tags'][0]['userName']

    # 获取第二个文件的信息，把图片url拿到
    url_2 = 'https://www.pixiv.net/ajax/illust/' + img_id + '/pages'

    response_2 = session.get(url_2)
    response_2 = eval(response_2.content)['body']
    img_dic['imgUrl'] = []  # 因为存在好几个插画在同一页面的情况，所以'imgUrl'的值用列表形式保存
    for img_url in response_2:
        img_dic['imgUrl'].append(img_url['urls']['original'].replace('\\', ''))

    return img_dic


# 从img_dic里提取下载所需的信息
def get_img_imformation(img_dic):
    img_imformation = {}
    img_imformation['img_url'] = img_dic['imgUrl']
    img_imformation['img_id'] = img_dic['illustID']
    img_imformation['img_title'] = img_dic['illustTitle']
    return img_imformation


# 下载图片，以图片标题命名
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
            print("下载出错，重试中\n")

        n = n + 1

if __name__ == '__main__':
    # 打开作者ID的txt文件，一个ID为一行
    file = open(r'id', encoding='utf-8')
    while True:
        # 去除换行符
        author_id = file.readline().replace('\n', '')
        # 根据作者ID得到插画ID
        author_img_dic = get_author_img_dic(author_id, 'aomiao9311z@qq.com', 'zhejiushimima')
        illusts_list = get_author_illusts(author_img_dic)
        # 根据作者ID得到下载信息
        print("画师ID%下载进度：\n"%author_id)
        for img_id in tqdm(illusts_list):
            img_dic = get_img_dic(img_id, 'aomiao9311z@qq.com', 'zhejiushimima')
            address = 'I://pixivs/' + img_dic['authorName']

            # 创建以画师为名的文件夹作为图片存放路径
            # try语句是为了去除重复创建文件夹带来的异常
            try:
                os.mkdir(address)
            except:
                img_imformation = get_img_imformation(img_dic)
                # 根据下载信息下载
                list_t = []
                for i in img_imformation:
                    t1 = Thread(target=download, args=(img_imformation, address))
                    t1.start()
                    list_t.append(t1)
                for j in list_t:
                    j.join()
            else:
                img_imformation = get_img_imformation(img_dic)# 根据下载信息下载
                for i in img_imformation:
                    t1 = Thread(target=download, args=(img_imformation, address))
                    t1.start()
                    list_t.append(t1)
                for j in list_t:
                    j.join()
        if author_id == '':
            break
    file.close()
