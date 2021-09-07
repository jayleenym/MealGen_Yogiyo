import datetime
import math
import os, sys
import time
import numpy as np
import pandas as pd
from tqdm import tqdm
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# db management libraries
import pymysql
from dbconfig import Insert, Upsert
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
            
            Upsert(self.controller, table_name='user_info', line=dict(df.iloc[i]), 
                    update='user_name')



if __name__ == "__main__":
    user = UpdateUser(file = "../connection.txt")
    user.controller._connection_info()

    # daily update
    user.update_info()
    # user.update_recommend()

    user.controller.curs.close()