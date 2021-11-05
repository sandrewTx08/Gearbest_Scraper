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

        self.cursor.execute(f""" CREATE TABLE IF NOT EXISTS {self.crtble['name']} (
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
    
        page = get(url, 
            timeout=120, 
            params=self.conf['http_header'])

        if page.status_code == 200:
            return HTML(page.text)

    def page_count_all(self, reference_page):

        if reference_page != None:
            try:
                return int(reference_page.xpath(
                    '//footer/div[2]/div/a[last()-1]')[0].xpath('string()'))

            except IndexError:
                return 0

        elif reference_page == None:
            return 0

    def search_category(self, reference_page, page_count_all):

        if page_count_all != 0:
            try:
                return reference_page.xpath(
                    '//div[@class="cateMain_asideSeachTitle"]/a[@title]'
                    )[0].get('title').replace("'", '').replace('"', '')

            except IndexError:
                try:
                    return reference_page.xpath(
                        '//div[@class="searchTitle_wrap"]/h1'
                        )[0].xpath('string()').replace("'", '').replace('"', '')

                except IndexError:
                    return None

    def table_currency(self, reference_page):
        
        currency = reference_page.xpath(
            '//li[@id="js-btnShowShipto"]/span/span[2]')[0].xpath('string()')

        # Check last currency id
        def last_id():
            return self.cursor.execute(  
                f""" SELECT MAX({self.crtble['id']}), {self.crtble['abbreviation']} 
                        FROM {self.crtble['name']} 
                        WHERE {self.crtble['abbreviation']} LIKE '{currency}'
                    ; """).fetchone()

        # Create a currency id if not exist
        if last_id()[0] == None:
            self.cursor.execute(
                f""" INSERT INTO {self.crtble['name']} 
                        ({self.crtble['id']},{self.crtble['abbreviation']}) 
                        VALUES (?,?)
                    ; """, (None, currency))

        elif last_id()[1] == currency:
            return last_id()[0]

    def table_search(self, search, reference_page, page_count_all): 
        
        if search != None:
            search_to_database = search.replace(
                "'", '').replace('"', '')

        elif search == None:
            search_to_database = None
        
        currency_id = self.table_currency(reference_page)
        search_category = self.search_category(reference_page, page_count_all)
        
        if page_count_all != 0:
            search_items_value = (
                search_to_database,
                search_category,
                page_count_all,
                currency_id)

            self.cursor.execute(
                f""" INSERT INTO {self.stble['name']} 
                    ({self.stble['keyword']}, 
                    {self.stble['category']},
                    {self.stble['pages_count']},
                    {self.stble['datetime']},
                    {self.stble['currency_id']})

                    VALUES(?,?,?,date('now'),?); """, search_items_value)

    def table_catalog(self, page_with_number):
        """ Insert catalog ads into database """

        page_with_number = self.request(page_with_number)

        # Catalog list parent element
        catalog_list_box = page_with_number.xpath(
            '//ul[@class="clearfix js_seachResultList"]')[0]

        if catalog_list_box.find('li[@data-goods-id]') != None:

            # Catalog list children elements
            catalog_list = catalog_list_box.xpath(
                '//li[@data-goods-id]') 

            # Avaliable catalog on page
            catalog_count = range(len( 
                catalog_list_box.xpath(
                    '//li[@data-goods-id]')))

            price = [
                    float(catalog_list[i].get(
                        'data-shopprice'))
                    for i in catalog_count
                ]
            
            id = [
                    catalog_list[i].get(
                        'data-goods-id')
                    for i in catalog_count
                ]
            
            image = [
                    catalog_list[i].xpath(
                        '//a[@data-img]/img[@data-lazy]')[i].get('data-lazy')
                        .replace("'", '').replace('"', '')
                    for i in catalog_count
                ]
            
            title = [
                    catalog_list[i].xpath(
                        '//div[@class="gbGoodsItem_outBox"]/p/a')[i].get('title')
                        .replace("'", '').replace('"', '')
                    for i in catalog_count
                ]
            
            link = [
                    catalog_list[i].xpath(
                        '//div[@class="gbGoodsItem_outBox"]/p/a')[i].get('href')
                        .replace("'", '').replace('"', '')
                    for i in catalog_count
                ]
            
            discount = [
                    int(catalog_list[i].find(
                        'span/strong').xpath('string()'))
                    if catalog_list[i].find(
                        'span/strong') != None
                    else None
                    for i in catalog_count
                ]
            
            review_rate = [
                    float(catalog_list[i].find(
                        'div/div[2]/span/span[2]').xpath('string()'))
                    if catalog_list[i].find(
                        'div/div[2]/span/span[2]') != None
                    else None
                    for i in catalog_count
                ]
            
            review_count = [
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
            
            price_tag = [
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
            
            self.database.commit()
    
    def link_generator(self, page_menu):

        for parent_link in page_menu.xpath(
            '//li[@class="headCate_item"]/a[@class="headCate_itemName"]'):

            yield parent_link.get('href')

        for child_link in page_menu.xpath(
            '//li[@class="headCate_item"]/div//a[@class="headCate_childName"]'):

            yield child_link.get('href')
    
    def scrape_by_search_bar(self):

        for search in self.conf['search_list']:
            
            search_to_url = search.replace(" ", "-")

            # Page used to refer primary values
            reference_page = self.request(
                'https://www.gearbest.com/sale/{}?page_size=120?odr=relevance'
                .format(search_to_url))

            page_count_all = self.page_count_all(reference_page)
            
            self.table_search(
                search,
                reference_page,
                page_count_all)

            for page_number in trange(page_count_all, colour='WHITE', desc=search):

                self.table_catalog(
                    'https://www.gearbest.com/sale/{}/{}.html?page_size=120?odr=relevance'
                    .format(search_to_url, page_number + 1)) 

    def scrape_by_link_generator(self):

        # Page used to refer primary values
        page_menu = self.request(
            'https://www.gearbest.com/')

        for url in self.link_generator(page_menu):

            reference_page = self.request(
                '{}?page_size=120?odr=relevance'
                .format(url))
            
            page_count_all = self.page_count_all(reference_page)

            self.table_search(
                None,
                reference_page,
                page_count_all)

            for page_number in trange(page_count_all, colour='WHITE', desc=url):
         
                self.table_catalog(
                    '{}{}.html?page_size=120?odr=relevance'
                    .format(url, page_number + 1))

    def scrape_by_popular_searches(self):
        
        reference_page = self.request('https://www.gearbest.com/')
        popular_list_box = reference_page.xpath('//li[@class="footerHotkey_item"]/a')
        
        def popular_searches():
            for pop_item in popular_list_box:
                yield (pop_item.get('href'), pop_item.xpath('string()'))
        
        for pop_item in popular_searches():
            
            # Page used to refer primary values
            reference_page = self.request(
                '{}?page_size=120?odr=relevance'
                .format(pop_item[0]))

            page_count_all = self.page_count_all(reference_page)
            
            self.table_search(
                pop_item[1],
                reference_page,
                page_count_all)

            for page_number in trange(page_count_all, colour='WHITE', desc=pop_item[1]):

                self.table_catalog(
                    '{}{}.html?page_size=120?odr=relevance'
                    .format(pop_item[0], page_number + 1))   


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
        scraper.scrape_by_search_bar()       

    if mode == 'link' or mode.startswith('l'):
        scraper.scrape_by_link_generator()
    
    if mode == 'popular' or mode.startswith('p'):
        scraper.scrape_by_popular_searches()
    
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

