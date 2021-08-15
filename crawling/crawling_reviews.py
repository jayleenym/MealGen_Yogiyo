from update_db import *

server = UpdateMealgen(file = "connection.txt")
server.controller._connection_info()

# daily crawling
server.crawl_review(input("시작 날짜('0000-00-00'): "))