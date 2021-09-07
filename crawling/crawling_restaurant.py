from update_crawling import *

server = UpdateCrawling(file = "../connection.txt")
server.controller._connection_info()

# daily crawling
server.crawl_restaurant()
