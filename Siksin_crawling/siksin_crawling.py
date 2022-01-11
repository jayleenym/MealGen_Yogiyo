from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

from bs4 import BeautifulSoup
from requests.compat import urlparse, urljoin
from requests.exceptions import HTTPError
from requests import Session
import requests
import pickle

import pandas as pd
import time
import datetime
from tqdm import tqdm
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))) # .py
# sys.path.append(os.path.dirname(os.path.abspath(os.getcwd()))) # jupyter

# db management libraries
import pymysql
from controller import MysqlController



options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('lang=ko_KR')

# Path
chromedriver_path = '/Users/yejin/Downloads/chromedriver' # mac
# chromedriver_path = 'C://Users//user//Desktop//chromedriver' # window

class Siksin():
    def __init__(self, file = None):
        if not file:
            _id = input("input id(root) : ")
            _pw = input("input pw       : ")
            _db = input("databases      : ")
            connect_info = ("localhost", 3306, _id, _pw, _db)
        else:
            with open(os.path.join(sys.path[0], file), "r") as f:
                connect_info = list(map(lambda x: x.strip(), f.read().split(",")))
        self.controller = MysqlController(*connect_info)
        self.driver = webdriver.Chrome(executable_path = chromedriver_path, options = options)
        # 기본 설정
        self.one = ''
        self.one_id = ''
        self.one_url = ''
        self.one_name = ''

        # 주소지 받아오기
<<<<<<< HEAD
        self.controller.curs.execute('SELECT DISTINCT CONCAT(sido, " ",dong) as adr FROM Address;')
=======
        self.controller.curs.execute('SELECT DISTINCT CONCAT(sigungu, " ",dong) as adr FROM Address;')
>>>>>>> 662adc44be49c1bb66c1277b14fcf39455533d12
        self.ADR = [f[0].replace("세종특별자치시 세종특별자치시", "세종특별자치시") 
                    for f in self.controller.curs.fetchall() 
                    if (f[0] != None) and (f[0] != "세종특별자치시 (알수없음)")]


    def get_all_rtr(self, address : str):
<<<<<<< HEAD
        # 위치로 페이지 들어가기
        url = f'https://www.siksinhot.com/search?keywords={address}'
        self.driver.get(url)

=======
        # 페이지 들어가기
        url = f'https://www.siksinhot.com/search?keywords={address}'
        self.driver.get(url)
        # 핫플레이스 태그 없으면 통과
        if '핫플레이스' not in self.driver.find_element_by_css_selector('div.area_recommand_tag').text:
            return -1
>>>>>>> 662adc44be49c1bb66c1277b14fcf39455533d12
        # 더보기 클릭
        while True:
            try:
                # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                self.driver.find_element_by_css_selector('a.btn_sMore').click()
                time.sleep(1)
            except:
                break

<<<<<<< HEAD
        # 더보기 한 상태로 식당 리스트 가져오기 : 광고 제거 잘 되는지 검사?
        res_list = [res for res in self.driver.find_elements_by_css_selector('#schMove1 > div.listTy1 > ul > li')] 
=======
        # 더보기 한 상태로 식당 리스트 가져오기
        res_list = [res.find_element_by_css_selector('a').get_attribute('href') 
                    for res in self.driver.find_elements_by_css_selector('#schMove1 > div.listTy1 > ul > li')] 
>>>>>>> 662adc44be49c1bb66c1277b14fcf39455533d12
        return res_list

    
    def get_one_info(self, one):
<<<<<<< HEAD
        # self.driver.switch_to.window(self.driver.window_handles[0])
        self.one_url = one.find_element_by_css_selector("a").get_attribute('href')
=======
        self.driver.get(one)
        self.one_url = one
