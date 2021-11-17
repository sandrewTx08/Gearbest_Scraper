from .database import database
from . import scraper
from tqdm import trange


class Method(scraper.Attributes, database.Connection):
    """ Request page ads """
    
    def scrape_pattern(self, url, keyword):
        """ Scrape pages based on url pattern """               
        self.page_root_url = url
                
        if self.page_count_all != 0 or None:           
            
            # Fill search_table
            (self.sqlite_table_search(keyword) 
            if self.sqlite_enable else None)
            
            (self.mysql_table_search(keyword)
            if self.mysql_enable else None)
            
            for url_number in trange(self.page_count_all, desc=keyword):
                # Defining page with ad by URL pattern
                self.page_ads_url = self.url_pattern.format(url, url_number + 1)
                
                # Fill catalog_table
                (self.sqlite_table_catalog()
                if self.sqlite_enable else None)
                
                (self.mysql_table_catalog()
                if self.mysql_enable else None)

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

