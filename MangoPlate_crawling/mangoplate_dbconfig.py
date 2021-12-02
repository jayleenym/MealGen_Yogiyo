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


mango_info = """
CREATE TABLE mango_restaurants
(
    _id INT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT "ID",
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성 일시',
    updated_at DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '업데이트 일시',
    mango_id VARCHAR(50) NOT NULL COMMENT '망고플레이트 식당 id',
    name VARCHAR(50) COMMENT '식당명',
    cnt_hit INT COMMENT '페이지 방문 수',
    cnt_review INT COMMENT '리뷰 수',
    cnt_favorite INT COMMENT '즐겨찾기 수',
    category  VARCHAR(50) COMMENT '망고플레이트 식당 분류',
    road_address VARCHAR(255) COMMENT '도로명주소',
    address VARCHAR(255) COMMENT '지번주소',
    phone VARCHAR(50) COMMENT '전화번호',
    price VARCHAR(50) COMMENT '가격대'
    )
COMMENT '망고플레이트 등록 식당';
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

    table_creation(cont, tformat = mango_info)
    cont.curs.close()
