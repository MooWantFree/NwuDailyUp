import configparser
import json
import sqlite3

import requests
from flask import Flask, request
from flask_cors import CORS

import dailyup

config = configparser.ConfigParser()
config.sections()
config.read('example.ini')
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'whosyourdaddy'
sql_address = config['sql']['address']


def sql_add(stuid, pwd, cookie, ns, yn):
    conn = sqlite3.connect(sql_address)
    conn.execute(''' INSERT INTO userinfo VALUES ( '%s' , '%s' ,'%s' ,'%s',%s) ''' % (stuid, pwd, cookie, ns, yn))
    conn.commit()
    conn.close()


def sql_change(stuid, ns, yn):
    conn = sqlite3.connect(sql_address)
    if (yn != 3):
        conn.execute('''UPDATE userinfo SET ns='%s', yn=%s  where stuid='%s' ''' % (ns, yn, stuid))
    elif (yn == 3):
        conn.execute('''UPDATE userinfo SET ns='%s' where stuid='%s' ''' % (ns, stuid))
    conn.commit()
    conn.close()
    return [True, 'user status has been changed']


def sql_search(stuid, pwd):
    conn = sqlite3.connect(sql_address)
    user_info = conn.execute('''select stuid,ns,yn from userinfo where stuid='%s' and pwd='%s' ''' % (stuid, pwd))

    try:
        user_info = user_info.__next__()
        print(user_info)
    except:
        print('用户名与密码不匹配')
        return [False, 'User\'s password is not right']
    return [True, user_info]


def location_post(stuid, cookie, location):
    head = {'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection': 'keep-alive',
            'Content-Length': '2497',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': f'{cookie}',
            'Host': 'app.nwu.edu.cn',
            'Origin': 'https://app.nwu.edu.cn',
            'Referer': 'https://app.nwu.edu.cn/ncov/wap/default/index',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
            'X-Requested-With': 'XMLHttpRequest', }
    data = {
        'changan': 'sfzx=1&tw=1&area=%E9%99%95%E8%A5%BF%E7%9C%81%20%E8%A5%BF%E5%AE%89%E5%B8%82%20%E9%95%BF%E5%AE%89%E5%8C%BA&city=%E8%A5%BF%E5%AE%89%E5%B8%82&province=%E9%99%95%E8%A5%BF%E7%9C%81&address=%E9%99%95%E8%A5%BF%E7%9C%81%E8%A5%BF%E5%AE%89%E5%B8%82%E9%95%BF%E5%AE%89%E5%8C%BA%E9%83%AD%E6%9D%9C%E8%A1%97%E9%81%93%E5%87%A4%E6%9E%97%E5%A4%A7%E9%81%93%E8%A5%BF%E5%8C%97%E5%A4%A7%E5%AD%A6%E9%95%BF%E5%AE%89%E6%A0%A1%E5%8C%BA&geo_api_info=%7B%22type%22%3A%22complete%22%2C%22info%22%3A%22SUCCESS%22%2C%22status%22%3A1%2C%22VDa%22%3A%22jsonp_546141_%22%2C%22position%22%3A%7B%22Q%22%3A34.14215%2C%22R%22%3A108.87224000000003%2C%22lng%22%3A108.87224%2C%22lat%22%3A34.14215%7D%2C%22message%22%3A%22Get%20ipLocation%20success.Get%20address%20success.%22%2C%22location_type%22%3A%22ip%22%2C%22accuracy%22%3Anull%2C%22isConverted%22%3Atrue%2C%22addressComponent%22%3A%7B%22citycode%22%3A%22029%22%2C%22adcode%22%3A%22610116%22%2C%22businessAreas%22%3A%5B%5D%2C%22neighborhoodType%22%3A%22%22%2C%22neighborhood%22%3A%22%22%2C%22building%22%3A%22%22%2C%22buildingType%22%3A%22%22%2C%22street%22%3A%22%E5%87%A4%E6%9E%97%E5%A4%A7%E9%81%93%22%2C%22streetNumber%22%3A%221%E5%8F%B7%22%2C%22country%22%3A%22%E4%B8%AD%E5%9B%BD%22%2C%22province%22%3A%22%E9%99%95%E8%A5%BF%E7%9C%81%22%2C%22city%22%3A%22%E8%A5%BF%E5%AE%89%E5%B8%82%22%2C%22district%22%3A%22%E9%95%BF%E5%AE%89%E5%8C%BA%22%2C%22township%22%3A%22%E9%83%AD%E6%9D%9C%E8%A1%97%E9%81%93%22%7D%2C%22formattedAddress%22%3A%22%E9%99%95%E8%A5%BF%E7%9C%81%E8%A5%BF%E5%AE%89%E5%B8%82%E9%95%BF%E5%AE%89%E5%8C%BA%E9%83%AD%E6%9D%9C%E8%A1%97%E9%81%93%E5%87%A4%E6%9E%97%E5%A4%A7%E9%81%93%E8%A5%BF%E5%8C%97%E5%A4%A7%E5%AD%A6%E9%95%BF%E5%AE%89%E6%A0%A1%E5%8C%BA%22%2C%22roads%22%3A%5B%5D%2C%22crosses%22%3A%5B%5D%2C%22pois%22%3A%5B%5D%7D&sfcyglq=0&sfyzz=0&qtqk=&ymtys=',
        'taibai': 'sfzx=1&tw=1&area=%E9%99%95%E8%A5%BF%E7%9C%81%20%E8%A5%BF%E5%AE%89%E5%B8%82%20%E7%A2%91%E6%9E%97%E5%8C%BA&city=%E8%A5%BF%E5%AE%89%E5%B8%82&province=%E9%99%95%E8%A5%BF%E7%9C%81&address=%E9%99%95%E8%A5%BF%E7%9C%81%E8%A5%BF%E5%AE%89%E5%B8%82%E7%A2%91%E6%9E%97%E5%8C%BA%E5%A4%AA%E7%99%BD%E5%8C%97%E8%B7%AF229%E5%8F%B7%E8%A5%BF%E5%8C%97%E5%A4%A7%E5%AD%A6%E5%A4%AA%E7%99%BD%E6%A0%A1%E5%8C%BA&geo_api_info=%7B%22type%22:%22complete%22,%22info%22:%22SUCCESS%22,%22status%22:1,%22VDa%22:%22jsonp_546141_%22,%22position%22:%7B%22Q%22:34.14215,%22R%22:108.87224000000003,%22lng%22:108.87224,%22lat%22:34.14215%7D,%22message%22:%22Get%20ipLocation%20success.Get%20address%20success.%22,%22location_type%22:%22ip%22,%22accuracy%22:null,%22isConverted%22:true,%22addressComponent%22:%7B%22citycode%22:%22029%22,%22adcode%22:%22610116%22,%22businessAreas%22:%5B%5D,%22neighborhoodType%22:%22%22,%22neighborhood%22:%22%22,%22building%22:%22%22,%22buildingType%22:%22%22,%22street%22:%22%E5%A4%AA%E7%99%BD%E5%8C%97%E8%B7%AF%22,%22streetNumber%22:%22229%E5%8F%B7%22,%22country%22:%22%E4%B8%AD%E5%9B%BD%22,%22province%22:%22%E9%99%95%E8%A5%BF%E7%9C%81%22,%22city%22:%22%E8%A5%BF%E5%AE%89%E5%B8%82%22,%22district%22:%E7%A2%91%E6%9E%97%E5%8C%BA%22,%22township%22:%22%E8%BE%B9%E5%AE%B6%E6%9D%91%22%7D,%22formattedAddress%22:%22%E9%99%95%E8%A5%BF%E7%9C%81%E8%A5%BF%E5%AE%89%E5%B8%82%E7%A2%91%E6%9E%97%E5%8C%BA%E5%A4%AA%E7%99%BD%E5%8C%97%E8%B7%AF229%E5%8F%B7%E8%A5%BF%E5%8C%97%E5%A4%A7%E5%AD%A6%E5%A4%AA%E7%99%BD%E6%A0%A1%E5%8C%BA%22,%22roads%22:%5B%5D,%22crosses%22:%5B%5D,%22pois%22:%5B%5D%7D&sfcyglq=0&sfyzz=0&qtqk=&ymtys=',
    }
    a = requests.post('https://app.nwu.edu.cn/ncov/wap/open-report/save', data=data[location], headers=head,
                      timeout=5)
    print(stuid + a.text)
    return a.json()['e']


