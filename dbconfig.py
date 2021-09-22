######################################################
# table definition
# - restaurant_info : 식당정보 저장(id : restaurant_id)
# - menu_info : 메뉴 저장(id : menu_id)
# - reviews : 리뷰 데이터 저장(id : _id)
######################################################

import pymysql
from controller import MysqlController
import os
import sys
import numpy as np
import datetime

global restaurant_info
global menu_info
global reviews

restaurant_info = """
CREATE TABLE restaurant_info
(
    _id INT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT "ID",
    restaurant_id INT NOT NULL UNIQUE COMMENT '식당 고유 번호(yogiyo)',
    company_id VARCHAR(32) COMMENT '사업자번호',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성 일시',
    updated_at DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '업데이트 일시',
    name VARCHAR(32) COMMENT '식당명',
    categories  VARCHAR(50) COMMENT '카테고리 set',
    phone VARCHAR(50) COMMENT '전화번호',
    address VARCHAR(255) COMMENT '주소',
    sido VARCHAR(50) COMMENT '시도 구분',
    sigungu VARCHAR(50) COMMENT '시군구 구분',
    franchise_yn TINYINT COMMENT '프랜차이즈 여부',
    franchise_id INT COMMENT '프랜차이즈 ID',
    franchise_name VARCHAR(50) COMMENT '프랜차이즈 이름',
    delivery_yn TINYINT COMMENT '배달가능 여부',
    delivery_time VARCHAR(32) COMMENT '배달시간',
    delivery_fee INT COMMENT '배달료',
    lat DECIMAL(16, 14) COMMENT '위도',
    lng DECIMAL(17, 14) COMMENT '경도',
    avg DOUBLE(10, 2) COMMENT '평균평점',
    review_count INT COMMENT '리뷰수'
)
COMMENT '식당 정보(yogiyo)';
"""

menu_info = """
CREATE TABLE menu_info
(
    _id INT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
    menu_id INT NOT NULL UNIQUE COMMENT '메뉴 고유 번호(yogiyo)',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
    updated_at DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '업데이트 일시',
    restaurant_id INT NOT NULL COMMENT '식당 id(foreign key)',
    FOREIGN KEY (restaurant_id) 
    REFERENCES restaurant_info(restaurant_id) ON UPDATE CASCADE,
    name VARCHAR(255) COMMENT '메뉴 이름',
    description TEXT COMMENT '설명',
    price INT COMMENT '가격'
)
COMMENT '메뉴 정보(yogiyo)';
"""

reviews = """
CREATE TABLE reviews
(
    review_id INT NOT NULL PRIMARY KEY COMMENT '리뷰 고유 번호(PK)',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
    updated_at DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '업데이트 일시',
    written_time DATETIME NOT NULL COMMENT '작성일시',
    nickname VARCHAR(50) COMMENT '유저닉네임',
    restaurant_id INT NOT NULL COMMENT '식당 id(FK)',
    FOREIGN KEY (restaurant_id) 
    REFERENCES restaurant_info(restaurant_id) ON UPDATE CASCADE,
    menu VARCHAR(255) COMMENT '주문 메뉴 요약',
    review VARCHAR(255) COMMENT '리뷰 내용',
    quantity INT NOT NULL COMMENT '양 평점',
    taste INT NOT NULL COMMENT '맛 평점',
    delivery INT NOT NULL COMMENT '배달 평점',
    rating INT NOT NULL COMMENT '평점',
    like_dislike TINYINT(1) COMMENT 'LIKE(5)/DISLIKE(1)'
)
COMMENT '리뷰 데이터(yogiyo)';
"""

user_predict = """
CREATE TABLE user_predict
(
    _id INT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
    updated_at DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '업데이트 일시',
    user_id INT NOT NULL COMMENT '유저 아이디',
    menu_id INT NOT NULL COMMENT '메뉴 고유 번호(yogiyo)(FK)',
    FOREIGN KEY (menu_id)
    REFERENCES menu_info(menu_id) ON UPDATE CASCADE,
    menu VARCHAR(255) COMMENT '메뉴 이름(FK)',
    restaurant_id INT NOT NULL COMMENT '식당 id(FK)',
    FOREIGN KEY (restaurant_id)
    REFERENCES restaurant_info(restaurant_id) ON UPDATE CASCADE,
    restaurant VARCHAR(32) COMMENT '식당명',
    predict FLOAT(7, 6) COMMENT 'LIKE(1)/DISLIKE(0) 예상 점수'
)
COMMENT '사용자 예상점수'
"""

