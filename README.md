# Gearbest_Scraper

# Overview

Gearbest_Scraper is simple, intuitive and manageable, it seeks catalog ads from Gearbest web page, scraping their information then it's storing by a sequence of SQL commands through a relational database.

# Installing
 
1. Download: 
```bash
> git clone https://github.com/sandrewTx08/Gearbest_Scraper
```

2. Move to directory 

```bash
> cd Gearbest_Scraper
```

3. Installing dependencies: 

```bash
> pip install -r requirements.txt
```

# How to use

1. Define yours search list keywords in __configuration.json__ file 

```json
{"search_list": ["keyword1","keyword2","keyword3"]}
```

2. Execute the program 
```bash
> cd Gearbest_Scraper
> python main.py
```

## Methods

You can choose between two mode:

__Search__ is select by default

### Link method

This method scrape all catalogs related to main page links on painel called "Category".
The number total page is set by sum of parent and childrens links on painel menu. Overtime database get larger.

```bash
> python main.py --mode link
```

### Search method

Search method uses a configuration file to set catalog targets.
The "search_list" inside the file must contain a list of keywords to be scrape like a search bar style.


```bash
> python main.py --mode search
```

### Configuration file:

The configuration file must have the following fields:

|key|description|
|---|---|
|search_list|keyword list to be scraped|
|http_header|http header to request web pages|
|database|database settings|
|table_catalog|containing catalogs ads information|
|table_search|containing search categories|

### Configurations example:

Phone brands list example:
```json
{"search_list": ["asus","huawai","lenovo","samsung","ulefone","xiaomi"]}
```

HTTP Header example:
```json
{"http_header": {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}}
```

Defining database path:
```json
{"database": {"name": "C://gearbest_scraper.db"}}
```

