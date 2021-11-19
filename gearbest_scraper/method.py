from .database import database
from . import scraper
from csv import writer
from tqdm import trange


class Method(scraper.Attributes, database.Connection):
    """ Request page ads """

    def to_csv(self):
        """ Append values related to 'catalog_table' sequence order
                'catalog_table' columns:
                    #1 id, #2 title
                    #3 link, #4 image
                    #5 price, #6 discount,
                    #7 price_tag, #8 review_rate,
                    #9 review_count, #10 search_id (foreign key) """
       
        with open(('catalog.csv' 
            if not self.conf['connection']['csv']['path'] 
            else self.conf['connection']['csv']['path']),
                'w', encoding='UTF-8', newline='') as file:
            
            csvfile_catalog = writer(file)                   
            csvfile_catalog.writerow(['id', 'title', 'link', 'image', 'price', 
                'discount', 'price_tag', 'review_rate', 'review_count'])
            
            for catalog in self.catalog_gen():
                csvfile_catalog.writerow(catalog)

    def scrape_pattern(self, url, keyword):
        """ Scrape pages based on url pattern """                           
        self.page_root_url = url
        
        # Fill search_table
        (self.sqlite_table_search(keyword) 
        if self.sqlite_enable else None)
        
        (self.mysql_table_search(keyword)
        if self.mysql_enable else None)
        
        for self.url_number in trange(self.page_count_all, desc=keyword):            
            # Fill catalog_table
            (self.sqlite_table_catalog()
            if self.sqlite_enable else None)
            
            (self.mysql_table_catalog()
            if self.mysql_enable else None)

            (self.to_csv()
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

