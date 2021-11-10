from os import chdir, path as sys_path
from tqdm import trange
from lxml.etree import HTML
from json import load
from sqlite3 import connect
import requests


class Attributes(object):
    """ Page objects """
    
    @property
    def page_count_all(self):           
        if self.page_root != None:
            try:
                return int(self.page_root.xpath(
                    '//footer/div[2]/div/a[last()-1]')[0].xpath('string()'))

            except IndexError:
                return 0
        else:
            return 0
    
    @property
    def currency(self):
        try:
            return self.page_root.xpath(
                '//li[@id="js-btnShowShipto"]/span/span[2]')[0].xpath('string()')
        
        except IndexError:
            return None

    @property
    def search_category(self):
        if self.page_count_all != 0:
            try:
                return self.page_root.xpath(
                    '//div[@class="cateMain_asideSeachTitle"]/a[@title]'
                    )[0].get('title').replace("'", '').replace('"', '')

            except IndexError:
                try:
                    return self.page_root.xpath(
                        '//div[@class="searchTitle_wrap"]/h1'
                        )[0].xpath('string()').replace("'", '').replace('"', '')

                except IndexError:
                    return None 

    def catalog(self, page):
        """ Scrape catalog ads """
        page = self.request(page)
        
        if page != None:
            # Catalog list parent element
            catalog_list_box = page.xpath(
                '//ul[@class="clearfix js_seachResultList"]')[0]

            if catalog_list_box.find('li[@data-goods-id]') != None:
                # Catalog list children elements
                catalog_list = catalog_list_box.xpath(
                    '//li[@data-goods-id]') 

                # Avaliable catalog on page
                catalog_count = range(len( 
                    catalog_list_box.xpath(
                        '//li[@data-goods-id]')))

                price = [ float(catalog_list[i].get(
                            'data-shopprice'))
                        for i in catalog_count ]
                
                id = [ catalog_list[i].get(
                            'data-goods-id')
                        for i in catalog_count ]
                        
                image = [ catalog_list[i].xpath(
                            '//a[@data-img]/img[@data-lazy]'
                                )[i].get('data-lazy')
                                    .replace("'", '')
                                    .replace('"', '')
                        for i in catalog_count ]
            
                title = [ catalog_list[i].xpath(
                            '//div[@class="gbGoodsItem_outBox"]/p/a'
                                )[i].get('title')
                                    .replace("'", '')
                                    .replace('"', '')
                        for i in catalog_count ]
                
                link = [ catalog_list[i].xpath(
                        '//div[@class="gbGoodsItem_outBox"]/p/a'
                            )[i].get('href')
                                .replace("'", '')
                                .replace('"', '')
                        for i in catalog_count ]
                
                discount = [ int(catalog_list[i].find('span/strong').xpath('string()'))
                            if catalog_list[i].find('span/strong') != None
                            else None
                        for i in catalog_count ]
                
                review_rate = [ float(catalog_list[i].find(
                            'div/div[2]/span/span[2]').xpath('string()'))
                        if catalog_list[i].find(
                            'div/div[2]/span/span[2]') != None
                        else None
                        for i in catalog_count ]
                
                review_count = [ int(catalog_list[i].xpath(
                            '//li[@data-goods-id]')[i].find(
                                'div/div[2]/span/span[3]').xpath('string()')
                            .replace('(', '')
                            .replace(')', ''))
                        if catalog_list[i].find(
                            'div/div[2]/span/span[3]') != None
                        else None
                        for i in catalog_count ]
                
                price_tag = [
                        catalog_list[i].find(
                            'div/div[1]/a/span').get('title')
                            .replace('Warehouse', '')
                            .replace("'", '')
                            .replace('"', '')
                        if catalog_list[i].find('div/div[1]/a/span') != None
                        else catalog_list[i].find('div/div[1]/span').xpath('string()')
                        if catalog_list[i].find('div/div[1]/span') != None
                        else None
                        for i in catalog_count ]

                for i in catalog_count:       
                    """ Append values related to 'table_catalog' sequence order
                        'table_catalog' columns:
                            1. id
                            2. title
                            3. link
                            4. image
                            5. price
                            6. discount
                            7. price_tag
                            8. review_rate
                            9. review_count
                            10. search_id (foreign key) """
                    
                    yield [ id[i], title[i], link[i], 
                            image[i], price[i], discount[i], 
                            price_tag[i], review_rate[i], 
                            review_count[i] ]
       
    def link_generator(self, page):
        page = self.request(page)
        
        for link in page.xpath(
            '//ul[@class="headCate"]/li[@class="headCate_item"]//*[@href]'):
           
           yield (link.get('href'), link.xpath('string()'))  

    def popular_searches(self, page):
        page = self.request(page)
        
        for link in page.xpath(
            '//li[@class="footerHotkey_item"]/a'):
            
            yield (link.get('href'), link.xpath('string()'))


