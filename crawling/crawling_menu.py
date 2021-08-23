from update_db import *

server = UpdateCrawling(file = "../connection.txt")
server.controller._connection_info()

# daily crawling
server.crawl_menu()
