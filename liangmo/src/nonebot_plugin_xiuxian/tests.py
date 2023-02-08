
from pathlib import Path
import json
import yaml
import sqlite3

# DATABASE = Path() / "data" / "xiuxian"
DATABASE = Path() / "xiuxian"

class XiuConfig:

    def __init__(self):
        self.config_jsonpath = DATABASE / "config.json"


    def read_data(self):
        """配置数据"""
        with open(self.config_jsonpath, 'r', encoding='utf-8') as e:
            data = json.load(e)
            print(data)
            return data

    def write_data(self, user_id):
        json_data = self.read_data()
        json_data[user_id] = True
        with open(self.config_jsonpath, 'w+') as f:
            json.dump(json_data, f)


def get_sql():
    database_path = r"D:\yuzi_bot\yuzi_bot\data\xiuxian\xiuxian.db"
    conn = sqlite3.connect(database_path)
    check_sql = f"select goods_num from user_back where user_id=? and goods_id=?"
    cur = conn.cursor()
    cur.execute(check_sql, ('111', '1'))
    result = cur.fetchone()
    if result:
        goods_nums = result[0]
        sql = f"UPDATE user_back set num=?,update_time=? WHERE user_id=? and goods_id=?"
        cur.execute(sql, (user_id, goods_id, name, type_n, num, remake))
        conn.commit()
    else:
        sql = """
                INSERT INTO user_back ( user_id, goods_id, goods_name, goods_type, goods_num, create_time, update_time )
        VALUES (?,?,?,?,?,?,?)"""
        cur.execute(sql, (user_id, goods_id, name, type_n, num, remake))
        conn.commit()

    # sql = f"INSERT INTO back(user_id, goods_id, goods_name, goods_type, goods_num, create_time, update_time) VALUES (?,?,?,?,?,?)"
    # cur = self.conn.cursor()
    # cur.execute(sql, (user_id, goods_id, name, type_n, num, remake))
    # self.conn.commit()



if __name__ == '__main__':
    # XiuConfig().write_data("抢灵石")
    # DATA = XiuConfig().read_data()
    import asyncio
    import time
    a = input("Enter：")
    while a == 1:
        time.sleep(2)
        print('暂停完毕')
        a = input("Enter：")