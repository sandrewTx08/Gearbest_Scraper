# Gearbest_Scraper

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/sandrewTx08/Gearbest_Scraper)


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

# Methods

Methods is how Gearbest_Scraper receive catalog ads.

__Search__ is select by default

## Link method

This method scrape all catalogs related to main page links on painel called "Category".
The number total page is set by sum of parent and childrens links on painel menu. Overtime database get larger.

<img width=90% src=https://user-images.githubusercontent.com/89039740/140583781-b1ba8b7c-115c-4a3d-a17b-065bf359b39d.gif>

Command line:
```bash
> python main.py --mode link
```

## Search method

Search method uses a configuration file to set catalog targets.
The "search_list" inside the file must contain a list of keywords to be scrape like a search bar style.

<img width=90% src=https://user-images.githubusercontent.com/89039740/140584581-3d8c88f3-b32e-4eb4-9f86-575e27001e0b.png>

Command line:
```bash
> python main.py --mode search
```

## Popular method

It scrape the most popular searches according web page.

<img width=90% src=https://user-images.githubusercontent.com/89039740/140584576-1ed76b3c-beb8-464e-8fe0-10b78f5e85a6.png>

Command line:
```bash
> python main.py --mode popular
```

## Configuration file:

The configuration file must have the following fields:

|key|description|
|---|---|
|search_list|keyword list to be scraped|
|http_header|http header to request web pages|
|database|database settings|
|table_catalog|containing catalogs ads information|
|table_search|containing search categories|
|table_currency|currency identifiers|

## Configurations example:

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

