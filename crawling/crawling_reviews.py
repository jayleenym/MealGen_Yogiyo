from requirements import *


class UpdateReviews():
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
           

    def reviews(self, restaurant_id, REVIEWS, yesterday = yesterday):
        # 리뷰어 이름 재설정
        rtr = pd.read_sql(f'SELECT sido, sigungu FROM restaurant_info WHERE restaurant_id = {restaurant_id};', self.controller.conn)

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

            q = f"SELECT count(*) FROM reviews WHERE review_id = {rev['id']} AND written_time = '{rev['time']}';"
            self.controller.curs.execute(q)
            result = self.controller.curs.fetchone()
            if result[0] > 0: # 중복 제거
                r += 1
                continue

            try:
                m_id = rev['menu_items']['id']
            except:
                m_id = -1
            
            # yesterday (변경가능) ~ today까지
            # if (rev['time'] >= yesterday) and (rev['time'] < today):
            if (rev['time'] < today):
                nickname = rev['nickname'].replace("'", "").strip()
                user_name = rtr.sido.iloc[0][:2].strip() + rtr.sigungu.iloc[0].strip() + nickname
                # user_id 배정
                iq = f"SELECT user_id FROM user_info WHERE user_name = '{user_name}';"
                self.controller.curs.execute(iq)
                info = self.controller.curs.fetchone()
                if not info:
                    self.controller.insert('user_info', 
                                            {"user_name": user_name,
                                             'sido': rtr.sido.iloc[0],
                                             'sigungu' : rtr.sigungu.iloc[0]}
                                             )
                    self.controller.conn.commit()
                    
                    uq = f"SELECT count(*) FROM user_info;"
                    self.controller.curs.execute(uq)
                    user_id = self.controller.curs.fetchone()[0]
                else:
                    user_id = info[0]
                # review 파일 만들기
                review = {
                          'written_time' : rev['time'],
                          'nickname' : nickname, # ' 있으면 오류
                          'user_name' : user_name,
                          'user_id' : user_id,
                          'review_id' : rev['id'],
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
                # int64 type error
                json.dump(REVIEWS, open(f'./reviews_{yesterday}_{today}.json', 'w'), ensure_ascii = False, indent = '\t')
                self.controller.insert(table_name = "reviews", line = review)
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
            # menu_id update
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

    def fill_extra(self, resid):
        rev_menu = pd.read_sql(f'SELECT menu, review_id FROM reviews WHERE menu_id = -1 AND restaurant_id = {resid};', self.controller.conn)
        rev_menu.menu = rev_menu.menu.apply(lambda x: re.findall('(.*?)/[0-9]+', x)[0].strip())
        menu = pd.read_sql(f'SELECT menu_id, name as menu FROM menu_info WHERE restaurant_id = {resid};', self.controller.conn)
        ids = pd.merge(rev_menu, menu, how = 'left', on = 'menu')
        ids = ids[ids.menu_id.notnull()]

        tmp = list(map(tuple, ids[['menu_id', 'review_id']].values))
        self.controller.curs.executemany("UPDATE reviews SET menu_id = %s, updated_at = now() WHERE review_id = %s", tmp)
        self.controller.conn.commit()



if __name__ == "__main__":
    server = UpdateReviews(file = "../connection.txt")
    server.controller._connection_info()

    sdate = input('리뷰 시작 날짜(yyyy-mm-dd): ')
    cnt = 0
    REV = []

    q = "select distinct restaurant_id from restaurant_info;"
    server.controller.curs.execute(q)
    restaurants = list(list(zip(*server.controller.curs.fetchall()))[0]) 
    # 리뷰 크롤링 시작
    print("****** INITIATING REVIEW CRAWLING *******")
    print(f" - RESTAURANTS({today}) : {len(restaurants)}")
    for restaurant_id in tqdm(restaurants):       
        cnt += server.reviews(restaurant_id, REV, yesterday = sdate)
        server.preprocess_rev()
        server.fill_extra(restaurant_id)
    print(f"****** {cnt} reviews updated {sdate} ~ {today}. ******")