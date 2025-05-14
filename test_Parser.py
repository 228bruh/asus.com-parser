import pytest
import random
from parse_page import Parser

@pytest.fixture(scope="module")
def all_links():
    return Parser().links

@pytest.fixture
def random_links(all_links):
    return random.sample(all_links, 3)


def test_links_exist(all_links):
    assert all_links, "Link list is empty"

def test_links_are_valid(all_links):
    assert all(link.startswith("https://www.laptopsdirect.co.uk/") for link in all_links), "Not all links start with the expected base URL"

def test_sync_parse_random_links(random_links):
    parser = Parser(links=random_links)
    results = parser.sync_parse()

    assert len(results) == 3
    for name, price in results:
        assert name != "Not found"
        assert price != "Not found"

def test_sync_parse_random_links_match(random_links):
    parser = Parser(links=random_links)
    results1 = parser.sync_parse()
    results2 = parser.sync_parse()
    assert results1 == results2

def test_async_parse_random_links(random_links):
    parser = Parser(links=random_links)
    results = parser.async_parse()

    assert len(results) == 3
    for name, price in results:
        assert name != "Not found"
        assert price != "Not found"

def test_async_parse_random_links_match(random_links):
    parser = Parser(links=random_links)
    results1 = parser.async_parse()
    results2 = parser.async_parse()
    assert results1 == results2

def test_sync_vs_async(random_links):
    parser = Parser(links=random_links)
    sync_results = parser.sync_parse()
    async_results = parser.async_parse()
    assert sync_results == async_results

invalidLinks = ["http://invalid.link", "https://fakelink.bruh", "qwert://dontwork.zxc",]
@pytest.mark.parametrize("link", invalidLinks)
def test_invalid_link_sync(link):
    parser = Parser(links=[link])
    result = parser.sync_parse()
    assert result == [["Not found", "Not found"]]

@pytest.mark.parametrize("link", invalidLinks)
def test_invalid_link_async(link):
    parser = Parser(links=[link])
    result = parser.async_parse()
    assert result == [["Not found", "Not found"]]
