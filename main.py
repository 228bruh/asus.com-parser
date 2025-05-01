from parse_page import Parser
from db_manager import DatabaseManager

parser = Parser()
products = parser.asyns_parse()

db = DatabaseManager()
db.insert_parsing_results(products)

db.close()