class Database(Attributes):
    """ Database handler """

    def __init__(self, path):
        # Load configuration file
        try:
            self.conf = load(open(path))

        except FileNotFoundError:
            chdir(sys_path.dirname(sys_path.abspath(__file__)))
            self.conf = load(open(path))

        self.database = connect(self.conf['database']['name'])
        self.cursor = self.database.cursor()

        self.stble = self.conf['database']['table_search']
        self.ctble = self.conf['database']['table_catalog']
        self.crtble = self.conf['database']['table_currency']

        # Enable foreign keys
        self.cursor.execute(""" PRAGMA foreign_keys = 1 ; """)

        self.cursor.execute(f""" CREATE TABLE IF NOT EXISTS {self.crtble['name']} (
                {self.crtble['id']} INTEGER PRIMARY KEY AUTOINCREMENT,
                {self.crtble['abbreviation']} TEXT ); """)

        self.cursor.execute(
            f""" CREATE TABLE IF NOT EXISTS {self.stble['name']} (
                {self.stble['id']} INTEGER PRIMARY KEY AUTOINCREMENT,
                {self.stble['keyword']} TEXT,
                {self.stble['category']} TEXT,
                {self.stble['pages_count']} INTEGER,
                {self.stble['datetime']} TEXT,
                {self.stble['currency_id']} TEXT,

                FOREIGN KEY ({self.stble['currency_id']})
                REFERENCES {self.crtble['name']} ({self.crtble['id']}) ); """)

        self.cursor.execute(
            f""" CREATE TABLE IF NOT EXISTS {self.ctble['name']} (
                {self.ctble['id']} TEXT NOT NULL,
                {self.ctble['title']} TEXT NOT NULL,
                {self.ctble['link']} TEXT NOT NULL,
                {self.ctble['image']} TEXT,
                {self.ctble['price']} REAL NOT NULL,
                {self.ctble['discount']} INTEGER,
                {self.ctble['price_tag']} TEXT,
                {self.ctble['review_rate']} REAL,
                {self.ctble['review_count']} INTEGER,
                {self.ctble['search_id']} INTEGER,

                FOREIGN KEY ({self.ctble['search_id']})
                REFERENCES {self.stble['name']} ({self.stble['id']}) ); """)

        self.database.commit()
    
    @property
    def currency_id(self):
        """ Query last id from currency table """
        currency_id = self.cursor.execute(  
            f""" SELECT MAX({self.crtble['id']}), {self.crtble['abbreviation']} 
                FROM {self.crtble['name']} 
                WHERE {self.crtble['abbreviation']} LIKE '{self.currency}'; """).fetchone()

        # Create a currency id if not exist
        if currency_id[0] == None:
            self.cursor.execute(
                f""" INSERT INTO {self.crtble['name']} 
                    ({self.crtble['id']},{self.crtble['abbreviation']}) 
                    VALUES (?,?); """, (None, self.currency))
            return 1

        elif currency_id[1] == self.currency:
            return currency_id[0]
    
    def table_search(self, keyword):        
        if self.page_count_all != 0:
            
            keyword_to_database = (
                keyword
                    .replace("'", '')
                    .replace('"', '')
                if keyword != None
                else None)
            
            values = (
                keyword_to_database,
                self.search_category,
                self.page_count_all,
                self.currency_id)

            self.cursor.execute(
                f""" INSERT INTO {self.stble['name']} 
                    ({self.stble['keyword']}, 
                    {self.stble['category']},
                    {self.stble['pages_count']},
                    {self.stble['datetime']},
                    {self.stble['currency_id']})

                    VALUES (?,?,?,date('now'),?); """, values)
            
            self.database.commit()

    def table_catalog(self, page_with_catalog):
        # Provide last id from 'table_search'
        last_id = [ int(self.cursor.execute(
                f""" SELECT MAX ({self.stble['id']})
                    FROM {self.stble['name']}; """).fetchone()[0]) ]

        for catalog in self.catalog(page_with_catalog):           
            # Concat catalog with last id as tuple
            catalog_concat = tuple(catalog) + tuple(last_id) 
            
            self.cursor.execute(
                f""" INSERT INTO {self.ctble['name']}  
                    VALUES (?,?,?,?,?,?,?,?,?,?); """, catalog_concat)


class Method(Database):
    """ Request page ads """
    session = requests.Session()

    def request(self, url):
        """ Return page object """
        url_check = (url.startswith('http://') 
                    or url.startswith('https://') 
                    or url.startswith('www.'))
        if url_check:
            try:
                page = self.session.get(url, 
                    timeout=120,
                    params=self.conf['http_header'])
            except:
                return None
            
            if page.status_code == 200:
                page_object = HTML(page.text)
                if page_object != None: return page_object 
                else: return None 
        else:
            return None

    def scrape_pattern(self, url, keyword):
        """ Scrape pages based on url pattern """
        self.page_root = self.request(url)
        self.table_search(keyword)
        
        for url_number in trange(self.page_count_all, 
                                colour='WHITE', 
                                desc=keyword):
            url_pattern = (
                '{}{}.html?page_size=120?odr=relevance'
                .format(url, url_number + 1))
            
            self.table_catalog(url_pattern)       

    def scrape_by_search_bar(self):
        for search in self.conf['search_list']:
            # Page used to refer primary values
            url = 'https://www.gearbest.com/sale/{}/'.format(search)
            
            self.scrape_pattern(
                url = url,
                keyword = search)
        self.database.close()

    def scrape_by_link_generator(self):
        # Page used to refer primary values
        menu_url = 'https://www.gearbest.com/'
        
        for url in self.link_generator(menu_url):
            self.scrape_pattern(
                url = url[0],
                keyword = url[1])      
        self.database.close()

    def scrape_by_popular_searches(self):
        # Page used to refer primary values
        menu_url = 'https://www.gearbest.com/'
        
        for url in self.popular_searches(menu_url):
            self.scrape_pattern(
                url = url[0],
                keyword = url[1])
        self.database.close()


def run(path, mode):   
    """ Execute the Gearbest_Scraper """
    method = Method(path)
    
    if mode == 'search' or mode.startswith('s'):
        # >> python --mode search
        method.scrape_by_search_bar()       

    elif mode == 'link' or mode.startswith('l'):
        # >> python --mode link
        method.scrape_by_link_generator()
    
    elif mode == 'popular' or mode.startswith('p'):
        # >> python --mode popular
        method.scrape_by_popular_searches()

