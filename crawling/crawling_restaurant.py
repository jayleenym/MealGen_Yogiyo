from update_db import *

server = UpdateMealgen(file = "connection.txt")
server.controller._connection_info()

# daily crawling
server.crawl_restaurant()