user_comp = """
CREATE TABLE user_comp(
    _id INT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
    updated_at DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '업데이트 일시',
    user_id INT NOT NULL COMMENT '유저 id',
    target_user_id INT NOT NULL COMMENT '유사도 타켓 유저 번호',
    expect_rate INT NOT NULL COMMENT '궁합점수 0% ~ 100%'
)
COMMENT '사용자간 유사도 점수'
"""

user_info = """
CREATE TABLE user_info(
    user_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT '유저id',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
    updated_at DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '업데이트 일시', 
    user_name VARCHAR(50) COMMENT '유저 이름',
    sido VARCHAR(50) COMMENT '시도 구분',
    sigungu VARCHAR(50) COMMENT '시군구 구분'
)
COMMENT '사용자 정보'    
"""

# 서울 메뉴들
seoul_menu = """
CREATE TABLE seoul_menu(
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
    updated_at DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '업데이트 일시',
    menu_id INT NOT NULL PRIMARY KEY COMMENT '메뉴id',
    restaurant_id INT NOT NULL COMMENT '식당 id(FK)',
    FOREIGN KEY (restaurant_id)
    REFERENCES restaurant_info(restaurant_id) ON UPDATE CASCADE,
    name VARCHAR(255) NOT NULL COMMENT '메뉴이름',
    price INT COMMENT '가격',
    std_mn VARCHAR(255) COMMENT '표준메뉴MT(FK)',
    std_mn_code VARCHAR(50) COMMENT '표준메뉴코드MNCODE(FK)'
)
COMMENT '서울 메뉴 표준화'
"""


def table_creation(controller, tformat):
    try:
        controller.curs.execute(tformat)
        controller.conn.commit()
        print(f"TABLE CREATED.")
    except Exception as e:
        print(e)




def reduce_mem_usage(props):
    start_mem_usg = props.memory_usage().sum() / 1024**2 
    print(f"Before Reduce : {start_mem_usg:.3f} MB")
    # null이 없는 column 사용
    # NAlist = []
    for col in props.columns:
        if props[col].dtype != object:  # Exclude strings
            
            # Print current column type
            # print("******************************")
            # print("Column: ",col)
            # print("dtype before: ",props[col].dtype)
            
            # make variables for Int, max and min
            IsInt = False
            mx = props[col].max()
            mn = props[col].min()
            
            # Integer does not support NA, therefore, NA needs to be filled
            if not np.isfinite(props[col]).all(): 
                # NAlist.append(col)
                props[col].fillna(mn-1,inplace=True)  
                   
            # test if column can be converted to an integer
            asint = props[col].fillna(0).astype(np.int64)
            result = (props[col] - asint)
            result = result.sum()
            if result > -0.01 and result < 0.01:
                IsInt = True

            
            # Make Integer/unsigned Integer datatypes
            if IsInt:
                if mn >= 0:
                    if mx < 255:
                        props[col] = props[col].astype(np.uint8)
                    elif mx < 65535:
                        props[col] = props[col].astype(np.uint16)
                    elif mx < 4294967295:
                        props[col] = props[col].astype(np.uint32)
                    else:
                        props[col] = props[col].astype(np.uint64)
                else:
                    if mn > np.iinfo(np.int8).min and mx < np.iinfo(np.int8).max:
                        props[col] = props[col].astype(np.int8)
                    elif mn > np.iinfo(np.int16).min and mx < np.iinfo(np.int16).max:
                        props[col] = props[col].astype(np.int16)
                    elif mn > np.iinfo(np.int32).min and mx < np.iinfo(np.int32).max:
                        props[col] = props[col].astype(np.int32)
                    elif mn > np.iinfo(np.int64).min and mx < np.iinfo(np.int64).max:
                        props[col] = props[col].astype(np.int64)    
            
            # Make float datatypes 32 bit
            else:
                props[col] = props[col].astype(np.float32)
            
            # Print new column type
            # print("dtype after: ", props[col].dtype)
    
    # Print final result
    mem_usg = props.memory_usage().sum() / 1024**2 
    print(f"After Reduce : {mem_usg: .3f} MB ({100*mem_usg/start_mem_usg: .2f}% of the initial size)")
    return props

# def upsert(controller, table_name : str = None, line : dict = None):


if __name__=="__main__":
    with open(os.path.join(sys.path[0],"connection.txt"), "r") as f:
            connect_info = f.read().split(",")
    cont = MysqlController(*connect_info)
    cont._connection_info()

    # table_creation(cont, tformat = restaurant_info)
    # table_creation(cont, tformat = menu_info)
    # table_creation(cont, tformat = reviews)

    # table_creation(cont, tformat = user_predict)
    # table_creation(cont, tformat = user_comp)
    # table_creation(cont, tformat= user_info)

    table_creation(cont, tformat = seoul_menu)

    cont.curs.close()
