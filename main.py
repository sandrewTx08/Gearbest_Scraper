from os import chdir, path
from argparse import ArgumentParser
from json import load
from sqlite3 import connect
from tqdm import trange
from requests import get
from lxml.etree import HTML


class Gearbest_Scraper(object):

    def __init__(self, configuration_file, database):
        self.conf = configuration_file
        
        self.database = database
        self.cursor = self.database.cursor()

        self.stble = self.conf['database']['table_search']
        self.ctble = self.conf['database']['table_catalog']
        self.crtble = self.conf['database']['table_currency']

        self.cursor.execute(""" PRAGMA foreign_keys = 1; """)

        self.cursor.execute(f""" CREATE TABLE IF NOT EXISTS {self.crtble['name']}  (
                {self.crtble['id']} INTEGER PRIMARY KEY AUTOINCREMENT,
                {self.crtble['abbreviation']} TEXT
            ); """)
        
        self.cursor.execute(
            f""" CREATE TABLE IF NOT EXISTS {self.stble['name']} (
                    {self.stble['id']} INTEGER PRIMARY KEY AUTOINCREMENT,
                    {self.stble['keyword']} TEXT,
                    {self.stble['category']} TEXT,
                    {self.stble['pages_count']} INTEGER,
                    {self.stble['datetime']} TEXT,
                    {self.stble['currency_id']} TEXT,
                    
                    FOREIGN KEY ({self.stble['currency_id']})
                    REFERENCES {self.crtble['name']} ({self.crtble['id']})
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
        
        self.database.commit()

    def request(self, url):
        """ Return page object """
        page = get(url, params=self.conf['http_header'], timeout=120)
        
        if page.status_code == 200:
            return HTML(page.text)

    def table_search(self, search, reference_page): 

        if reference_page != None:

            try:
                page_count_all = int(reference_page.xpath(
                    '//footer/div[2]/div/a[last()-1]')[0].xpath('string()'))
            
            except IndexError:
                page_count_all = 0
                return page_count_all

            if page_count_all != 0:
                try:
                    search_category = reference_page.xpath(
                        '//div[@class="cateMain_asideSeachTitle"]/a[@title]'
                        )[0].get('title').replace("'", '').replace('"', '')

                except IndexError:
                    try:
                        search_category = reference_page.xpath(
                            '//div[@class="searchTitle_wrap"]/h1'
                            )[0].xpath('string()').replace("'", '').replace('"', '')
                    
                    except IndexError:
                        search_category = None

                currency = reference_page.xpath(
                    '//li[@id="js-btnShowShipto"]/span/span[2]')[0].xpath('string()')

                if search != None:
                    search_to_database = search.replace(
                        "'", '').replace('"', '')

                elif search == None:
                    search_to_database = None
                
                USD_NUM = 1

                currency_value = (
                    USD_NUM,
                    currency
                )
                
                self.cursor.execute(
                    f"""INSERT OR IGNORE INTO {self.crtble['name']} 
                        ({self.crtble['id']}, {self.crtble['abbreviation']}) 
                        VALUES (?,?); """, currency_value)

                search_items_value = (
                    search_to_database,
                    search_category,
                    page_count_all,
                    USD_NUM)
                
                self.cursor.execute(
                    f""" INSERT INTO {self.stble['name']} 
                        ({self.stble['keyword']}, 
                        {self.stble['category']},
                        {self.stble['pages_count']},
                        {self.stble['datetime']},
                        {self.stble['currency_id']})

                        VALUES(?,?,?,date('now'),?); """, search_items_value)
                
                return page_count_all

        elif reference_page == None:
            page_count_all = 0
            return page_count_all
    
    def table_catalog(self, catalog_list_box):
        """ Insert value from catalog ads """
        
        # List of catalog
        catalog_list = catalog_list_box.xpath(
            '//li[@data-goods-id]') 

        # Avaliable catalog on page
        catalog_count = range(len( 
            catalog_list_box.xpath(
                '//li[@data-goods-id]')))

        price=[
                float(catalog_list[i].get(
                    'data-shopprice'))
                for i in catalog_count
            ]
        
        id=[
                catalog_list[i].get(
                    'data-goods-id')
                for i in catalog_count
            ]
        
        image=[
                catalog_list[i].xpath(
                    '//a[@data-img]/img[@data-lazy]')[i].get('data-lazy')
                    .replace("'", '').replace('"', '')
                for i in catalog_count
            ]
        
        title=[
                catalog_list[i].xpath(
                    '//div[@class="gbGoodsItem_outBox"]/p/a')[i].get('title')
                    .replace("'", '').replace('"', '')
                for i in catalog_count
            ]
        
        link=[
                catalog_list[i].xpath(
                    '//div[@class="gbGoodsItem_outBox"]/p/a')[i].get('href')
                    .replace("'", '').replace('"', '')
                for i in catalog_count
            ]
        
        discount=[
                int(catalog_list[i].find(
                    'span/strong').xpath('string()'))
                if catalog_list[i].find(
                    'span/strong') != None
                else None
                for i in catalog_count
            ]
        
        review_rate=[
                float(catalog_list[i].find(
                    'div/div[2]/span/span[2]').xpath('string()'))
                if catalog_list[i].find(
                    'div/div[2]/span/span[2]') != None
                else None
                for i in catalog_count
            ]
        
        review_count=[
                int(catalog_list[i].xpath(
                    '//li[@data-goods-id]')[i].find(
                        'div/div[2]/span/span[3]').xpath('string()')
                    .replace('(', '')
                    .replace(')', ''))
                if catalog_list[i].find(
                    'div/div[2]/span/span[3]') != None
                else None
                for i in catalog_count
            ]
        
        price_tag=[
                catalog_list[i].find(
                    'div/div[1]/a/span').get('title')
                    .replace('Warehouse', '')
                    .replace("'", '').replace('"', '')
                if catalog_list[i].find('div/div[1]/a/span') != None
                else catalog_list[i].find('div/div[1]/span').xpath('string()')
                if catalog_list[i].find('div/div[1]/span') != None
                else None
                for i in catalog_count
            ]

        last_id = self.cursor.execute(
            f""" SELECT MAX ({self.stble['id']})
                FROM {self.stble['name']}; """).fetchone()[0]


        def catalog_list():
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
                    last_id)

        for catalog in catalog_list():
            self.cursor.execute(
                f""" INSERT INTO {self.ctble['name']}  
                    VALUES (?,?,?,?,?,?,?,?,?,?); """, catalog)

    def link_generator(self, page_menu):
        
        for parent_link in page_menu.xpath(
            '//li[@class="headCate_item"]/a[@class="headCate_itemName"]'):
            
            yield parent_link.get('href')
        
        for child_link in page_menu.xpath(
            '//li[@class="headCate_item"]/div//a[@class="headCate_childName"]'):
            
            yield child_link.get('href')
    
    def scrape_by_search_bar(self, search):
        """ Access page by its page number
            Insert catalog information into database
            """

        search_to_url = search.replace(" ", "-")

        # Page used to refer primary values
        reference_page = self.request(
            'https://www.gearbest.com/sale/{}?page_size=120?odr=relevance'
            .format(search_to_url))

        table_search_page_count_all = self.table_search(
            search,
            reference_page)

        for page_number in trange(table_search_page_count_all, colour='WHITE', desc=search):

            page_with_number = self.request(
                'https://www.gearbest.com/sale/{}/{}.html?page_size=120?odr=relevance'
                .format(search_to_url, page_number + 1))
            
            if page_with_number != None:
                
                catalog_list_box = page_with_number.xpath(
                    '//ul[@class="clearfix js_seachResultList"]')[0]

            # Break loop if any catalog is not found
            if not catalog_list_box.find('li[@data-goods-id]') == None:
                self.table_catalog(catalog_list_box)
        
            else:
                break
        
        self.database.commit()
        
    def scrape_by_link_generator(self):
        
        # Page used to refer primary values
        page_menu = self.request(
            'https://www.gearbest.com/')

        for url in self.link_generator(page_menu):

            reference_page = self.request(
                '{}?page_size=120?odr=relevance'
                .format(url))
            
            table_search_page_count_all = self.table_search(
                None,
                reference_page)

            for page_number in trange(table_search_page_count_all, colour='WHITE', desc=url):
         
                page_with_number = self.request('{}{}.html?page_size=120?odr=relevance'
                .format(url, page_number + 1))

                if not page_with_number == None:
                    
                    catalog_list_box = page_with_number.xpath(
                        '//ul[@class="clearfix js_seachResultList"]')[0]

                # Break loop if any catalog is not found
                if not catalog_list_box.find('li[@data-goods-id]') == None:
                    self.table_catalog(catalog_list_box)

                else:
                    break

            self.database.commit()


def run(path, mode):   
    """ Loading configuration from file 
    Execute the Gearbest_Scraper
    """

    def configuration(path):
        try:
            config = load(open(path))

        except FileNotFoundError:
            chdir(path.dirname(path.abspath(__file__)))
            config = load(open(path))

        return config
    
    config = configuration(path)
    database = connect(config['database']['name'])   
    scraper = Gearbest_Scraper(config, database)
    
    if mode == 'search' or mode.startswith('s'):
        for search in config['search_list']:
            scraper.scrape_by_search_bar(search)       

    if mode == 'link' or mode.startswith('l'):
        scraper.scrape_by_link_generator()
    
    database.close()


def main():

    parser = ArgumentParser()

    parser.add_argument('--mode', type=str, default='search', 
    help='choose a method to Gearbest_Scraper')
    parser.add_argument('--config', type=str, default='configuration.json', 
    help='configuration file ex: configuration.json')

    args = parser.parse_args()

    run(args.config, args.mode)


if __name__ == '__main__':
    main()

