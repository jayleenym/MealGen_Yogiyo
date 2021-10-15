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
            # Upsert(server, table_name='reviews', line=dict(df.iloc[i]), update='user_name')

if __name__ == "__main__":
    user = UpdateUser(file = "../connection.txt")
    user.controller._connection_info()

    # daily update
    user.update_info()
    # user.update_recommend()

    user.controller.curs.close()