from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
from threading import Thread
from urllib.parse import urlencode
import time
import os

# 自带梯子，否则无法响应,R18目前无法实现。。技术问题

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


# 最终返回一个参数列表，方便接下来加载的时候调用
def set_leaderboard(content, mode, r18, date): 
    
    print("已设置起始榜单为" + date[:4] + "年" + date[4:6] + "月" + date[6:8] + "日" + content + "区" + mode + "榜")

    if content == '综合':
        content = ''
    elif content == '插画':
        content = 'illust'
    elif content == '动图':
        content = 'ugoira'
    elif content == "漫画":
        content = 'manga'

    if mode == '今日':
        mode = 'daily'
    elif mode == '本周':
        mode = 'weekly'
    elif mode == '本月':
        mode = 'monthly'
    elif mode == '新人':
        mode = 'rookie'
    elif mode == '受男性欢迎':
        mode = 'male'
    elif mode == '受女性欢迎':
        mode = 'female'

    if r18:
        mode = mode + '_r18'
    else:
        mode = mode + ''

    return [content, mode, date]


# 使用前确保set_leaderboard()函数已调用，并将其返回的参数列表传入该函数
# 进入榜单，返回一个带有图片url等信息的字典
def load_leaderboard(username, password, set_leaderboard):
    response_list = []

    # 先登录用户
    session = login(username, password)

    # 初始化爬取的页数以及所需传入的参数
    p = 1
    data = {
        'mode': set_leaderboard[1],  # 这些是 set_leaderboard()函数返回的参数
        'content': set_leaderboard[0],
        'date': set_leaderboard[2],
        'p': p,
        'format': 'json'
    }
    print(data['mode'])
    print("正在加载" + "https://www.pixiv.net/ranking.php?" + urlencode(data))

    # 如果date是今天，需要去除date项;如果content为综合，需要去除content项。
    # 这是因为P站排行榜的今日榜不需要传入'date'，而综合区不需要传入'content'
    if set_leaderboard[2] == time.strftime("%Y%m%d"):
        data.pop('date')
    if set_leaderboard[0] == '':
        data.pop('content')

    # 开启循环进行翻页
    while True:

        # 翻页并更新data中的'p'参数
        data['p'] = p
        p = p + 1

        # 使用urlencode()函数将data传入url，获取目标文件
        url = "https://www.pixiv.net/ranking.php?" + urlencode(data)
        response = session.get(url)

        # 处理的到的文件并转为字典形式
        # 不加以下这些会报错，似乎是因为eval()不能处理布尔型数据
        global false, null, true
        false = 'False'
        null = 'None'
        true = 'True'
        try:
            response = eval(response.content)['contents']
        except KeyError:
            break
        response_list = response_list + response
    # 返回一个列表，列表元素为字典形式，包括了图片的各个信息
    return response_list


# 从response_list中得到作者图片的ID
def get_author_pic(response_list):
    pic_list = []
    for element in response_list:
        pic_list.append(str(element['illust_id']))
    return pic_list


# 传入图片ID，返回该图片ID下的信息，具体信息见注释
def get_img_dic(pic_list, username, password):
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
    url_1 = 'https://www.pixiv.net/ajax/illust/' + pic_list
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
    # img_dic['authorID'] = response_1['tags']['tags'][0]['userId']
    # img_dic['authorName'] = response_1['tags']['tags'][0]['userName']

    # 获取第二个文件的信息，把图片url拿到
    url_2 = 'https://www.pixiv.net/ajax/illust/' + pic_list + '/pages'

    response_2 = session.get(url_2)
    response_2 = eval(response_2.content)['body']
    img_dic['imgUrl'] = []  # 因为存在好几个插画在同一页面的情况，所以'imgUrl'的值用列表形式保存
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
            print("下载出错，重试中\n")

        n = n + 1


def begin(content, mode, R18, date):
    set = set_leaderboard(content, mode, R18, date)  # 设置起始页插画区、今日榜、是否R18
    response_list = load_leaderboard('username', 'password', set)
    illusts_list = get_author_pic(response_list)
    while True:
        # 根据作者ID得到下载信息
        print("下载进度：")
        for img_id in tqdm(illusts_list):
            img_dic = get_img_dic(img_id, 'username', 'password')
            address = 'I://pixivranks/' + set[0] + set[1] + set[2]

            # 创建以画师为名的文件夹作为图片存放路径
            # try语句是为了去除重复创建文件夹带来的异常
            try:
                if not os.path.exists(address):
                    os.mkdir(address)
            except:
                img_imformation = get_img_imformation(img_dic)
                # 根据下载信息下载     
                t1 = Thread(target=download, args=(img_imformation, address))
                t1.start()
            else:
                img_imformation = get_img_imformation(img_dic)  # 根据下载信息下载
                t1 = Thread(target=download, args=(img_imformation, address))
                t1.start()


if __name__ == '__main__':
    # 1:综合 插画 动图 漫画
    # 2:今日 本周 本月 新人 受男性欢迎 受女性欢迎
    # 3:True False (r18 or not)
    # 4:yyyymmdd
    # 设置起始页插画区、今日榜、是否R18
    begin("插画", '本月', False, "20190901")
