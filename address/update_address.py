# import datetime
# import math
import os, sys
# import time
# import numpy as np
import pandas as pd
# from tqdm import tqdm
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# db management libraries
import pymysql
# from dbconfig import reduce_mem_usage
from controller import MysqlController

folder_path = '/Users/yejin/Downloads/202109_/'
txt_headers = ['시군구코드', '기초구간일련번호', '기초번호본번', '기초번호부번', '도로구간일련번호',
          '시도명', '시군구명', '읍면동코드', '읍면동명', '도로명코드', '도로명', '도로구간시점', '도로구간종점',
          '중심점좌표_X', '중심점좌표_Y']

        
class UpdateAddress():
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

    def update_address(self):
        iq = "INSERT INTO Address (updated_at, sido, sigungu, dong, X, Y) VALUES (now(), %s, %s, %s, %s, %s)"
        
        for f in os.listdir(folder_path):
            if f.endswith('.txt'):
                df = pd.read_csv(folder_path + f, sep = '|', header = None, encoding = 'ms949')
                df.columns = txt_headers
                df = df.drop_duplicates(subset = '읍면동명', ignore_index = True)
                df = df[['시도명', '시군구명', '읍면동명', '중심점좌표_X', '중심점좌표_Y']].fillna('(알수없음)')
                
                self.controller.curs.executemany(iq, list(map(tuple, df.values)))
                self.controller.conn.commit()



if __name__ == '__main__':
    server = UpdateAddress(file = "../connection.txt")
    server.controller._connection_info()

    server.update_address()