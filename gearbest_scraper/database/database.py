from sqlite3 import connect
from json import load
from os import chdir, path as sys_path

class Connection:
    """ Database handler """

    def __init__(self, configuration_path):
        # Load configuration file
          
        try: self.conf = load(open(configuration_path))
        except FileNotFoundError:
            chdir(sys_path.dirname(sys_path.abspath(__file__)))
            self.conf = load(open(configuration_path))
        
        self.database = connect(
            self.conf['connection']['database']['sqlite']['path']
            if self.conf['connection']['database']['sqlite']['path'] != None
            else 'gearbest_scraper_default.db')
        self.cursor = self.database.cursor()

        # Enable foreign keys
        self.cursor.execute(""" PRAGMA foreign_keys = 1 ; """)

        currency_table = open('gearbest_scraper/database/currency_table.sql').read()
        self.cursor.executescript(currency_table)

        search_table = open('gearbest_scraper/database/search_table.sql').read()
        self.cursor.executescript(search_table)

        catalog_table = open('gearbest_scraper/database/catalog_table.sql').read()
        self.cursor.executescript(catalog_table)

        self.database.commit()
    
    @property
    def currency_id(self):
        """ Query last id from currency table """
        currency_id = self.cursor.execute(  
            f""" SELECT MAX (id), abbreviation 
                FROM currency_table 
                WHERE abbreviation LIKE '{self.currency}'; """).fetchone()

        # Create a currency id if not exist
        if currency_id[0] == None:
            self.cursor.execute(
                f""" INSERT INTO currency_table 
                    (id, abbreviation) 
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
                f""" INSERT INTO search_table (keyword, 
                    category, pages_count, 
                    datetime, currency_id)

                    VALUES (?,?,?,date('now'),?); """, values)
            
            self.database.commit()

    def table_catalog(self):
        # Provide last id from 'table_search'
        last_id = [ int(self.cursor.execute(
                f""" SELECT MAX (id)
                    FROM search_table; """).fetchone()[0]) ]

        for catalog in self.catalog_gen():           
            # Concat catalog with last id as tuple
            catalog_concat = tuple(catalog) + tuple(last_id) 
            
            self.cursor.execute(
                f""" INSERT INTO catalog_table 
                    VALUES (?,?,?,?,?,?,?,?,?,?); """, catalog_concat)
