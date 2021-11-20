from .database import database
from . import scraper
from csv import writer
from tqdm import trange


class CSV(object):
    csv_open_catalog = False
    csv_open_search = False
    
    def csv_catalog_init(self):
        """ Append values related to 'catalog_table' sequence order
                    'catalog_table' columns:
                        #1 id, #2 title
                        #3 link, #4 image
                        #5 price, #6 discount,
                        #7 price_tag, #8 review_rate,
                        #9 review_count, #10 search_id (foreign key) """
        
        if self.conf['connection']['csv']['enable']:
            self.csv_open_catalog = True
            
            self.csvfile_catalog = writer(open('catalog.csv',
                'w', encoding='UTF-8', newline=''))
            
            self.csvfile_catalog.writerow(['id', 'title', 'link', 'image', 'price', 
                'discount', 'price_tag', 'review_rate', 'review_count'])

    def csv_search_init(self):
        
        if self.conf['connection']['csv']['enable']:
            self.csv_open_search = True

            self.csvfile_search = writer(open('search.csv',
                'w', encoding='UTF-8', newline=''))
            
            self.csvfile_search.writerow(['keyword', 
                'category', 'pages_count'])

    def to_csv_search(self):
        if not self.csv_open_search:
            self.csv_search_init()
        
        else: self.csvfile_search.writerow(self.search_values)
    
    def to_csv_catalog(self):            
        if not self.csv_open_catalog:
            self.csv_catalog_init()
        
        else:
            for catalog in self.catalog_gen():
                self.csvfile_catalog.writerow(catalog)

class Method(CSV, scraper.Attributes, database.Connection):
    """ Request page ads """  
 
    def scrape_pattern(self, url, keyword):
        """ Scrape pages based on url pattern """                           
        self.page_root_url = url
        self.keyword = keyword
        
        # Fill search_table
        (self.sqlite_table_search() 
        if self.sqlite_enable else None)
        
        (self.mysql_table_search()
        if self.mysql_enable else None)
        
        (self.to_csv_search()
            if self.conf['connection']['csv']['enable'] else None)

        for self.url_number in trange(self.page_count_all, desc=self.keyword):            
            # Fill catalog_table
            (self.sqlite_table_catalog()
            if self.sqlite_enable else None)
            
            (self.mysql_table_catalog()
            if self.mysql_enable else None)

            (self.to_csv_catalog()
            if self.conf['connection']['csv']['enable'] else None)

    def scrape_by_search_bar(self):
        for search in self.conf['method']['search']['list']:
            # Page used to refer primary values
            url = 'https://www.gearbest.com/sale/{}/'.format(search)
            self.scrape_pattern(url, search)

    def scrape_by_link_url(self):
        # Page used to refer primary values
        for values in self.link_gen():
            self.scrape_pattern(values[0], values[1])      

    def scrape_by_popular_searches(self):
        # Page used to refer primary values
        for values in self.popular_searches_gen():
            self.scrape_pattern(values[0], values[1])

