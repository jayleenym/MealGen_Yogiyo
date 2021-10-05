import pandas as pd
import os, sys
# from dbconfig import Insert, Upsert
from controller import MysqlController
import datetime
import numpy as np
import json
from tqdm import tqdm


with open(os.path.join(sys.path[0], './connection.txt'), "r") as f:
                connect_info = list(map(lambda x: x.strip(), f.read().split(",")))
server = MysqlController(*connect_info)

# 서울 메뉴 데이터 가져오기
server.curs.execute("SELECT DISTINCT restaurant_id FROM restaurant_info WHERE sido = '서울특별시';")
res_id = [i[0] for i in server.curs.fetchall()]

# 표준화 테이블
path = '/Users/yejin/Downloads/NAVERWORKS/seoul_menu_ver.0.2_210819.xlsx'
STD_MN = pd.read_excel(path, sheet_name = 2, header = 0)

STD_MN.drop(columns = '담당자', inplace = True)
STD_MN.drop(STD_MN[STD_MN['표준 메뉴(MN)'] == '삭제'].index.values, inplace = True)
STD_MN.drop(STD_MN[STD_MN['표준 메뉴(MN)'] == '하단정렬'].index.values, inplace = True)
STD_MN = STD_MN[['메뉴명', '표준 메뉴(MN)', 'MN CODE']]

STD_MN.reset_index(drop = True, inplace = True)

for id in tqdm(res_id):
    df = pd.read_sql(f"SELECT menu_id, restaurant_id, name as 메뉴명, price FROM menu_info WHERE restaurant_id = {id}", server.conn)
    # STD_MN 원천 메뉴 완전 일치
    df = df.merge(STD_MN, how = 'inner', on = '메뉴명').rename(columns = {'표준 메뉴(MN)': 'std_mn', 'MN CODE': 'std_mn_code', '메뉴명': 'name'})
    if len(df) != 0:
        # 업데이트 불가, 새로 올리기
        temp = list(map(tuple, df.values))
        insert_q = f"""
        INSERT INTO seoul_menu (updated_at, menu_id, restaurant_id, name, price, std_mn, std_mn_code) 
        VALUES('{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', %s, %s, %s, %s, %s, %s)
        """
        server.curs.executemany(insert_q, temp)
        server.conn.commit()
    else: continue
# server.curs.execute('DELETE FROM seoul_menu WHERE std_mn = 0;')
# server.conn.commit()

server.conn.close()