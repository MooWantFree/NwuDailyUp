import configparser
import json
import logging
import sqlite3
import time

import requests

config = configparser.ConfigParser()
config.sections()
config.read('example.ini')
sql_address = config['sql']['address']


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
    a = requests.post('https://app.nwu.edu.cn/ncov/wap/open-report/save', data=data[location], headers=head, timeout=5)
    # print(stuid+a.text)
    return a.text


def get_userinfo():
    conn = sqlite3.connect(sql_address)
    start_time = time.time()
    userinfo = list(conn.execute(''' select stuid,cookie,ns,yn from userinfo'''))
    userinfo_0 = list(conn.execute(''' select stuid from userinfo where yn=0'''))
    userinfo_1 = list(conn.execute(''' select stuid,cookie,ns from userinfo where yn=1'''))
    userinfo_3 = list(conn.execute(''' select stuid from userinfo where yn=3'''))

    db_people_count = len(userinfo)  # 总人数
    db_1_people = len(userinfo_1)  # 填报人数
    db_0_people = len(userinfo_0)  # 取消填报人数
    db_3_people = len(userinfo_3)  # 取消填报人数
    conn.close()

    location_dict = {'n': 'taibai', 's': 'changan'}
    LOG_FORMAT = "%(asctime)s  - %(message)s"
    DATE_FORMAT = "%Y/%m/%d %H:%M:%S %p"
    data_time = time.strftime("%Y%m%d%H%M", time.localtime())
    logging.basicConfig(filename=f'./logdata/{data_time}.log', level=logging.INFO, format=LOG_FORMAT,
                        datefmt=DATE_FORMAT)
    logging.getLogger("requests").setLevel(logging.WARNING)

    url = f"https://api.telegram.org/bot{config['Notice_id']['telegram_bot_key']}/sendMessage"
    data_time1 = time.strftime("%Y年%m月%d日%H时%M分%S秒", time.localtime())
    context = f'{data_time1}开始填报....'
    data = {'chat_id': config["Notice_id"]["your_telegram_chat_id"], 'text': str(context)}
    tg_send_start_message = requests.post(url, data=data, timeout=5)
    start_message_json = json.loads(tg_send_start_message.text)
    start_message_id = start_message_json["result"]["message_id"]

    report_all_conut = 0
    success_stuid = []
    report_count = 0
    error_stuid = []
    while (len(userinfo_1) != len(success_stuid)):
        for i in range(len(userinfo_1)):
            try:
                if (userinfo_1[i][0] not in success_stuid):
                    post_result = location_post(userinfo_1[i][0], userinfo_1[i][1], location_dict[userinfo_1[i][2]])
                    logging.info(userinfo_1[i][0] + post_result)
                    report_count = report_count + 1
                    success_stuid.append(userinfo_1[i][0])
                else:
                    pass

            except Exception as e:
                # print(userinfo_1[i][0])
                logging.info(userinfo_1[i][0] + ' Error Description: ' + str(e))
        report_all_conut += 1
        if (report_all_conut > 2):
            for i in range(len(userinfo_1)):
                error_stuid.append(userinfo_1[i][0])
            break

    data_time2 = time.strftime("%Y年%m月%d日%H时%M分%S秒", time.localtime())
    end_time = time.time()
    context = f'{data_time2}填报完毕\n' \
              f'本次运行时间{end_time - start_time}秒\n' \
              f'上报成功人数{report_count}\n' \
              f'上报失败人数{len(error_stuid)}\n' \
              f'数据库总人数{db_people_count}\n' \
              f'开启填报人数{db_1_people}\n' \
              f'关闭填报人数{db_0_people}\n' \
              f'还未激活人数{db_3_people}\n' \
              f'失败学号列表: \n' \
              f'{error_stuid}'

    data = {'chat_id': config["Notice_id"]["your_telegram_chat_id"],
            'text': str(context),
            'reply_to_message_id': start_message_id,
            }
    tg_notice = requests.post(url, data=data, timeout=5)
    print(tg_notice.text)
    return True


if __name__ == '__main__':
    get_userinfo()
