from os import chdir, path as sys_path
from tqdm import trange
from lxml import html
from json import load
from sqlite3 import connect
from requests import Session, Request


class Attributes(object):
    """ Page objects """
      
    @property
    def page_menu(self):
        return self.request(self.page_menu_url)
    page_menu_url = 'https://www.gearbest.com/'
    
    @property
    def page_root(self):
        return self.request(self.page_root_url)
    page_root_url = None
    
    @property
    def page_ads(self):
        return self.request(self.page_ads_url)
    page_ads_url = None

    @property
    def page_count_all(self):           
        if self.page_root != None:
            try: return int(self.page_root.xpath(
                '//footer/div[2]/div/a[last()-1]')[0].xpath('string()'))
            except IndexError: return 0
            except ValueError: return 0
        else: return 0
    
    @property
    def currency(self):
        try: return self.page_root.xpath(
            '//li[@id="js-btnShowShipto"]/span/span[2]')[0].xpath('string()')
        except IndexError: return None

    @property
    def search_category(self):
        if self.page_count_all != 0:
            try: return self.page_root.xpath(
                '//div[@class="cateMain_asideSeachTitle"]/a[@title]'
                )[0].get('title').replace("'", '').replace('"', '')
            except IndexError:
                try: return self.page_root.xpath(
                    '//div[@class="searchTitle_wrap"]/h1'
                    )[0].xpath('string()').replace("'", '').replace('"', '')
                except IndexError: return None 

    def catalog_gen(self):
        """ Scrape catalog ads """
        
        if self.page_ads != None:
            # Catalog list parent element
            try: catalog_list_box = self.page_ads.xpath(
                '//ul[@class="clearfix js_seachResultList"]')[0]
            except IndexError: return None

            if catalog_list_box.find('li[@data-goods-id]') != None:
                # Catalog list children elements
                try: catalog_list = catalog_list_box.xpath(
                    '//li[@data-goods-id]') 
                except IndexError: return None
                
                # Avaliable catalog on page
                catalog_count = len(catalog_list_box.xpath(
                    '//li[@data-goods-id]')) if catalog_list != None else 0
                
                if catalog_count >= 1:
                    catalog_count_range = range(catalog_count)
                    
                    price = [ float(catalog_list[i].get('data-shopprice'))
                        for i in catalog_count_range ]
                    
                    id = [ catalog_list[i].get('data-goods-id')
                        for i in catalog_count_range ]
                
                    image = [ catalog_list[i].xpath(
                            '//a[@data-img]/img[@data-lazy]')[i].get('data-lazy')
                                .replace("'", '')
                                .replace('"', '')
                        for i in catalog_count_range ]
                    
                    title = [ catalog_list[i].xpath(
                            '//div[@class="gbGoodsItem_outBox"]/p/a')[i].get('title')
                                .replace("'", '')
                                .replace('"', '')
                        for i in catalog_count_range ]
                    
                    link = [ catalog_list[i].xpath(
                            '//div[@class="gbGoodsItem_outBox"]/p/a')[i].get('href')
                                .replace("'", '')
                                .replace('"', '')
                        for i in catalog_count_range ]
                    
                    discount = [ int(catalog_list[i].find('span/strong').xpath('string()'))
                        if catalog_list[i].find('span/strong') != None
                        else None
                        for i in catalog_count_range ]
                    
                    review_rate = [ float(catalog_list[i].find(
                            'div/div[2]/span/span[2]').xpath('string()'))
                        if catalog_list[i].find('div/div[2]/span/span[2]') != None
                        else None
                        for i in catalog_count_range ]
                    
                    review_count = [ int(catalog_list[i].xpath('//li[@data-goods-id]')[i].find(
                            'div/div[2]/span/span[3]').xpath('string()')
                                .replace('(', '')
                                .replace(')', ''))
                        if catalog_list[i].find('div/div[2]/span/span[3]') != None
                        else None
                        for i in catalog_count_range ]
                    
                    price_tag = [ catalog_list[i].find('div/div[1]/a/span').get('title')
                            .replace('Warehouse', '')
                            .replace("'", '')
                            .replace('"', '')
                        if catalog_list[i].find('div/div[1]/a/span') != None
                        else catalog_list[i].find('div/div[1]/span').xpath('string()')
                        if catalog_list[i].find('div/div[1]/span') != None
                        else None
                        for i in catalog_count_range ]
                    
                    for i in catalog_count_range:       
                        """ Append values related to 'table_catalog' sequence order
                            'table_catalog' columns:
                                #1 id, #2 title
                                #3 link, #4 image
                                #5 price, #6 discount,
                                #7 price_tag, #8 review_rate,
                                #9 review_count, #10 search_id (foreign key) """
                        
                        yield [ id[i], title[i], link[i], image[i], price[i], 
                            discount[i], price_tag[i], review_rate[i], review_count[i] ]
        else: return None
    
    def link_gen(self):
        page = self.request(self.page_menu_url)
        
        for link in page.xpath(
            '//ul[@class="headCate"]/li[@class="headCate_item"]//*[@href]'):
           
           yield (link.get('href'), link.xpath('string()'))  

    def popular_searches_gen(self):
        page = self.request(self.page_menu_url)
        
        for link in page.xpath(
            '//li[@class="footerHotkey_item"]/a'):
            
            yield (link.get('href'), link.xpath('string()'))


