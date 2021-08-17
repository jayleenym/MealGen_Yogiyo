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
    _id INT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
    updated_at DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '업데이트 일시',
    written_time DATETIME NOT NULL COMMENT '작성일시',
    nickname VARCHAR(50) COMMENT '유저닉네임',
    user_id INT NOT NULL COMMENT '유저 id(yogiyo)',
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

def table_creation(controller, tformat):
    try:
        controller.curs.execute(tformat)
        controller.conn.commit()
        print("DONE")
    except Exception as e:
        print(e)

# temp function(insertion)
def insert(controller, table_name : str = None, line : dict = None):
    columns = ','.join(line.keys())
    placeholders = ','.join(['%s']*len(line))
    sql_command = """INSERT INTO %s(%s) VALUES(%s)"""%(table_name, columns, placeholders)
    controller.curs.execute(sql_command, tuple(str(val) for val in line.values()))
    # need controller.commit() after executing all lines


if __name__=="__main__":
    with open(os.path.join(sys.path[0],"connection.txt"), "r") as f:
            connect_info = f.read().split(",")
    cont = MysqlController(*connect_info)
    cont._connection_info()

    # table_creation(cont, tformat=restaurant_info)
    # table_creation(cont, tformat = menu_info)
    # table_creation(cont, tformat=reviews)

    cont.curs.close()
