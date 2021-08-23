# crawling libraries
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

# basic
import pandas as pd
import os
import sys
import time
import datetime
from datetime import timedelta
import json
from tqdm.auto import tqdm
import re
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# db management libraries
import pymysql
from dbconfig import insert
from controller import MysqlController


API_header = {'x-apisecret': 'fe5183cc3dea12bd0ce299cf110a75a2',
              'x-apikey': 'iphoneap'}

yesterday = (datetime.date.today() - timedelta(days = 1)).isoformat()
today = datetime.date.today().isoformat()

txt_headers = ['시군구코드', '기초구간일련번호', '기초번호본번', '기초번호부번', '도로구간일련번호',
          '시도명', '시군구명', '읍면동코드', '읍면동명', '도로명코드', '도로명', '도로구간시점', '도로구간종점',
          '중심점좌표_X', '중심점좌표_Y']

review_headers = ['name', 'register_number', 'rating', 'menu_items', 
                'menu_summary', 'rating_quantity', 'rating_taste', 
                'rating_delivery', 'is_mine_review','is_mine_like', 'nickname', 'id', 'time']

# Chrome driver option
options = webdriver.ChromeOptions()
options.add_argument("headless")

# Path
chromedriver_path = './crawling/chromedriver'
address_path = './address'


class UpdateCrawling():
    def __init__(self, file = None):
        if not file:
            _id = input("input id(root) : ")
            _pw = input("input pw       : ")
            _db = input("databases      : ")
            connect_info = ("localhost", 3306, _id, _pw, _db)
        else:
            with open(os.path.join(sys.path[0], file), "r") as f:
                connect_info = f.read().split(",")
        self.controller = MysqlController(*connect_info)
        

    def restaurant_information(self, file, driver):
        if file.endswith('csv'): city = pd.read_csv(f"{address_path}/{file}")
        RESTAURANTS = []

        for i in range(len(city)):
            p = 0
            while(1):
                params = {
                            'items' : 200,
                            'lat': city['중심점좌표_Y'][i],
                            'lng': city['중심점좌표_X'][i],
                            'order': 'review_count',
                            'page': p
                            }
                
                url = "https://www.yogiyo.co.kr/api/v1/restaurants-geo/"

                json_data = requests.get(url, params = params, headers = API_header).json()
                if len(json_data['restaurants']) == 0: break
                
                for j in range(len(json_data['restaurants'])):
                    res = json_data['restaurants'][j]

                    q = f"SELECT count(*) FROM restaurant_info WHERE restaurant_id = {res['id']}"
                    self.controller.curs.execute(q)
                    result = self.controller.curs.fetchone()
                    
                    # review 수 업데이트
                    if result[0] > 0:
                        # q = f"UPDATE restaurant_info SET review_count = {res['review_count']} \
                            # WHERE restaurant_id = {res['id']} AND NOT review_count = {res['review_count']};"
                        # self.controller.curs.execute(q)
                        # self.controller.conn.commit()
                        j += 1
                        continue

                    driver.get(f'https://www.yogiyo.co.kr/mobile/#/{res["id"]}')
                    time.sleep(1)
                    while True: # 정보 클릭
                        try:
                          driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[1]/ul/li[3]').click()
                          break
                        except:
                          try:
                            driver.get(f'https://www.yogiyo.co.kr/mobile/#/{res["id"]}') # 새로고침
                            time.sleep(0.5) # give more delay
                          except:
                            # Max Try exception
                            driver.close()
                            driver = webdriver.Chrome(executable_path = chromedriver_path)
                            driver.get(f'https://www.yogiyo.co.kr/mobile/#/{res["id"]}')
                    
                    # 사업자등록번호 추가                                 
                    regist_num = driver.find_element_by_xpath('//*[@id="info"]/div[4]/p[2]/span').text

                    # 식당 정보 json
                    restaurant = {
                                    'restaurant_id' : res['id'], 
                                    'name' : res['name'], 
                                    'company_id' : regist_num,
                                    'phone' : res['phone'], 
                                    'address' : res['address'], 
                                    'sido' : res['address'].split()[0], 
                                    'sigungu' : res['address'].split()[1],
                                    'franchise_yn' : int(bool(res['franchise_name'])),
                                    'franchise_name' : None,
                                    'franchise_id' : -1, # default None value
                                    'categories' : ",".join(res['categories']),
                                    'delivery_yn' : int(bool(res['is_available_delivery'])), 
                                    'delivery_time' : res['estimated_delivery_time'], 
                                    'delivery_fee' : res['delivery_fee'], 
                                    'lat' : res['lat'],
                                    'lng' : res['lng'], 
                                    'avg' : res['review_avg'], 
                                    'review_count' : res['review_count'],
                                    'updated_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                    # 프랜차이즈일 때 업데이트
                    if restaurant['franchise_yn']:
                        restaurant['franchise_name'] = res['franchise_name']
                        restaurant['franchise_id'] = res['franchise_id']

                    insert(self.controller, table_name = "restaurant_info", line = restaurant)
                    self.controller.conn.commit()
                    # 이상한거 update - 요기요시, 요기요구, None 64-11

                    RESTAURANTS.append(restaurant)
                    json.dump(RESTAURANTS, open(f'./restaurant_info_{today}.json', "w"), ensure_ascii=False, indent='\t')
                p += 1
        return len(RESTAURANTS)


    def preprocess_res(self):
        q = '''
        UPDATE restaurant_info
        SET phone = NULL, delivery_time = NULL, 
            address = (CASE WHEN sido = '서울' THEN replace(replace(address, sido, '서울특별시'), '서울특별시특별시', '서울특별시')
                            WHEN sido = '인천' THEN replace(replace(address, sido, '인천광역시'), '인천광역시광역시', '인천광역시')
                            WHEN sido in ('경기', '경기동') THEN replace(address, sido, '경기도')
                            WHEN sido = '세종' THEN replace(address, sido, '세종특별자치시')
                            WHEN sido = '충남' THEN replace(address, sido, '충청남도')
                            WHEN sido in ('대전', '대전시') THEN replace(address, sido, '대전광역시')
                            WHEN sido = '광주' THEN replace(address, sido, '광주광역시')
                            WHEN sido = '울산' THEN replace(address, sido, '울산광역시')
                            WHEN sido = '부산' THEN replace(address, sido, '부산광역시')
                            WHEN sido = '충북' THEN replace(address, sido, '충청북도')
                            WHEN sido in ('대구', '대구시') THEN replace(address, sido, '대구광역시')
                            WHEN sido = '전남' THEN replace(address, sido, '전라남도')
                            WHEN sido = '경북' THEN replace(address, sido, '경상북도')
                            WHEN sido = '경남' THEN replace(address, sido, '경상남도')
                            WHEN sido = '제주' THEN replace(replace(address, sido, '제주특별자치도'), '제주특별자치도시', '제주시')
                        END)
        WHERE phone = '000000000' or delivery_time = '' or
              sido in ('서울', '인천', '경기', '경기동', '세종', '충남','대전', '대전시', 
                       '광주' , '울산' , '부산', '충북', '대구', '대구시', '전남', '경북', 
                       '경남', '제주');
        '''
        self.controller.curs.execute(q)
        self.controller.conn.commit()

        q = '''
        UPDATE restaurant_info 
        SET sido = substring_index(address, " ", 1),
            sigungu = replace(substring_index(address, " ", 2), substring_index(address, " ", 1), "");'''
        self.controller.curs.execute(q)
        self.controller.conn.commit()

    def menu_information(self, restaurant_id, MENUS):
        response = requests.get(f"https://www.yogiyo.co.kr/api/v1/restaurants/{restaurant_id}/menu", headers=API_header)
        try:
            menu = response.json()
        except Exception as e:
            # error
            print(e)
            return 0
        
        for M in menu:
            try:
                len(M['items'])
            except:
                return 0 # no items

            for m in M['items']:
                q = f"SELECT count(*) FROM menu_info WHERE menu_id = {m['id']}"
                self.controller.curs.execute(q)
                result = self.controller.curs.fetchone()
                if result[0] >0 : # 중복제거
                    continue

                # 메인메뉴 크롤링
                _menu = {
                    "menu_id": m['id'],
                    "restaurant_id": restaurant_id,
                    "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "name": m['name'],
                    "description": m['description'],
                    "price": m['price'],
                }
                insert(self.controller, table_name = "menu_info", line = _menu)
                self.controller.conn.commit()

                MENUS.append(_menu)
        json.dump(MENUS, open(f'./menu_info_{today}.json', "w", encoding = "utf-8"), ensure_ascii=False, indent='\t')
        return len(MENUS)


    def preprocess_menu(self):
        q = """UPDATE menu_info SET name = replace(name, "'", ""); """
        self.controller.curs.execute(q)
        self.controller.conn.commit()

        q2 = 'UPDATE menu_info SET description = NULL WHERE description = "";'
        self.controller.curs.execute(q2)
        self.controller.conn.commit()
        


    def reviews(self, restaurant_id, REVIEWS, yesterday = yesterday):
        while True:
            try:
                response = requests.get(f"https://www.yogiyo.co.kr/api/v1/reviews/{restaurant_id}/").json()
                break
            except:
                time.sleep(1.5)
        r = 0
        while (r < len(response)):
        # for r in range(len(response)):
            rev = response[r]
            
            # 빈 메뉴 선택 생략
            if rev['menu_summary'] == "":
                r += 1
                continue

            q = f"SELECT count(*) FROM reviews WHERE user_id = {rev['id']} AND written_time = '{rev['time']}';"
            self.controller.curs.execute(q)
            result = self.controller.curs.fetchone()
            if result[0] > 0: # 중복 제거
                r += 1
                continue

            # menu_id 배정
            # m = re.findall('(.*?)/[0-9]+', rev['menu_summary'])[0]
            # m_q1 = f"SELECT menu_id FROM menu_info WHERE name = '{m}' AND restaurant_id = {restaurant_id};"
            # self.controller.curs.execute(m_q1)
            # try:
                # m_id = self.controller.curs.fetchone()[0]
            # except:
                # m_id = -1
            try:
                m_id = rev['menu_items']['id']
            except:
                m_id = -1
            
            # yesterday (변경가능) ~ today까지
            # if (rev['time'] >= yesterday) and (rev['time'] < today):
            if (rev['time'] < today):
                review = {
                          'written_time' : rev['time'],
                          'nickname' : rev['nickname'],
                          'user_id' : rev['id'],
                          'restaurant_id' : restaurant_id,
                          'menu' : rev['menu_summary'].replace("'", ""),
                          'menu_id' : m_id, # default -1
                          'review' : rev['comment'],
                          'quantity' : rev['rating_quantity'],
                          'taste' : rev['rating_taste'],
                          'delivery' : rev['rating_delivery'],
                          'rating' : rev['rating'],
                          'like_dislike' : int(bool(rev['rating'] >= 2.5)),
                          'updated_at' : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                          }
        
                REVIEWS.append(review)
                json.dump(REVIEWS, open(f'./reviews_{yesterday}.json', 'w'), ensure_ascii = False, indent = '\t')
                insert(self.controller, table_name = "reviews", line = review)
                self.controller.conn.commit()
                r += 1
            else: 
                r += 1
                break

        return len(REVIEWS)


    def preprocess_rev(self):
        # 제거되지 않은 ' 없애기
        q = '''UPDATE reviews SET menu = replace(menu, "'", "");'''
        self.controller.curs.execute(q)
        self.controller.conn.commit()
        
        # menu가 빈 데이터 삭제
        q = "DELETE FROM reviews WHERE menu = '';"
        self.controller.curs.execute(q)
        self.controller.conn.commit()

        # menu_id 결측치 처리
        q = "SELECT count(*) FROM menu_info WHERE menu_id = -1;"
        self.controller.curs.execute(q)
        result = self.controller.curs.fetchone()
        if result[0] > 0: 
            # menu_id update - 다른 방법이 생각이 안남..
            q = "SELECT name, menu_id, restaurant_id FROM menu_info ORDER BY restaurant_id ASC;"
            self.controller.curs.execute(q)
            menus, id, res = [], [], []
            for i in self.controller.curs.fetchall():
                menus.append(i[0])
                id.append(i[1])
                res.append(i[2])
            
            for i in tqdm(range(len(menus))):
                q1 = f"SELECT count(*) FROM reviews WHERE menu LIKE '{menus[i]}%' AND restaurant_id = {res[i]} AND menu_id = -1;"
                self.controller.curs.execute(q1)
                result = self.controller.curs.fetchone()
                if result[0]==0: 
                    # 해당 메뉴 리뷰 없음 or 이미 update 완료
                    continue 
            
                q2 = f"UPDATE reviews SET menu_id = {id[i]} WHERE menu LIKE '{menus[i]}%' AND restaurant_id = {res[i]};"
                self.controller.curs.execute(q2)
                self.controller.conn.commit()
        else: return

    # daily update
    def crawl_restaurant(self):
        cnt = 0
        print("****** INITIATING RESTAURANT CRAWLING *******")
        driver = webdriver.Chrome(executable_path = chromedriver_path)
        for f in tqdm(os.listdir(address_path)): 
            cnt += self.restaurant_information(f, driver)
            self.preprocess_res()
        driver.close()
        print(f"****** {cnt} restaurants added {today}. ******")


    def get_all_restaurant_ids(self):
        q = "select distinct restaurant_id from restaurant_info;"
        self.controller.curs.execute(q)
        return list(list(zip(*self.controller.curs.fetchall()))[0])


    def crawl_menu(self, s = None, e = None):
        cnt = 0
        MENU = []
        restaurants = self.get_all_restaurant_ids()
        print("****** INITIATING MENU CRAWLING *******")
        print(f" - RESTAURANTS({today}) : {len(restaurants)}")
        for restaurant_id in tqdm(restaurants[s: e]): 
            cnt += self.menu_information(restaurant_id, MENU)
            self.preprocess_menu()
        print(f"****** {cnt} menus updated {today}. ******")
    

    def crawl_review(self, sdate):
        cnt = 0
        REV = []
        restaurants = self.get_all_restaurant_ids()
        print("****** INITIATING REVIEW CRAWLING *******")
        print(f" - RESTAURANTS({today}) : {len(restaurants)}")
        for restaurant_id in tqdm(restaurants):       
            cnt += self.reviews(restaurant_id, REV, yesterday = sdate)
            self.preprocess_rev()
        print(f"****** {cnt} reviews updated {sdate} ~ {today}. ******")



if __name__ == "__main__":
    server = UpdateCrawling(file = "../connection.txt")
    server.controller._connection_info()

    # daily crawling
    # server.crawl_restaurant()
    # server.crawl_menu()
    server.crawl_review(yesterday)
# 
    server.controller.curs.close()
