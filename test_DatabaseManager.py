import pytest
import random
from parse_page import Parser
from db_manager import DatabaseManager

@pytest.fixture(scope="module")
def parser():
    return Parser()

@pytest.fixture(scope="module")
def products(parser):
    return parser.async_parse()

@pytest.fixture
def db_with_data(products):
    db = DatabaseManager(":memory:")
    db.insert_parsing_results(products)
    return db

def test_selection_inserted(db_with_data, products):
    selections = db_with_data.get_selections()
    assert selections, "No selections found"
    
    productsCount = selections[0][2]
    assert productsCount == len(products), "Stored products count dont match with expected products count"

def test_products_stored_correctly(db_with_data, products):
    storedProducts = db_with_data.get_products_by_selecID(1)
    expected = [(1, name, price) for name, price in products]

    assert storedProducts == expected, "Stored products dont match with expected products"

def test_compare_randomLinks_with_db(parser, db_with_data):
    allLinks = parser.links
    randomIndices = random.sample(range(len(allLinks)), 3)
    randomLinks = [allLinks[i] for i in randomIndices]

    parsedSubset = Parser(links=randomLinks).async_parse()
    parsedSubset = [tuple(p) for p in parsedSubset]

    storedProducts = db_with_data.get_products_by_selecID(1)
    storedSubset = [storedProducts[i] for i in randomIndices]
    storedSubsetCleaned = [(name, price) for _, name, price in storedSubset]

    assert parsedSubset == storedSubsetCleaned, "Parsed links dont match stored products in DB"