def add_user(stuid, pwd, ns, yn):
    nwu = dailyup.NWU()
    login_info = nwu.login(stuid, pwd)  # 登陆成功返回True,失败返回False
    if (login_info[0] == True):
        cookie = login_info[2]
        location_dict = {'n': 'taibai', 's': 'changan'}
        post_result = location_post(stuid, cookie, location_dict[ns])
        if (post_result == 10013):
            return [False, 'two_step']
        else:
            sql_add(stuid, pwd, cookie, ns, yn)
            url = f"https://api.telegram.org/bot{config['Notice_id']['telegram_bot_key']}/sendMessage"
            data = {'chat_id': config["Notice_id"]["your_telegram_chat_id"], 'text': str(stuid)}
            requests.post(url, data=data)
            return [True, 'user has been added']
    elif (login_info[0] == False):
        return [False, login_info[1]]


@app.route('/loginweb', methods=['post'])
def login():
    a = request.get_data()
    a = json.loads(a)
    stuid, pwd, ns, yn = a['stuid'], a['pwd'], a['ns'], a['yn']
    ns_dict2 = {'n': '太白校区(北校区)', 's': '长安校区(南校区)'}
    yn_dict2 = {1: '开启', 0: '关闭', 3: '未激活'}
    userinfo = sql_search(stuid, pwd)
    if (userinfo[0] != True):  # 用户不存在
        add_result = add_user(stuid, pwd, ns, yn)
        print(add_result[1])
        if (add_result[0] == True):
            stuid, ns, yn = sql_search(stuid, pwd)[1]
            return {'status': True,
                    'result': f'学号:{stuid}\n自动填报定位:{ns_dict2[ns]}\n填报状态:{yn_dict2[yn]}'}
        else:
            return {'status': False,
                    'result': add_result[1], }
    elif (userinfo[0] == True):  # 用户存在
        # session['username'] = stuid
        # session['pwd'] = pwd
        sql_change(stuid, ns, yn)
        stuid, ns, yn = sql_search(stuid, pwd)[1]
        return {'status': True,
                'result': f'学号:{stuid}\n自动填报定位:{ns_dict2[ns]}\n填报状态:{yn_dict2[yn]}'}
        # return redirect('/manage')
    elif (userinfo[0] == False):
        return {'status': False,
                'result': 'pwderror'}


if __name__ == '__main__':
    app.run(debug=False, port=12315)
