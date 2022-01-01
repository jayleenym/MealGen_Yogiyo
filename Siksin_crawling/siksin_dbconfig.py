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


ss_res = """
CREATE TABLE siksin_restaurants
(
    _id INT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT "ID",
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성 일시',
    updated_at DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '업데이트 일시',
    rname VARCHAR(32) COMMENT '식당명',
    rid VARCHAR(50) COMMENT '식신 식당id',
    main_category VARCHAR(50) COMMENT '식신 식당 대분류',
    sub_category  VARCHAR(50) COMMENT '식신 식당 소분류',
    address VARCHAR(255) COMMENT '식신에 등록된 지번 주소',
    road_address VARCHAR(255) COMMENT '식신에 등록된 도로명 주소',
    phone VARCHAR(100) COMMENT '전화번호',
    star DECIMAL(2,1) COMMENT '식신 5점만점 점수',
    favorite INT COMMENT '즐겨찾기 갯수',
    view INT COMMENT '조회 수',
    parking TINYINT COMMENT '주차 가능 여부'
)
COMMENT '식신 식당 정보';
"""

ss_menu = """
CREATE TABLE siksin_men신
(
    _id INT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT "ID",
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성 일시',
    updated_at DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '업데이트 일시',
    rname VARCHAR(32) COMMENT '식당명',
    rid VARCHAR(50) COMMENT '식신 식당id',
    menu VARCHAR(100) COMMENT '메뉴 이름',
    price VARCHAR(32) COMMENT '메뉴 가격'
)
COMMENT '식신 식당 메뉴 정보';
"""

ss_rev = """
CREATE TABLE siksin_reviews
(
    _id INT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT "ID",
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성 일시',
    updated_at DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '업데이트 일시',
    rname VARCHAR(32) COMMENT '식당명',
    rid VARCHAR(50) COMMENT '식신 식당id',
    reviewer  VARCHAR(50) COMMENT '리뷰어 이름',
    reviewer_info VARCHAR(50) COMMENT '리뷰어 정보',
    star DECIMAL(2,1) COMMENT '5점만점 점수',
    date DATETIME COMMENT '리뷰 등록 날짜',
    review VARCHAR(255) COMMENT '리뷰내용'
)
COMMENT '식신 리뷰 정보';
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

    table_creation(cont, tformat = ss_res)
    # table_creation(cont, tformat = ss_menu)
    # table_creation(cont, tformat = ss_rev)
    cont.curs.close()
