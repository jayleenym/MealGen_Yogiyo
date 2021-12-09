from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from bs4 import BeautifulSoup
from requests.compat import urlparse, urljoin
from requests.exceptions import HTTPError
from requests import Session
import requests

import pandas as pd
import time
import datetime
from tqdm import tqdm
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# db management libraries
import pymysql
from controller import MysqlController


# 연결
with open('./connection.txt', "r") as f:
                connect_info = list(map(lambda x: x.strip(), f.read().split(",")))
server = MysqlController(*connect_info)

# 주소지 받아오기
server.curs.execute('SELECT DISTINCT CONCAT(sigungu, " ",dong) as adr FROM Address;')
ADR = [f[0] for f in server.curs.fetchall()]


# 식당 리스트 받아오기
options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

## Path
chromedriver_path = '/Users/yejin/Downloads/chromedriver'
driver = webdriver.Chrome(executable_path = chromedriver_path, options = options)

for adr in tqdm(ADR):
# adr = ADR[0]
    # 주소지별 사이트 입장
    url = f'https://www.diningcode.com/list.php?query={adr}'
    driver.get(url)

    # 더보기 다 누르기
    while True:
        try:
            driver.find_element_by_css_selector('#div_list_more').click()
            time.sleep(1)
        except:
            break
    
    # 광고 제거 안됨
    res_list = [res for res in driver.find_elements_by_css_selector('#div_list > li') if type(res.get_property('onmouseenter')) == dict]
    
    # 식당 한개씩 들어가기
    for res in res_list:
        # res = res_list[0]
        driver.switch_to.window(driver.window_handles[0])
        one_url = res.find_element_by_tag_name('a')
        one_id = re.findall('rid=(.*)', one_url.get_attribute('href'))[0]
        # 중복 체크
        server.curs.execute(f"SELECT count(*) FROM diningcode_restaurants WHERE diningcode_id = '{one_id}';")
        if server.curs.fetchone()[0] >= 1: continue

        # 클릭해서 열고 활성탭 옮김
        one_url.click()
        driver.switch_to.window(driver.window_handles[1])

        one_name = driver.find_element_by_css_selector('div.tit-point').text
        
        try:
            one_grade = float(driver.find_element_by_css_selector('div.sns-grade strong').text.replace('점', ""))
        except:
            one_grade = 0.0
        
        try:
            one_star = float(driver.find_element_by_css_selector('div.sns-grade span.point strong').text.replace('점', ""))
        except:
            one_star = 0.0


        # 식당정보
        server.insert('diningcode_restaurants', line = {
            'updated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'name': one_name,
            'diningcode_id': one_id, 
            'category': driver.find_element_by_css_selector('div.btxt').text.split('|')[1].strip(),
            'grade' : one_grade,
            'star' : one_star,
            'favorite' : int(driver.find_element_by_css_selector('div.favor-pic-appra i').text),
            'address' : driver.find_element_by_css_selector('li.locat').text,
            'phone' : driver.find_element_by_css_selector('li.tel').text
            # tag, char은 제외
        })
        

        # 메뉴
        menu = [m.text for m in driver.find_elements_by_css_selector('ul.list.Restaurant_MenuList li p.l-txt.Restaurant_MenuItem') if m.text != '']
        # price = [int(re.sub('[원,]', "", p.text)) if re.sub('[원,]', "", p.text).isalnum() else p.text 
        price = [p.text
                    for p in driver.find_elements_by_css_selector('ul.list.Restaurant_MenuList li p.r-txt.Restaurant_MenuPrice') if p.text != '']
        
        if len(menu) != 0:
            for i in range(len(menu)):
                # 중복 체크
                server.curs.execute(f"""SELECT count(*) 
                                           FROM diningcode_menu 
                                           WHERE diningcode_id = '{one_id}'
                                           AND menu = '{menu[i]}';""")
                if server.curs.fetchone()[0] >= 1: continue
                
                server.insert('diningcode_menu', line = {
                    'updated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'name': one_name,
                    'diningcode_id': one_id,
                    'menu' : menu[i],
                    'price' : price[i]
                })

        # 리뷰 정보
        # 안되면 NoSuchElementException
        # 끝까지 더보기 누르고
        while True:
            try:
                driver.find_element_by_css_selector('#div_more_review').click()
                time.sleep(1.2)
            except:
                break

        # 리뷰 크롤링
        reviewers = [re.findall('(.*) [(](.*)[)]', pr.text)[0] for pr in driver.find_elements_by_css_selector('p.person-grade span.btxt')]
        # point = [s.text for s in driver.find_elements_by_css_selector('p.point-detail')]
        review = [r.text for r in driver.find_elements_by_css_selector('p.review_contents.btxt')]
        date = [d.text for d in driver.find_elements_by_css_selector('span.star-date')]
        star = [s for s in driver.find_elements_by_css_selector('i.star > i')]

        if len(reviewers) != 0:
            for i in range(len(reviewers)):
                server.curs.execute(f"""SELECT count(*) 
                                           FROM diningcode_reviews 
                                           WHERE diningcode_id = '{one_id}' AND 
                                                 review = '{review[i]}';""")
                if server.curs.fetchone()[0] >= 1: continue
                # 리뷰
                try:
                    d = datetime.datetime.strptime(date[i], "%Y년 %m월 %d일") 
                except:
                    d = datetime.datetime.strptime(date[i], "2021년 %m월 %d일")
                server.insert('diningcode_reviews', line = {
                    'updated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'restaurant_name': driver.find_element_by_css_selector('div.tit-point').text,
                    'diningcode_id': one_id,
                    'reviewer' : reviewers[i][0],
                    'reviewer_info' : reviewers[i][1],
                    'star' : int(re.findall('[0-9]+', star[i].get_attribute('style'))[0]) / 100 * 5 ,
                    # 'point_taste' : float(re.findall('맛([0-5][.]?[0-9]?)', point[i])[0]),
                    # 'point_price' : float(re.findall('가격([0-5][.]?[0-9]?)', point[i])[0]),
                    # 'point_service' : float(re.findall('서비스([0-5][.]?[0-9]?)', point[i])[0]),
                    'review' : review[i],
                    'date' : d
                })
        
        # 식당 하나 끝
        driver.close()

# 완전 종료
driver.quit()