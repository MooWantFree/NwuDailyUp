import configparser
import sqlite3


def init_config():  # 创建初始化配置文件
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'Post_login': 'True',
                         'Wechat_login': 'True',
                         }
    config['Notice_id'] = {'Server_chan': 'True',
                           'Server_chan_key': '',
                           'Telegram_bot': 'True',
                           'Telegram_bot_key': '',
                           'Your_telegram_chat_id': '',
                           }
    # 储存密码使用rsa对称加密, rsa_key为密钥
    config['sql'] = {'address': '.',
                     'rsa_key': '',

                     }
    with open('example.ini', 'w') as configfile:
        config.write(configfile)
    return True


def init_sql():  # 创建初始化数据库
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE userinfo
    (Stuid TEXT PRIMARY KEY     NOT NULL, 
    password           TEXT    NOT NULL,
    cookies            TEXT     NOT NULL,
    location        TEXT,
    Status        text);''')
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_config()
    init_sql()
