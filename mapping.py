import pandas as pd
import os, sys
from dbconfig import Insert, Upsert
from controller import MysqlController
import datetime
import numpy as np
import json
from tqdm import tqdm


with open(os.path.join(sys.path[0], './connection.txt'), "r") as f:
                connect_info = list(map(lambda x: x.strip(), f.read().split(",")))
server = MysqlController(*connect_info)

# 서울 메뉴 데이터 가져오기
server.curs.execute("SELECT DISTINCT restaurant_id FROM restaurant_info WHERE sido = '서울특별시'")
res_id = [i[0] for i in server.curs.fetchall()]

# 표준화 테이블
MN_CODE = pd.read_sql("SELECT STD_MENU_NAME, STD_MENU_CODE FROM STD_MENU;", server.conn)

for id in tqdm(res_id):
    df = pd.read_sql(f"SELECT menu_id, restaurant_id, name, name as name_2, price FROM menu_info WHERE restaurant_id = {id}", server.conn)
    # 메뉴에서 띄어쓰기 지우기
    df.name_2 = df.name_2.str.replace(" ", "")
    
    df['std_mn'] = pd.Series(np.zeros(len(df)))
    df['std_mn_code'] = pd.Series(np.zeros(len(df)))
    
    # 1차: MN_CODE에 있는거 먼저
    for mn in range(len(MN_CODE[:-1])):
        # 완전 일치
        idx_p = list(df[df.name_2 == MN_CODE.loc[mn, 'STD_MENU_NAME']].index)
        for p in idx_p:
            df.loc[p, 'std_mn'] = MN_CODE.loc[mn, 'STD_MENU_NAME']
            df.loc[p, 'std_mn_code'] = MN_CODE.loc[mn, 'STD_MENU_CODE']
            
        # # 부분 일치 처리
        # idx_c = list(df[df.name_2.str.contains(MN_CODE['표준 메뉴(MN)'][mn])].index)
        # for c in idx_c:
        #     if df.loc[c, 'std_mn'] != 0:
        #         continue
        #     else:
        #         df.loc[c, 'std_mn'] = MN_CODE.loc[mn, '표준 메뉴(MN)']
        #         df.loc[c, 'std_mn_code'] = MN_CODE.loc[mn, 'MN CODE']

    df.drop(columns = 'name_2', inplace = True)

    # 한꺼번에 올리기
    temp=[]
    df = df.values
    temp = list(map(tuple,df))
    
    q = f"""
    INSERT INTO seoul_menu (updated_at, menu_id, restaurant_id, name, price,std_mn, std_mn_code) 
    VALUES('{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', %s, %s, %s, %s, %s, %s)
    """
    try:
        server.curs.executemany(q,temp)
        server.conn.commit()
    except:
        continue # 이미 있거나 오류