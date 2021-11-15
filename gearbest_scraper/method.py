from .database import database
from . import scraper
from tqdm import trange


class Method(scraper.Attributes, database.Connection):
    """ Request page ads """
    
    def scrape_pattern(self, url, keyword):
        """ Scrape pages based on url pattern """               
        self.page_root_url = url
                
        if self.page_count_all != 0 or None:           
            self.table_search(keyword)  # search_table
            for url_number in trange(self.page_count_all, desc=keyword):
                self.page_ads_url = self.url_pattern.format(url, url_number + 1)
                self.table_catalog()  # catalog_table

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


def run(path, mode):   
    """ Execute the Gearbest_Scraper """
    method = Method(path)
    
    if mode == 'search' or mode.startswith('s'):
        # >> python --mode search
        assert method.conf['method']['search']['enable'] == True
        method.scrape_by_search_bar()      

    elif mode == 'link' or mode.startswith('l'):
        # >> python --mode link
        assert method.conf['method']['link']['enable'] == True
        method.scrape_by_link_url()
    
    elif mode == 'popular' or mode.startswith('p'):
        # >> python --mode popular
        assert method.conf['method']['popular']['enable'] == True
        method.scrape_by_popular_searches()

    method.database.close() 