>>>>>>> 662adc44be49c1bb66c1277b14fcf39455533d12
        self.one_id = re.findall('/P/([0-9]+)', self.one_url)[0]

        # 중복 체크
        self.controller.curs.execute(f"""SELECT count(*) FROM siksin_restaurants
                                        WHERE rid = '{self.one_id}' 
                                        AND parking is not NULL;""")
                                        
        if self.controller.curs.fetchone()[0] >= 1: return
        
        # 바로 driver로 열기
        self.driver.get(self.one_url)

        # 식당 정보 제대로 뜰 때까지
        while True:
            try:
                self.one = self.driver.find_element_by_css_selector('div.store_name_score')
                break
            except:
                time.sleep(1.5)
                self.driver.refresh()

        # 주차 없을 수 있음
<<<<<<< HEAD
        try: one_info = re.findall('(.*)([0-9][.][0-9]|평가중).*(주차|발렛)', self.one.find_element_by_css_selector('h3').text)
        except: one_info = re.findall('(.*)([0-9][.][0-9]|평가중)', self.one.find_element_by_css_selector('h3').text)

        # 이름
        try: one_name = one_info[0]
        except: one_name = ""
=======
        try: one_info = re.findall('(.*)([0-9][.][0-9]|평가중).*(주차|발렛)?', self.one.find_element_by_css_selector('h3').text)[0]
        except: one_info = re.findall('(.*)([0-9][.][0-9]|평가중)', self.one.find_element_by_css_selector('h3').text)[0]

        # 이름
        try: self.one_name = one_info[0]
        except: self.one_name = ""
>>>>>>> 662adc44be49c1bb66c1277b14fcf39455533d12
        
        # 사용자 평점
        try: one_star = float(one_info[1])
        except: one_star = 0.0

        # 업종 분류 전체
        try: one_category = self.driver.find_element_by_css_selector('#contents > div > div > div.content > div.sec_left > div > div:nth-child(1) > div:nth-child(1) > p').text.split(">")
        except: one_category = ''
        
        # 주차 여부
        try: one_parking = int(bool(one_info[2]))
        except: one_parking = 0
        
        # 주소
        try: 
            one_adr = self.driver.find_element_by_css_selector('a.txt_adr')
            one_road = one_adr.find_element_by_xpath("../span").text.replace("(지번) ", "")
        except: 
            one_adr = ''
            one_road = ''
        
        # 즐겨찾기, 조회수
        try:
            one_fv = [int(x.text) for x in self.one.find_elements_by_css_selector("ul > li")
                        if x.text != '']
        except: one_fv = [0] * 4

<<<<<<< HEAD
=======
        # 전화
        try: one_phone = self.driver.find_element_by_css_selector('div.p_tel p').text
        except: one_phone = ""

>>>>>>> 662adc44be49c1bb66c1277b14fcf39455533d12
        # 식당 정보 입력
        # 업데이트
        self.controller.curs.execute(f"""SELECT count(*) FROM siksin_restaurants
                                        WHERE rid = '{self.one_id}';""")
        if self.controller.curs.fetchone()[0] >= 1: return
        else:
            self.controller.insert('siksin_restaurants', 
            {
                'updated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'rname': one_name,
                'rid': self.one_id, 
                'main_category': one_category[0].strip(),
                'sub_category' : one_category[1].strip(),
                'star' : one_star,
                'favorite' : one_fv[1],
                'address' : one_adr.text,
                'road_address' : one_road,
<<<<<<< HEAD
                'phone' : self.driver.find_element_by_css_selector('div.p_tel p').text,
                'parking' : one_parking,
                'view' : one_fv[2]
            })
                
    def get_one_menus(self):
        # 안 열려 있으면 열기 
        if len(self.driver.window_handles) == 1: self.one_url.click()
        self.driver.switch_to.window(self.driver.window_handles[1])
        # 메뉴 더보기
        try:
            self.driver.find_element_by_css_selector('#div_detail div.menu-info a.more-btn').click()
        except:
            pass
        
        menu = [m.text.replace("'", '"') for m in self.driver.find_elements_by_css_selector('ul.list.Restaurant_MenuList li p.l-txt.Restaurant_MenuItem') if m.text != '']
        price = [p.text for p in self.driver.find_elements_by_css_selector('ul.list.Restaurant_MenuList li p.r-txt.Restaurant_MenuPrice') if p.text != '']
