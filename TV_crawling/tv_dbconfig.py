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


global TV_program

TV_program = """
CREATE TABLE TV_restaurants
(
    _id INT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT "ID",
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성 일시',
    updated_at DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '업데이트 일시',
    name VARCHAR(32) COMMENT '식당명',
    category  VARCHAR(50) COMMENT '네이버 지도 분류',
    address VARCHAR(255) COMMENT '지번주소',
    2TV생생정보 TINYINT,
    6시내고향 TINYINT,
    백종원의골목식당 TINYINT,
    맛있는녀석들 TINYINT,
    모닝와이드 TINYINT,
    생방송오늘저녁 TINYINT,
    생방송투데이 TINYINT,
    생활의달인 TINYINT,
    수요미식회 TINYINT,
    전지적참견시점 TINYINT
)
COMMENT 'TV 프로그램 방영 식당';
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

    table_creation(cont, tformat = TV_program)
    cont.curs.close()
