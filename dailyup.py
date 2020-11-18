# -*- coding: utf-8 -*-
"""
Created on 2020/11/18
@author: Moo
"""

import base64
import json
import math
import random
import re
import time
from io import BytesIO

import requests
from Crypto.Cipher import AES
from PIL import Image
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class post_data(object):  # 纯网络请求方式登录
    # 禁用安全请求警告
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    #
    __login_page_url = "http://authserver.nwu.edu.cn/authserver/login?service=https://app.nwu.edu.cn/a_nwu/api/sso" \
                       "/cas?redirect=https://app.nwu.edu.cn/site/ncov/dailyup&from=wap"
    __lasttime_reportdata_url = "https://app.nwu.edu.cn/ncov/wap/open-report/index"
    __dailyup_page_url = "https://app.nwu.edu.cn/ncov/wap/open-report/save"

    def __init__(self):
        self.__session = requests.session()

    def login(self, username, raw_password):
        response = self.__session.get(self.__login_page_url, verify=False)
        ds = BeautifulSoup(response.text, "html5lib")
        lt = ds.select('input[name="lt"]')[0].get('value')
        dllt = ds.select('input[name="dllt"]')[0].get('value')
        execution = ds.select('input[name="execution"]')[0].get('value')
        _eventId = ds.select('input[name="_eventId"]')[0].get('value')
        rm_shown = ds.select('input[name="rmShown"]')[0].get('value')
        pwd_default_encrypt_salt = self.__get_aes_salt(response.text)
        pc = self.AESCipher(pwd_default_encrypt_salt)  # 初始化密钥
        password = pc.encrypt(raw_password)  # 加密
        data = {
            "_eventId": _eventId,
            "dllt": dllt,
            "execution": execution,
            "lt": lt,
            "password": password,
            "rmShown": rm_shown,
            "username": username,
        }

        response_login = self.__session.post(self.__login_page_url, data=data, verify=False)
        cookie_dict = self.__session.cookies.get_dict()
        if response_login is not None:
            msg = self.__get_msg(response_login.text)
            if msg == 1:
                cookie_str = ''
                for i in (cookie_dict):
                    cookie_str += i + '=' + cookie_dict[i] + '; '
                return [True, '登陆成功', cookie_str]
                # title_soup = BeautifulSoup(response_login.text, 'html5lib')
                # title = title_soup.find('title')
                # if (title is None) or title.text != '统一身份认证':
                #     return [False, '登录页面错误']
                # else:
                #     # print("登录成功!")
                #     return [True, '登陆成功']
            elif msg == -1:
                # print("登录失败!")
                return [False, '账号或密码错误']
            elif msg == -2:
                # print("需要验证码!")
                return [False, '需要验证码']
        return [False, '网络错误']

    def dailyup(self):
        #        lasttime_response = self.__session.get(self.__lasttime_reportdata_url, verify=False)
        #        lasttime_data = json.loads(lasttime_response.text)
        #        sfzx = lasttime_data['d']['info']['sfzx']
        #        tw = lasttime_data['d']['info']['tw']
        #        sfcyglq = lasttime_data['d']['info']['sfcyglq']
        #        sfyzz = lasttime_data['d']['info']['sfyzz']
        #        qtqk = lasttime_data['d']['info']['qtqk']
        #
        #        city = lasttime_data['d']['setting']['city']
        data = dict(sfzx="1", tw="1", area="陕西省 西安市 碑林区", city="西安市", province="陕西省",
                    address="陕西省西安市碑林区张家村街道含光路150号西北工业大学附属中学含光校区",
                    geo_api_info='{"type":"complete","position":{"Q":34.247495659723,"R":108.93127794053902,'
                                 '"lng":108.931278,"lat":34.247496},"location_type":"html5","message":"Get ipLocation '
                                 'failed.Get geolocation success.Convert Success.Get address success.","accuracy":200,'
                                 '"isConverted":true,"status":1,"addressComponent":{"citycode":"029","adcode":"610103",'
                                 '"businessAreas":[{"name":"环城南路","id":"610103","location":{"Q":34.250901,'
                                 '"R":108.94798100000002,"lng":108.947981,"lat":34.250901}},{"name":"长安路",'
                                 '"id":"610113","location":{"Q":34.225014,"R":108.94260099999997,"lng":108.942601,'
                                 '"lat":34.225014}},{"name":"甜水井","id":"610104","location":{"Q":34.255614,'
                                 '"R":108.92899899999997,"lng":108.928999,"lat":34.255614}}],"neighborhoodType":"",'
                                 '"neighborhood":"","building":"","buildingType":"","street":"含光路",'
                                 '"streetNumber":"150号","country":"中国","province":"陕西省","city":"西安市","district":"碑林区",'
                                 '"township":"张家村街道"},"formattedAddress":"陕西省西安市碑林区张家村街道含光路150号西北工业大学附属中学含光校区",'
                                 '"roads":[],"crosses":[],"pois":[],"info":"SUCCESS"}', sfcyglq="0", sfyzz="0", qtqk="",
                    ymtys="")
        response_dailyup = self.__session.post(self.__dailyup_page_url, data=data, verify=False)
        if response_dailyup is not None:
            msg = json.loads(response_dailyup.text)
            e = msg['e']
            m = msg['m']
            if e == 0:
                # print("填报成功")
                return [True, m]
            elif e == 1:
                # print(m)
                return [False, m]
            else:
                # print(msg)
                return [False, m]
        return [False, '网络错误']

    @staticmethod
    def __get_msg(html):
        soup = BeautifulSoup(html, 'html5lib')
        span = soup.select('span[id="msg"]')
        if len(span) == 0:
            return 1
        msg = soup.select('span[id="msg"]')[0].text
        if msg == "您提供的用户名或者密码有误":
            return -1
        elif msg == "无效的验证码":
            return -2
        elif msg == "请输入验证码":
            return -2

    def __get_aes_salt(self, string):
        '''
        :param string: 登陆界面源码
        :return: 盐值
        '''
        t1 = string.split('pwdDefaultEncryptSalt = "')[1]
        t2 = t1.split('"')[0]
        return t2

    class AESCipher:
        def __init__(self, key):
            self.key = key.encode()
            self.iv = self.random_string(16).encode()

        def __pad(self, text):
            """填充方式，加密内容必须为16字节的倍数，若不足则使用self.iv进行填充"""
            text_length = len(text)
            amount_to_pad = AES.block_size - (text_length % AES.block_size)
            if amount_to_pad == 0:
                amount_to_pad = AES.block_size
            pad = chr(amount_to_pad)
            return text + pad * amount_to_pad

        def encrypt(self, text):
            """加密"""
            raw = self.random_string(64) + text
            raw = self.__pad(raw).encode()
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            return base64.b64encode(cipher.encrypt(raw))

        @staticmethod
        def random_string(length):
            aes_chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
            aes_chars_len = len(aes_chars)
            retStr = ''
            for i in range(0, length):
                retStr += aes_chars[math.floor(random.random() * aes_chars_len)]
            return retStr