=======
                'phone' : one_phone,
                'parking' : one_parking,
                'view' : one_fv[2]
            })

    
    def get_one_menus(self):        
        menu = [m.text.replace("'", '"').split("\n") for m in self.driver.find_elements_by_css_selector('ul.menu_ul > li') if m.text != '']
>>>>>>> 662adc44be49c1bb66c1277b14fcf39455533d12
        
        for m in menu:
            # 중복 체크
            self.controller.curs.execute(f"""SELECT count(*) 
                                    FROM siksin_menu 
                                    WHERE rid = '{self.one_id}'
                                    AND menu = '{m[0]}';""")
            if self.controller.curs.fetchone()[0] >= 1: continue
            
            self.controller.insert('siksin_menu', line = {
                'updated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'rname': self.one_name,
                'rid': self.one_id,
                'menu' : m[0],
                'price' : m[1]
            })

    
    def get_one_rvs(self):
        # 안 열려 있으면 열기 
        # if len(self.driver.window_handles) == 1: self.one_url.click()
        # self.driver.switch_to.window(self.driver.window_handles[1])
        # 더보기
        while True:
            try:
                self.driver.find_element_by_css_selector('div.siksin_review a.btn_sMore').click()
                time.sleep(1.2)
            except: break
        
        # 리뷰 크롤링
        for one in self.driver.find_elements_by_css_selector('div.rList > ul > li.false'):

            # 리뷰어 아이디, 없을 수도 있음
            try: reviewer = one.find_element_by_css_selector('div.name_data').text
            except: reviewer = ""
            
            try: star = float(one.find_element_by_css_selector("div.newStarBox").text)
            except: star = 0.0
            
            try: review = one.find_element_by_css_selector("div.score_story p").text.replace("'", '"')
            except: review = ""

            try: heart = int(re.findall('[0-9]+', one.find_element_by_css_selector("a.btn_like"))[0])
            except: heart = 0

            # 리뷰 중복체크
            self.controller.curs.execute(f"""SELECT count(*) 
                                    FROM siksin_reviews 
                                    WHERE rid = '{self.one_id}' AND 
                                            review = '{review}';""")
            if self.controller.curs.fetchone()[0] >= 1: continue

            # table에 입력
            self.controller.insert('siksin_reviews', line = {
                'updated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'rname': self.one_name,
                'rid': self.one_id,
                'reviewer' : reviewer,
                'heart' : heart,
                'star' : star,
                'review' : review
            })
            
if __name__ == "__main__":
    siksin = Siksin(file = "../connection.txt")
    siksin.controller._connection_info()
    errors = []
with tqdm(total = len(siksin.ADR)) as tm:
    i = 0
    while i < len(siksin.ADR):
        adr = siksin.ADR[i]
        try:
            rtr_list = siksin.get_all_rtr(adr)
            if rtr_list == -1:
                i += 1
                break
            for r in rtr_list[40:]:
                # print(r)
                siksin.get_one_info(r)
                siksin.get_one_menus()
                siksin.get_one_rvs()
                # 하나 크롤링 끝!
                    # siksin.driver.close()
            i += 1
            tm.update(1)
        except TimeoutException as ex:
            siksin.driver.quit()
            print(ex)
            siksin = Siksin(file = "../connection.txt")
            print("******** RECONNECT ********")
        except ElementClickInterceptedException as ec:
            time.sleep(5)
            siksin.driver.refresh()
        except Exception as e:
            print(adr + ": " + e)
            # i += 100
            errors = errors.append(adr)
            i += 1
            siksin.driver.quit()
            siksin = Siksin(file = "../connection.txt")
            print("****** QUIT & RECONNECT ******")
pickle.dump(errors, open("./error_address.txt", "wb"))