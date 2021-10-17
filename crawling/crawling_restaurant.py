from requirements import *

class UpdateRestaurant():
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
        

    def restaurant_information(self, driver):
        self.controller.curs.execute('SELECT X, Y FROM Address;')
        city = self.controller.curs.fetchall()
        RESTAURANTS = []

        for i in tqdm(range(len(city))):
            p = 0
            while(1):
                params = {
                            'items' : 200,
                            'lat': city[i][1],
                            'lng': city[i][0],
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
                        #     WHERE restaurant_id = {res['id']} AND NOT review_count = {res['review_count']};"
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
                            driver = webdriver.Chrome(executable_path = chromedriver_path, chrome_options=options)
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
                                    # 'delivery_fee' : res['delivery_fee'], 
                                    'delivery_fee' : res['adjusted_delivery_fee'], # key 이름 바뀜
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

                    self.controller.insert(table_name = "restaurant_info", line = restaurant)
                   
                    # 이상한거 update - 요기요시, 요기요구, None 64-11

                    RESTAURANTS.append(restaurant)
                    json.dump(RESTAURANTS, open(f'./restaurant_info_{today}.json', "w"), ensure_ascii=False, indent='\t')
                p += 1
        return len(RESTAURANTS)


    def preprocessing(self):
        self.controller.curs.execute("""
        UPDATE restaurant_info
        SET phone = NULL WHERE phone = '000000000' or phone = '';""")
        self.controller.conn.commit()

        self.controller.curs.execute("""UPDATE restaurant_info
        SET delivery_time = NULL WHERE delivery_time = '';""")
        self.controller.conn.commit()

        q = '''
        UPDATE restaurant_info
        SET address = (CASE WHEN sido = '서울' THEN replace(replace(address, sido, '서울특별시'), '서울특별시특별시', '서울특별시')
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
        WHERE sido in ('서울', '인천', '경기', '경기동', '세종', '충남','대전', '대전시', 
                    '광주' , '울산' , '부산', '충북', '대구', '대구시', '전남', '경북', 
                    '경남', '제주');
        '''
        self.controller.curs.execute(q)
        self.controller.conn.commit()

        q = '''
        UPDATE restaurant_info 
        SET sido = substring_index(address, " ", 1),
            sigungu = replace(substring_index(address, " ", 2), substring_index(address, " ", 1), "");
        '''
        self.controller.curs.execute(q)
        self.controller.conn.commit()

    def fill_address(self):
        while True:
            try:
                rs = pd.read_sql('SELECT * FROM restaurant_info WHERE address is NULL;', server.controller.conn)
                driver = webdriver.Chrome(executable_path = chromedriver_path, options=options)

                for id in tqdm(rs.restaurant_id.values):
                    driver.get(f'https://www.yogiyo.co.kr/mobile/#/{id}')
                    time.sleep(0.5)

                    if driver.current_url != f'https://www.yogiyo.co.kr/mobile/#/{id}/':
                        self.controller.curs.execute(f'UPDATE restaurant_info SET company_id = "폐점", name = "폐점", phone = "폐점",\
                        address = "폐점", sido = "폐점", sigungu = "폐점" WHERE restaurant_id = {id};')
                        self.controller.conn.commit()
                        continue

                    try:    
                        driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[1]/ul/li[3]').click()
                        time.sleep(0.3)
                        p = driver.find_element_by_css_selector('#info > div:nth-child(2) > p:nth-child(3) > span').text.replace(' (요기요 제공 번호)', '')
                        a = driver.find_element_by_css_selector('#info > div:nth-child(2) > p:nth-child(4) > span').text
                        d = a.split()[0]
                        g = a.split()[1]
                        # print(p, a, d, g)
                        self.controller.curs.execute(f"UPDATE restaurant_info \
                        SET phone = '{p}', address = '{a}', sido = '{d}', sigungu = '{g}'\
                        WHERE restaurant_id = {id};")
                        self.controller.conn.commit()
                    except: continue
                        
                self.preprocess_res()
                driver.close()
                break
            except:
                print("Restart...", datetime.datetime.now())
                self.preprocess_res()
                


if __name__ == "__main__":
    
    server = UpdateRestaurant(file = "../connection.txt")
    server.controller._connection_info()
    # 식당 크롤링
    print("****** INITIATING RESTAURANT CRAWLING *******")
    driver = webdriver.Chrome(executable_path = chromedriver_path, options = options)
    cnt = server.restaurant_information(driver)
    server.preprocessing()
    driver.close()
    print(f"****** {cnt} restaurants added {today}. ******")

    server.controller.curs.close()