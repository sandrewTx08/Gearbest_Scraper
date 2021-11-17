from argparse import ArgumentParser
from gearbest_scraper import method


def main():
    parser = ArgumentParser()
    parser.add_argument('--mode', default='search')
    parser.add_argument('--conf', default='configuration.json')
    args = parser.parse_args()
    
    m = method.Method(args.conf)
    if args.mode == 'search': 
        assert m.conf['method']['search']['enable']
        m.scrape_by_search_bar()
    elif args.mode == 'link': 
        assert m.conf['method']['link']['enable']
        m.scrape_by_link_url()
    elif args.mode == 'popular': 
        assert m.conf['method']['popular']['enable']
        m.scrape_by_popular_searches()
    
    # Close connections
    if m.sqlite_enable: m.sqlite_cursor.close(), m.sqlite_database.close()
    if m.mysql_enable: m.mysql_cursor.close(), m.mysql_database.close()


if __name__ == '__main__':
    main()

