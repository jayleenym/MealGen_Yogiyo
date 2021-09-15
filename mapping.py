import pandas as pd
import os, sys
from dbconfig import Insert, Upsert
from controller import MysqlController
import datetime
import numpy as np
import json
from tqdm import tqdm


# 서울 데이터 업데이트
with open(os.path.join(sys.path[0], './connection.txt'), "r") as f:
                connect_info = list(map(lambda x: x.strip(), f.read().split(",")))
server = MysqlController(*connect_info)

server.curs.execute("SELECT DISTINCT restaurant_id FROM restaurant_info WHERE sido = '서울특별시'")
res_id = [i[0] for i in server.curs.fetchall()]
# res_id[:10]

# 표준화된 파일
# path = '/Users/yejin/Downloads/NAVERWORKS/서울지역 메뉴 필터링_최종본_ver.0.2_210819 (1).xlsx'
# STD_MN = pd.read_excel(path, sheet_name=2, header = 0)

# STD_MN.drop(columns = '담당자', inplace = True)
# STD_MN.drop(STD_MN[STD_MN['표준 메뉴(MT)'] == '삭제'].index.values, inplace = True)
# STD_MN.drop(STD_MN[STD_MN['표준 메뉴(MT)'] == '하단정렬'].index.values, inplace = True)
# STD_MN = STD_MN[['메뉴명', '표준 메뉴(MN)', 'MN CODE']]

# STD_MN.reset_index(drop = True, inplace = True)
# MN_CODE = pd.read_excel(path, sheet_name=3, header=0)
MN_CODE = pd.read_sql("SELECT STD_MENU_NAME, STD_MENU_CODE FROM STD_MENU;", server.conn)

for id in tqdm(res_id):
    df = pd.read_sql(f"SELECT menu_id, restaurant_id, name, name as name_2, price FROM menu_info WHERE restaurant_id = {id}", server.conn)
    # df = df.append(df2)
    # 메뉴에서 띄어쓰기 지우기
    df.name_2 = df.name_2.str.replace(" ", "")
    # df.tail()
    df['std_mn'] = pd.Series(np.zeros(len(df)))
    df['std_mn_code'] = pd.Series(np.zeros(len(df)))
    # df.head()

    # 1차: MN_CODE에 있는거 먼저
    for mn in range(len(MN_CODE[:-2])):
        # 완전 일치 먼저
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

    # JSON = df.to_json(orient='records', force_ascii=False)
    # JSON = json.loads(JSON)
    # # JSON

    # for j in JSON:
    #     j['updated_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     try:
    #         Insert(server, table_name = "seoul_menu", line = j) # 0 값으로 되어 있는거 빼고 업로드
    #     except:
    #         continue
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
        continue