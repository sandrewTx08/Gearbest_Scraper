from sqlite3 import connect as sqlite
from mysql.connector import connect as mysql
from json import load
from os import chdir, path as sys_path


class SQLite(object):
    
    def sqlite_init(self):
        """ Create database """
        # Enable foreign keys
        self.sqlite_cursor.execute(""" PRAGMA foreign_keys = 1 ; """)

        currency_table = open('gearbest_scraper/database/sqlite/currency_table.sql').read()
        self.sqlite_cursor.executescript(currency_table)

        search_table = open('gearbest_scraper/database/sqlite/search_table.sql').read()
        self.sqlite_cursor.executescript(search_table)

        catalog_table = open('gearbest_scraper/database/sqlite/catalog_table.sql').read()
        self.sqlite_cursor.executescript(catalog_table)

        self.sqlite_database.commit()

    @property
    def sqlite_currency_id(self):
        """ Query last id from currency table """
        currency_id = self.sqlite_cursor.execute(  
            f""" SELECT MAX (id), abbreviation 
                FROM currency_table 
                WHERE abbreviation LIKE '{self.currency}'; """).fetchone()

        # Create a currency id if not exist
        if currency_id[0] == None:
            self.sqlite_cursor.execute(
                f""" INSERT INTO currency_table 
                    (id, abbreviation) 
                    VALUES (?,?); """, (None, self.currency))
            return 1

        elif currency_id[1] == self.currency: return currency_id[0]

    def sqlite_table_search(self, keyword):        
        if self.page_count_all != 0:
            values = ((keyword  # Formatting string to database 
                        .replace("'", '')
                        .replace('"', '')
                    if keyword != None
                    else None),
                self.search_category,
                self.page_count_all,
                self.sqlite_currency_id)   
            self.sqlite_cursor.execute(
                f""" INSERT INTO search_table (keyword, 
                    category, pages_count, 
                    datetime, currency_id)

                    VALUES (?,?,?,date('now'),?); """, values)
            
            self.sqlite_database.commit()

    def sqlite_table_catalog(self):
        # Provide last id from 'table_search'
        last_id = [ int(self.sqlite_cursor.execute(
                f""" SELECT MAX (id)
                    FROM search_table; """).fetchone()[0]) ]

        for catalog in self.catalog_gen():           
            # Concat catalog with last id as tuple
            catalog_concat = tuple(catalog) + tuple(last_id) 
            
            self.sqlite_cursor.execute(
                f""" INSERT INTO catalog_table 
                    VALUES (?,?,
                            ?,?,
                            ?,?,
                            ?,?,
                            ?,?); """, catalog_concat)


class MySQL(object):

    def mysql_init(self):
        """ Create database """
        for _ in self.mysql_cursor.execute(open(
            'gearbest_scraper/database/mysql/database.sql').read(), multi=True): pass

        for _ in self.mysql_cursor.execute(open(
            'gearbest_scraper/database/mysql/currency_table.sql').read(), multi=True): pass

        for _ in self.mysql_cursor.execute(open(
            'gearbest_scraper/database/mysql/search_table.sql').read(), multi=True): pass

        for _ in self.mysql_cursor.execute(open(
            'gearbest_scraper/database/mysql/catalog_table.sql').read(), multi=True): pass

        self.mysql_database.commit()
            
    @property
    def mysql_currency_id(self):
        """ Query last id from currency table """
        self.mysql_cursor.execute(  
            f""" SELECT MAX(id), abbreviation 
                FROM currency_table 
                WHERE abbreviation LIKE '{self.currency}'; """)

        currency_id = self.mysql_cursor.fetchone()

        # Create a currency id if not exist
        if currency_id[0] == None:
            self.mysql_cursor.execute(
                """ INSERT INTO currency_table 
                    (id, abbreviation) 
                    VALUES (%s,%s); """, (None, self.currency))
            return 1

        elif currency_id[1] == self.currency: return currency_id[0]

    def mysql_table_catalog(self):
        self.mysql_cursor.execute(""" SELECT MAX(id) FROM search_table; """)
               
        last_id = [ int(self.mysql_cursor.fetchone()[0]) ]

        for catalog in self.catalog_gen():           
            # Concat catalog with last id as tuple
            catalog_concat = tuple(catalog) + tuple(last_id) 
            
            self.mysql_cursor.execute(
                """ INSERT INTO catalog_table 
                    VALUES (%s,%s,
                            %s,%s,
                            %s,%s,
                            %s,%s,
                            %s,%s); """, catalog_concat)

    def mysql_table_search(self, keyword):
        if self.page_count_all != 0:
            values = ((keyword  # Formatting string to database 
                        .replace("'", '')
                        .replace('"', '')
                    if keyword != None
                    else None),
                self.search_category,
                self.page_count_all,
                self.mysql_currency_id)   
            
            self.mysql_cursor.execute(
                """ INSERT INTO search_table (keyword, 
                    category, pages_count, 
                    datetime, currency_id)

                    VALUES (%s,%s,%s,NULL,%s); """, values)
            
            self.mysql_database.commit()   


class Connection(SQLite, MySQL):
    """ Database handler """

    def __init__(self, configuration_path):
        # Load configuration file 
        try: self.conf = load(open(configuration_path))
        except FileNotFoundError:
            chdir(sys_path.dirname(sys_path.abspath(__file__)))
            self.conf = load(open(configuration_path))

        self.sqlite_enable = (True
            if self.conf['connection']['database']['sqlite']['enable']
            else False)

        self.mysql_enable = (True 
            if self.conf['connection']['database']['mysql']['enable']
            else False)

        if self.sqlite_enable:
            self.sqlite_database = sqlite(
                self.conf['connection']['database']['sqlite']['path']
                if self.conf['connection']['database']['sqlite']['path'] != None
                else 'gearbest_scraper_default.db')
            self.sqlite_cursor = self.sqlite_database.cursor()
            self.sqlite_init()
        
        if self.mysql_enable:
            self.mysql_database = mysql(
                host = self.conf['connection']['database']['mysql']['host'],
                user = self.conf['connection']['database']['mysql']['user'],
                password = self.conf['connection']['database']['mysql']['password'])
            self.mysql_cursor = self.mysql_database.cursor()
            self.mysql_init()

