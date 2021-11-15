from lxml import html
from requests import Session, Request


class Attributes(object):
    """ Page objects """
    session = Session()
    url_pattern = '{}{}.html?page_size=120?odr=relevance'
    
    def request(self, url):
        """ Return page object """       
        if (url.startswith('http://') or url.startswith('https://') 
            and "gearbest.com" in url):
            # Prepare request to be send
            request = Request(method='GET', url=url, 
                headers=self.conf['connection']['request']['headers'],
                cookies=self.conf['connection']['request']['cookies']).prepare()            

            # Response from request
            response = self.session.send(request)

            # Return page content passing to HTML parser
            return (html.fromstring(response.text)
                if response.status_code == 200 or response != None 
                else None)
        else:
            return None

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
        for link in self.page_menu.xpath(
            '//ul[@class="headCate"]/li[@class="headCate_item"]//*[@href]'):
           yield (link.get('href'), link.xpath('string()'))  

    def popular_searches_gen(self):       
        for link in self.page_menu.xpath(
            '//li[@class="footerHotkey_item"]/a'):
            yield (link.get('href'), link.xpath('string()'))

