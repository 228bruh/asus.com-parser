from parse_page import Parser
import time

parser = Parser()

startTime = time.time()

# products = parser.syns_parse()
# for product in products:
#     print(product)

products = parser.asyns_parse()
for p in products:
    print(p)

finishTime = time.time()
print(finishTime - startTime)
print(len(products))