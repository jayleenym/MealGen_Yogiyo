######################################################
# table definition
#
######################################################

import pymysql
import os
import sys
import numpy as np
import datetime
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from controller import MysqlController


dc_res = """
CREATE TABLE diningcode_restaurants
(
    _id INT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT "ID",
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성 일시',
    updated_at DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '업데이트 일시',
    rname VARCHAR(32) COMMENT '식당명',
    rid VARCHAR(50) COMMENT '다이닝코드 식당id',
    category  VARCHAR(50) COMMENT '다이닝코드 식당 분류',
    address VARCHAR(255) COMMENT '다이닝코드에 등록된 주소',
    phone VARCHAR(100) COMMENT '전화번호',
    grade INT COMMENT '다이닝코드 계산 점수',
    star DECIMAL(2,1) COMMENT '5점만점 점수',
    favorite INT COMMENT '좋아요 갯수'
)
COMMENT '다이닝코드 식당 정보';
"""

dc_menu = """
CREATE TABLE diningcode_menu
(
    _id INT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT "ID",
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성 일시',
    updated_at DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '업데이트 일시',
    rname VARCHAR(32) COMMENT '식당명',
    rid VARCHAR(50) COMMENT '다이닝코드 식당id',
    menu VARCHAR(100) COMMENT '메뉴 이름',
    price VARCHAR(32) COMMENT '메뉴 가격'
)
COMMENT '다이닝코드 식당 메뉴 정보';
"""

dc_rev = """
CREATE TABLE diningcode_reviews
(
    _id INT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT "ID",
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성 일시',
    updated_at DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '업데이트 일시',
    rname VARCHAR(32) COMMENT '식당명',
    rid VARCHAR(50) COMMENT '다이닝코드 식당id',
    reviewer  VARCHAR(50) COMMENT '리뷰어 이름',
    reviewer_info VARCHAR(50) COMMENT '리뷰어 정보',
    star DECIMAL(2,1) COMMENT '5점만점 점수',
    date DATETIME COMMENT '리뷰 등록 날짜',
    review VARCHAR(255) COMMENT '리뷰내용'
)
COMMENT '다이닝코드 리뷰 정보';
"""


def table_creation(controller, tformat):
    try:
        controller.curs.execute(tformat)
        controller.conn.commit()
        print(f"TABLE CREATED.")
    except Exception as e:
        print(e)



if __name__=="__main__":
    with open(os.path.join("connection.txt"), "r") as f:
            connect_info = f.read().split(",")
    cont = MysqlController(*connect_info)
    cont._connection_info()

    table_creation(cont, tformat = dc_res)
    table_creation(cont, tformat = dc_menu)
    table_creation(cont, tformat = dc_rev)
    cont.curs.close()
