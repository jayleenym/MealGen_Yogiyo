from base import *


crawl = DiningCode(file = "../connection.txt")
crawl.controller._connection_info()
errors = []
with tqdm(total = len(crawl.ADR) - 1117) as tm:
    i = 1117
    while i < len(crawl.ADR):
        adr = crawl.ADR[i]
        try:
            rtr_list = crawl.get_all_rtr(adr)
            if rtr_list == -1:
                i += 1
                break
            for r in rtr_list:
                crawl.get_one_info(r)
                crawl.get_one_menus()
                crawl.get_one_rvs()
                # 하나 크롤링 끝!
                crawl.driver.close()
            i += 1
            tm.update(1)
        except TimeoutException as ex:
            crawl.driver.quit()
            print(ex)
            crawl = DiningCode(file = "../connection.txt")
            print("********RECONNECT********")    

        except ElementClickInterceptedException as ec:
            time.sleep(5)
            crawl.driver.refresh()
        except Exception as e:
            print(e)
            # i += 100
            errors.append(adr)
            i += 1
            crawl.driver.quit()
            crawl = DiningCode(file = "../connection.txt")
            print("********RECONNECT********")   
pickle.dump(errors, open("./error_address.txt", "wb"))
