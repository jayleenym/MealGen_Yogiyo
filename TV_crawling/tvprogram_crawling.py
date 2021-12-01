from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import time
import datetime
import pandas as pd
from tqdm import tqdm
import re


DONG = pd.read_excel('./Report.xlsx', header = 1)['동'][2:]
DONG = DONG.drop(345).reset_index(drop = True)
# no_meaning = ["포장배달\n", "포장매장\n", '메뉴판 이미지로 보기\n', '사진\n', '대표\n', '배달의민족\n', '(대표메뉴)', '★대표메뉴★_']
KEYWORD = ['생방송투데이', '생생정보', '생방송오늘저녁', '생활의달인', '골목식당', '6시내고향', '모닝와이드', '전지적참견시점', '수요미식회', '맛있는녀석들']


def paging():
    try: 
        # 차례로 스크롤 내리기
        # NoSuchElement ; 조건에 맞는 업체가 없습니다 or scorll 최대
        for n in range(10, 50, 10):
            ELEMENT = driver.find_element_by_css_selector(f"#_pcmap_list_scroll_container > ul > li:nth-child({n})")
            actions = ActionChains(driver)
            actions.move_to_element(ELEMENT).perform()
    except:
        # print('스크롤 pass')
        pass
    return driver.find_elements_by_css_selector('#_pcmap_list_scroll_container > ul > li > div.Ow5Yt > a:nth-child(1)')


def crawling_one_page(final, lp, iframe):   
    pcmap_list = paging()
    if lp == pcmap_list:
        # print(dong, '마지막 페이지입니다.')
        return -1

    if (len(pcmap_list) == 0):
        # 조건에 맞는 업체가 없습니다
        # print(dong, '조건에 맞는 업체가 없습니다.')
        return -1

    for restaurant in pcmap_list:
        # 상세보기 클릭
        name = restaurant.text.replace('이미지 더 있음\n', "").split('\n')[0]
        # if name in FINAL.name.values:
            # return -1
        restaurant.click() 

        time.sleep(3)
        
        # 상세정보 frame(entryIframe) 들어가기
        driver.switch_to.parent_frame()
        entryIframe = driver.find_elements_by_tag_name("iframe")[-1]
        driver.switch_to.frame(entryIframe)
        # 상세정보 뽑아내기
        # detail = driver.find_element_by_css_selector('#app-root > div > div > div.place_detail_wrapper').text
        # category, address, phone, menu = "", "", "", ""
        try:
            category = driver.find_element_by_xpath('//*[@id="_title"]/span[2]').text
        except:
            # print()
            # pass
            category = ""
        
        try:
            driver.find_element_by_css_selector('a._1Gmk4').click()
            time.sleep(0.3)
            # address = driver.find_element_by_xpath('//*[@id="app-root"]/div/div/div[2]/div[5]/div/div[4]/div/ul/li[2]').text
            address = driver.find_elements_by_css_selector('div.TDq8t')[1]
            address = re.findall("지번(.*)\n", address.text)[0].strip()
        except:
            address = ""
        # try:
        #     # phone = driver.find_element_by_css_selector('//*[@id="app-root"]/div/div/div[2]/div[5]/div/div[4]/div/ul/li[1]').text
        #     phone = re.findall('[0-9]+[-][0-9]+[-]*[0-9]*', detail)[0]
        # except Exception as e:
        #     # print(e)
        #     pass
        
        # try:
        #     # menu = driver.find_element_by_xpath('//*[@id="app-root"]/div/div/div[2]/div[5]/div/div[5]').text
        #     menu = re.sub('[\n]주문수 [0-9]+', "", re.sub('별점[\n][0-9]', "", re.findall("\n메뉴[가-힇0-9]*\n(.*)\n메뉴더보기", detail, re.S)[0]))
        #     for _ in no_meaning : menu = menu.replace(_, "").strip()
        #     # print(name, detail)
        # except Exception as e:
        #     # print(e)
        #     pass

        # df 추가
        final = final.append({'name':name, 'address':address, 'category':category}, ignore_index=True)
        final.drop_duplicates(inplace = True, ignore_index = True)

        # searchIframe으로 이동
        driver.switch_to.parent_frame()
        try:
            driver.find_element_by_css_selector('#container > shrinkable-layout > div > app-base > search-layout > div.sub.ng-star-inserted > entry-layout > entry-close-button > button').click()
        except:
            pass
        
        driver.switch_to.frame(iframe)


if __name__ == "__main__":

    for key in KEYWORD:
        #  Chrome driver options
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # Path
        chromedriver_path = '/Users/yejin/Downloads/chromedriver'
        driver = webdriver.Chrome(executable_path = chromedriver_path, options = options)
        
        FINAL = pd.DataFrame(columns = ['name', 'category', 'address'])#, 'phone', 'menu'])
        
        for dong in tqdm(DONG):
            url = f'https://map.naver.com/v5/search/{dong}%20{key}'
            while True:
                try:
                    driver.get(url)
                    # 가게 리스트 frame(searchIframe)으로 변경
                    time.sleep(0.5)
                    searchIframe = driver.find_elements_by_tag_name("iframe")[-1]
                    driver.switch_to.frame(searchIframe)
                    last_page = []
                    while True:    
                        if crawling_one_page(FINAL, last_page, searchIframe) == -1:
                            break
                        last_page = paging()
                        # 한 페이지(최대 50개)까지 다 돌고 나면 다음 페이지 버튼
                        # pages = driver.find_elements_by_xpath('//*[@id="app-root"]/div/div[2]/div[2]/a')
                        # pages[-1].click()
                    break
                except:
                    time.sleep(0.2)
            # print(len(FINAL))
        
        FINAL.to_csv(f"../NaverMap/{key}_전체_지번주소.csv", index = False, sep = ';')
        driver.close()