class wechat(object):  # 微信扫码方式登录
    __auth_login_url = 'http://authserver.nwu.edu.cn/authserver/login?service=https%3A%2F%2Fapp.nwu.edu.cn%2Fa_nwu%2Fapi%2Fsso%2Fcas%3Fredirect%3Dhttps%253A%252F%252Fapp.nwu.edu.cn%252Fsite%252Fncov%252Fdailyup%26from%3Dwap'
    __wechat_login_url = 'http://authserver.nwu.edu.cn/authserver/combinedLogin.do?type=weixin&success=http://authserver.nwu.edu.cn/authserver/login?service=https%3A%2F%2Fapp.nwu.edu.cn%2Fa_nwu%2Fapi%2Fsso%2Fcas%3Fredirect%3Dhttps%253A%252F%252Fapp.nwu.edu.cn%252Fsite%252Fncov%252Fdailyup%26from%3Dwap'

    __head = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh-TW;q=0.9,zh;q=0.8,ja-JP;q=0.7,ja;q=0.6,en-GB;q=0.5,en;q=0.4',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Host': 'authserver.nwu.edu.cn',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36',
    }
    __get_status_head = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Host': 'lp.open.weixin.qq.com',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    }
    __get_qrcode_head = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    }

    def __init__(self):
        self.login_session = requests.session()  # 初始化session

    def get_cookie(self):
        login_auth_web_2_get_cookie = self.login_session.get(self.__auth_login_url)
        get_wechat_qrcode = self.login_session.get(self.__wechat_login_url)
        state = re.findall('state=(.+)\#', get_wechat_qrcode.url)[0]  # 用于获取一会重定向时候需要的get参数:state
        qrcode_image_url = re.findall('qrcode-image js_qr_img\" src=\"(.+)\"', get_wechat_qrcode.text)
        uuid = re.findall('qrcode\/(.+)', qrcode_image_url[0])[0]
        qrcode_url = 'https://open.weixin.qq.com' + qrcode_image_url[0]
        qrcode_image = self.login_session.get(qrcode_url, headers=self.__get_qrcode_head, timeout=5)
        image_data = qrcode_image.content
        print(image_data)
        image = Image.open(BytesIO(qrcode_image.content))
        image.show()
        print('请扫码')
        # print(qrcode_url)
        # with open(f'{uuid}.jpg', 'wb') as f:
        #     f.write(qrcode_image.content) #保存二维码文件, 如果是web使用, 将byte返回给前端, 让前端绘制图片即可
        """ 
        微信扫码登录, 是通过不停的GET请求'https://lp.open.weixin.qq.com/connect/l/qrconnect?uuid=061Mloz91c4m000U&_=1605676789626'
        来实现的, 其中uuid是二维码的编号, 后面的数字是unix毫秒时间戳
        如果没有被扫描, 返回的response.preview=window.wx_errcode=408;window.wx_code='';
        如果被扫描了, 返回的是

        """
        while True:
            unix_ms = int(time.time() * 1000)
            # 需要的时间戳为13位
            judge_qrcode_scanned_url = f'https://lp.open.weixin.qq.com/connect/l/qrconnect?uuid={uuid}&_={unix_ms}'
            # 这里需要做一个长时间的get, 浏览器里面是14秒
            # 以轮询的方式来判断用户是否已经扫码/确认
            scan_result = self.login_session.get(judge_qrcode_scanned_url, headers=self.__get_status_head, timeout=20)
            if ('404' in scan_result.text):
                print('已被扫描')
                time.sleep(5)
                # 返回码为404代表qrcode已经被扫描, 但我们仍要轮询访问, 来确定用户是否点击了确定
                # 这里不能频繁get, 不然会被微信ban掉, 返回606, 就需要刷新验证码重新来过
            if ('405' in scan_result.text):
                # 返回码405代表用户已经扫码并且点击了确认
                print('用户已确认, 即将登陆跳转')
                get_redirect_url = f'https://lp.open.weixin.qq.com/connect/l/qrconnect?uuid={uuid}&last=404&_={unix_ms}'
                head = {
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Connection': 'keep-alive',
                    'DNT': '1',
                    'Host': 'lp.open.weixin.qq.com',
                    'Referer': 'https://open.weixin.qq.com/',
                    'Sec-Fetch-Dest': 'script',
                    'Sec-Fetch-Mode': 'no-cors',
                    'Sec-Fetch-Site': 'same-site',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
                }
                get_wx_code = self.login_session.get(get_redirect_url, headers=head)
                wx_code = re.findall("wx_code=\'(.+)\'", get_wx_code.text)  # 用户的weixin_code
                if (len(wx_code) == 1):  # 如果成功获取的wx_code, 终止轮询
                    break
        callback_url = f'http://authserver.nwu.edu.cn/authserver/callback?code={wx_code[0]}&state={state}'
        callback_head = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'DNT': '1',
            'Host': 'authserver.nwu.edu.cn',
            'Proxy-Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        }
        redirect_url = self.login_session.get(callback_url, headers=callback_head)
        if (len(redirect_url.history) != 4):
            '''
            如果已经绑定了微信账号,会进行4次302跳转,history的长度为4
            未绑定不进行跳转, history的长度为0
            '''
            # 绑定地址http://authserver.nwu.edu.cn/authserver/index.do?tab=combinedLoginSetting
            print('还未绑定账号')
            return [False, '请绑定账号']
        else:
            '''
            已经获取到了需要的wx_code和state, 我们直接使用requests访问callback_url,
            requests会帮我们自动重定向, 因为我们用了session(),会自动帮我们管理cookies
            '''
            cookie_dict = self.login_session.cookies.get_dict()  # 获取cookie字典
            cookies = requests.utils.cookiejar_from_dict(cookie_dict, cookiejar=None,
                                                         overwrite=True)  # 为了一会测试cookie是否正确, 需要jar类型的cookies
            head = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive',
                'DNT': '1',
                'Host': 'app.nwu.edu.cn',
                'Referer': 'https://app.nwu.edu.cn/site/ncov/dailyup',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest',
            }
            test_cookie = self.login_session.get('https://app.nwu.edu.cn/ncov/wap/open-report/index', headers=head,
                                                 cookies=cookies)
            print(test_cookie.text)
            userinfo1 = json.loads(test_cookie.text)
            # print(userinfo1)
            stuid = userinfo1['d']['userinfo']['role']['number']  # 学工号
            print(userinfo1)
            print('学工号:' + stuid)
            return [True, cookie_dict, stuid]


if __name__ == '__main__':
    a = wechat()