class Database(Attributes):
    """ Database handler """

    def __init__(self, path):
        # Load configuration file
        try: self.conf = load(open(path))
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

        self.cursor.execute(
            f""" CREATE TABLE IF NOT EXISTS {self.crtble['name']} (
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

        elif currency_id[1] == self.currency: return currency_id[0]
    
    def table_search(self, keyword):        
        if self.page_count_all != 0:
            values = ((keyword  # Formatting string to database 
                        .replace("'", '')
                        .replace('"', '')
                    if keyword != None
                    else None),
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

    def table_catalog(self):
        # Provide last id from 'table_search'
        last_id = [ int(self.cursor.execute(
                f""" SELECT MAX ({self.stble['id']})
                    FROM {self.stble['name']}; """).fetchone()[0]) ]

        for catalog in self.catalog_gen():           
            # Concat catalog with last id as tuple
            catalog_concat = tuple(catalog) + tuple(last_id) 
            
            self.cursor.execute(
                f""" INSERT INTO {self.ctble['name']}  
                    VALUES (?,?,?,?,?,?,?,?,?,?); """, catalog_concat)


class Method(Database):
    """ Request page ads """
    session = Session()
    url_pattern = '{}{}.html?page_size=120?odr=relevance'

    def request(self, url):
        """ Return page object """       
        if (url.startswith('http://') or url.startswith('https://') 
            and "gearbest.com" in url):
            # Prepare request to be send
            request = Request(method='GET', url=url, 
                headers=self.conf['http_header']).prepare()            

            # Response from request
            response = self.session.send(request)

            # Return page content passing to HTML parser
            return (html.fromstring(response.text)
                if response.status_code == 200 or response != None 
                else None)
        else:
            return None

    def scrape_pattern(self, url, keyword):
        """ Scrape pages based on url pattern """               
        self.page_root_url = url
                
        if self.page_count_all != 0 or None:           
            self.table_search(keyword)
            for url_number in trange(self.page_count_all, desc=keyword):
                self.page_ads_url = self.url_pattern.format(url, url_number + 1)
                self.table_catalog()  

    def scrape_by_search_bar(self):
        for search in self.conf['search_list']:
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
        method.scrape_by_search_bar()      

    elif mode == 'link' or mode.startswith('l'):
        # >> python --mode link
        method.scrape_by_link_url()
    
    elif mode == 'popular' or mode.startswith('p'):
        # >> python --mode popular
        method.scrape_by_popular_searches()

    method.database.close() 