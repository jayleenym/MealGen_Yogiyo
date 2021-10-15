import datetime
import math
import os, sys
import time
# from unicodedata import name
import numpy as np
import pandas as pd
from tqdm import tqdm
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# db management libraries
import pymysql
# from dbconfig import Upsert, Insert
from controller import MysqlController


class UpdateUser():
    def __init__(self, file = None):
        if not file:
            _id = input("input id(root) : ")
            _pw = input("input pw       : ")
            _db = input("databases      : ")
            connect_info = ("localhost", 3306, _id, _pw, _db)
        else:
            with open(os.path.join(sys.path[0], file), "r") as f:
                connect_info = list(map(lambda x: x.strip(), f.read().split(",")))
        self.controller = MysqlController(*connect_info)
    
    
    def update_info(self):
        q = """
        SELECT DISTINCT(CONCAT(res.sigungu, "", rev.nickname)) as user_name,
                res.sido, res.sigungu
        FROM reviews as rev JOIN restaurant_info as res 
        ON rev.restaurant_id = res.restaurant_id;
        """
        df = pd.read_sql(q, self.controller.conn)
        for i in tqdm(range(len(df))):
            if df.iloc[i].sido == '세종특별자치시':
                df.iloc[i].user_name = '세종'+ df.iloc[i].user_name.strip()
            
            # try:
                # self.controller.insert(self.controller, table_name='user_info', line=dict(df.iloc[i]))
            # except: continue
            

    def update_review(self):
        self.controller.curs.execute("SELECT count(*) FROM reviews;")
        ct = self.controller.curs.fetchone()[0]
        for i in range(0, ct, 10000):
            q = f"""
            SELECT DISTINCT(CONCAT(res.sigungu, "", rev.nickname)) as user_name, 
                   res.sido, res.sigungu, rev.review_id
            FROM reviews as rev 
            JOIN restaurant_info as res
            ON rev.restaurant_id = res.restaurant_id
            LIMIT {i}, {i+10000};"""
        df = pd.read_sql(q, self.controller.conn)

        for i in tqdm(range(len(df))):
            if df.iloc[i].sido == '세종특별자치시':
                df.iloc[i].user_name = '세종'+ df.iloc[i].user_name.strip()
            
            name = df.iloc[i].user_name
            id = df.iloc[i].review_id
            q = f"""
            UPDATE reviews
            SET user_name = '{name}', updated_at = '{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            WHERE review_id = {id};
            """
            self.controller.curs.execute(q)
            self.controller.conn.commit()

    def review_username(self):
        # reviews에 user_name 업데이트하기 (누락 업데이트용)
        reviews = pd.read_sql("SELECT review_id, nickname, restaurant_id FROM reviews;", self.controller.conn)
        restaurant = pd.read_sql("SELECT restaurant_id, sido, sigungu FROM restaurant_info", self.controller.conn)
        user = pd.read_sql('SELECT user_name, user_id FROM user_info', self.controller.conn)

        df = reviews.merge(restaurant, on = 'restaurant_id')
        df['user_name'] = df.sido.apply(lambda x: x[:2]) + df.sigungu + df.nickname
        df = df.merge(user, on = 'user_name')

        tp = list(map(tuple, df[['user_name', 'user_id', 'review_id']].values))

        for t in tqdm(tp):
            self.controller.curs.execute(f'''UPDATE reviews SET user_name ='{t[0]}', user_id = {t[1]} WHERE review_id = {t[2]};''')
            self.controller.conn.commit()

        self.controller.conn.close()

    def review_userid(self):
        # reviews에 userid 업데이트하기 (누락 업데이트용)
        q = """SELECT rev.nickname, res.sido, res.sigungu, rev.review_id
            FROM reviews as rev
            JOIN restaurant_info as res
            ON rev.restaurant_id = res.restaurant_id;"""
        df = pd.read_sql(q, self.controller.conn)

        rev = pd.read_sql("SELECT user_name, user_id FROM user_info;", self.controller.conn)

        df['user_name'] = df.sido.apply(lambda x: x[:2]) + df.sigungu + df.nickname
        ds = df.merge(rev, on = 'user_name')

        tmp = list(map(tuple, ds[['user_name', 'user_id', 'review_id']].values))
        print('start Updating...')
        for t in tmp:
            update_q = f"""UPDATE reviews
                    SET user_name = '{t[0]}', user_id = {t[1]},
                    updated_at = '{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                    WHERE user_name = {t[2]};"""
            self.controller.curs.execute(update_q)
            self.controller.conn.commit()

        print('finished')
        self.controller.conn.close()


if __name__ == "__main__":
    user = UpdateUser(file = "../connection.txt")
    user.controller._connection_info()

    # daily update
    user.update_info()
    # user.update_recommend()

    user.controller.curs.close()