from sys import argv
from gearbest_scraper import method as mt


def main():
    method = mt.Method(argv[1])
    if argv[2] == 'search': method.scrape_by_search_bar()       
    elif argv[2] == 'link': method.scrape_by_link_url()
    elif argv[2] == 'popular': method.scrape_by_popular_searches()
    method.database.close() 


if __name__ == '__main__':
    main()

