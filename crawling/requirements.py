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
from controller import MysqlController


API_header = {'x-apisecret': 'fe5183cc3dea12bd0ce299cf110a75a2',
              'x-apikey': 'iphoneap'}

yesterday = (datetime.date.today() - timedelta(days = 1)).isoformat()
today = datetime.date.today().isoformat()

review_headers = ['name', 'register_number', 'rating', 'menu_items', 
                'menu_summary', 'rating_quantity', 'rating_taste', 
                'rating_delivery', 'is_mine_review','is_mine_like', 'nickname', 'id', 'time']

# Chrome driver option
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Path
chromedriver_path = '/Users/yejin/Downloads/chromedriver'
address_path = './address'