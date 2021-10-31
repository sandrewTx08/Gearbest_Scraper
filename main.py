from os import chdir, path
from json import load
from sqlite3 import connect
from tqdm import trange
from requests import get
from lxml.etree import HTML


class Gearbest_Scraper(object):

    def __init__(self, configuration_file, database):
        self.conf = configuration_file
            
        self.cursor = database.cursor()
        
        self.stble = self.conf['database']['table_search']
        self.ctble = self.conf['database']['table_catalog']

        self.cursor.execute(""" PRAGMA foreign_keys = 1; """)
        
        self.cursor.execute(
            f""" CREATE TABLE IF NOT EXISTS {self.stble['name']} (
                    {self.stble['id']} INTEGER PRIMARY KEY AUTOINCREMENT,
                    {self.stble['keyword']} TEXT NOT NULL,
                    {self.stble['category']} TEXT,
                    {self.stble['currency']} TEXT,
                    {self.stble['pages_count']} INTEGER,
                    {self.stble['datetime']} TEXT
                ); """)
        
        self.cursor.execute(
            f""" CREATE TABLE IF NOT EXISTS {self.ctble['name']} (
                    {self.ctble['id']} TEXT NOT NULL,
                    {self.ctble['title']} TEXT NOT NULL,
                    {self.ctble['link']} TEXT NOT NULL,
                    {self.ctble['image']} TEXT,
                    {self.ctble['price']}  REAL NOT NULL,
                    {self.ctble['discount']}  INTEGER,
                    {self.ctble['price_tag']}  TEXT,
                    {self.ctble['review_rate']}  REAL,
                    {self.ctble['review_count']}  INTEGER,
                    {self.ctble['search_id']} INTEGER,
                    
                    FOREIGN KEY ({self.ctble['search_id']})
                    REFERENCES {self.stble['name']} (id)
                ); """)

    def request(self, url):
        """ Return page object """
        page = get(url, params=self.conf['http_header'])
        
        if page.status_code == 200:
            return HTML(page.text)
    
    def table_search_name(self, search_to_database, search_category, currency, pages_count_all): 
        
        search_items_value = (
            search_to_database,
            search_category,
            currency,
            pages_count_all)
        
        self.cursor.execute(
        f""" INSERT INTO {self.stble['name']} 
            ({self.stble['keyword']}, 
            {self.stble['category']},
            {self.stble['currency']},
            {self.stble['pages_count']},
            {self.stble['datetime']})
            
            VALUES(?,?,?,?,date('now')); """, search_items_value)

    def table_catalog_name(self, catalogs_list, catalog_count):
        
        for its in self.catalog_list(catalogs_list ,catalog_count):
            self.cursor.execute(
                f""" INSERT INTO {self.ctble['name']}  
                    VALUES (?,?,?,?,?,?,?,?,?,?); """, its)

    def get_last_id(self):
        return self.cursor.execute(
            f""" SELECT MAX ({self.stble['id']})
                FROM {self.stble['name']}; """).fetchone()[0]

    def catalog_list(self, catalogs_list, catalog_count):    
        """ Return value from catalog ads """

        price=[
                float(catalogs_list[i].get(
                    'data-shopprice'))
                for i in catalog_count
            ]
        
        id=[
                catalogs_list[i].get(
                    'data-goods-id')
                for i in catalog_count
            ]
        
        image=[
                catalogs_list[i].xpath(
                    '//a[@data-img]/img[@data-lazy]')[i].get('data-lazy')
                    .replace("'", '').replace('"', '')
                for i in catalog_count
            ]
        
        title=[
                catalogs_list[i].xpath(
                    '//div[@class="gbGoodsItem_outBox"]/p/a')[i].get('title')
                    .replace("'", '').replace('"', '')
                for i in catalog_count
            ]
        
        link=[
                catalogs_list[i].xpath(
                    '//div[@class="gbGoodsItem_outBox"]/p/a')[i].get('href')
                    .replace("'", '').replace('"', '')
                for i in catalog_count
            ]
        
        discount=[
                int(catalogs_list[i].find(
                    'span/strong').xpath('string()'))
                if catalogs_list[i].find(
                    'span/strong') != None
                else None
                for i in catalog_count
            ]
        
        review_rate=[
                float(catalogs_list[i].find(
                    'div/div[2]/span/span[2]').xpath('string()'))
                if catalogs_list[i].find(
                    'div/div[2]/span/span[2]') != None
                else None
                for i in catalog_count
            ]
        
        review_count=[
                int(catalogs_list[i].xpath(
                    '//li[@data-goods-id]')[i].find(
                        'div/div[2]/span/span[3]').xpath('string()')
                    .replace('(', '')
                    .replace(')', ''))
                if catalogs_list[i].find(
                    'div/div[2]/span/span[3]') != None
                else None
                for i in catalog_count
            ]
        
        price_tag=[
                catalogs_list[i].find(
                    'div/div[1]/a/span').get('title')
                    .replace('Warehouse', '')
                    .replace("'", '').replace('"', '')
                if catalogs_list[i].find('div/div[1]/a/span') != None
                else catalogs_list[i].find('div/div[1]/span').xpath('string()')
                if catalogs_list[i].find('div/div[1]/span') != None
                else None
                for i in catalog_count
            ]

        for i in catalog_count:       
            yield (
                    id[i], 
                    title[i],
                    link[i],
                    image[i],
                    price[i],
                    discount[i],
                    price_tag[i],
                    review_rate[i],
                    review_count[i],
                    self.get_last_id()
                )

    def scrape_catalog_by_search_bar(self, search):
        """ Access page by its page number
            Insert catalog information into database
            """
        
        search_to_url = search.replace(" ", "-")
        search_to_database = search.replace("'", '').replace('"', '')
        
        # Page used to refer primary values
        reference_page = self.request(
            'https://www.gearbest.com/sale/{}?page_size=120?odr=relevance'
            .format(search_to_url))
        
        search_category = reference_page.xpath(
            '//div[@class="cateMain_asideSeachTitle"]/a[@title]'
            )[0].get('title').replace("'", '').replace('"', '')
        
        pages_count_all = int(reference_page.xpath(
            '//footer/div[2]/div/a[last()-1]')[0].xpath('string()'))
        
        currency = reference_page.xpath(
            '//li[@id="js-btnShowShipto"]/span/span[2]')[0].xpath('string()')

        self.table_search_name(
            search_to_database,
            search_category,
            currency,
            pages_count_all)

        for page_number in trange(pages_count_all, colour='WHITE', desc=f'{search}'):
            
            catalog_list_items = self.request(
                'https://www.gearbest.com/sale/{}/{}.html?page_size=120?odr=relevance'
                .format(search_to_url, page_number + 1)).xpath(
                    '//ul[@class="clearfix js_seachResultList"]')[0]
            
            # Break loop if any catalog is not found
            if not catalog_list_items.find('li[@data-goods-id]') == None:
                
                catalogs_list = catalog_list_items.xpath(
                    '//li[@data-goods-id]') # List of catalog
                
                catalog_count = range(len( # Avaliable catalog on page
                    catalog_list_items.xpath(
                        '//li[@data-goods-id]')))

                self.table_catalog_name(
                    catalogs_list,
                    catalog_count
                    )
        
            else:
                break
  

def run(configuration_path):   
    """ Loading configuration from file 
    Execute the Gearbest_Scraper
    """
    try:
        config = load(open(configuration_path))

    except FileNotFoundError:
        chdir(path.dirname(path.abspath(__file__)))
        config = load(open(configuration_path))

    database = connect(config['database']['name'])   
    scraper = Gearbest_Scraper(config, database)

    for search in config['search_list']:
        scraper.scrape_catalog_by_search_bar(search)       
        database.commit()
    
    database.close()


def main():
    run('configuration.json')


if __name__ == '__main__':
    main()

