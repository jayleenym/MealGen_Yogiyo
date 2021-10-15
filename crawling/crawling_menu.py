from requirements import *

class UpdateMenu():
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
                self.controller.insert(table_name = "menu_info", line = _menu)
                

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
        

if __name__ == "__main__":
    server = UpdateMenu(file = "../connection.txt")
    server.controller._connection_info()
    
    cnt = 0
    MENU = []
    q = "select distinct restaurant_id from restaurant_info;"
    server.controller.curs.execute(q)
    restaurants = list(list(zip(*server.controller.curs.fetchall()))[0]) 
    
    print("****** INITIATING MENU CRAWLING *******")
    print(f" - RESTAURANTS({today}) : {len(restaurants)}")
    for restaurant_id in tqdm(restaurants): 
        cnt += server.menu_information(restaurant_id, MENU)
        server.preprocess_menu()
    print(f"****** {cnt} menus updated {today}. ******")

    server.controller.curs.close()