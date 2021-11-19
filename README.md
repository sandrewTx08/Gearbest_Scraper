# Gearbest_Scraper

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/sandrewTx08/Gearbest_Scraper)

# Overview

Gearbest_Scraper is simple, intuitive and manageable, it seeks catalog ads from Gearbest web page, scraping their information then it's storing by a sequence of SQL commands through a relational database.

# Support

| <img src="https://www.iconsdb.com/icons/preview/green/csv-xxl.png"> | <img width=100px src="https://logodownload.org/wp-content/uploads/2016/10/mysql-logo.png"> | <img width=100px src="https://logodownload.org/wp-content/uploads/2018/05/sqlite-logo.png"> | <img width=100px src="https://upload.wikimedia.org/wikipedia/commons/2/29/Postgresql_elephant.svg"> | <img width=100px src="https://logodownload.org/wp-content/uploads/2016/10/Microsoft-SQL-Server-Logo-1.png"> | <img width=100px src="https://logodownload.org/wp-content/uploads/2014/04/oracle-logo-0.png"> |
|---|---|---|---|---|---|
| CSV | MySQL | SQLite | Postgresql | Microsoft SQL Server | Oracle Database |
| ✅ Avaliable | ✅ Avaliable | ✅ Avaliable | ⚠️ Soon | ⚠️ Maybe soon | ⚠️ Maybe soon |

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
Gearbest_Scraper> install.bat
```

__or__

```bash
Gearbest_Scraper:~$ ./install.bash
```

__or__

```bash
Gearbest_Scraper> pip install -r requirements.txt
```

# How to use

1. Define yours search list keywords in __configuration.json__ file 

```json
{"search":{"list":["keyword_foo_1","keyword_foo_2","keyword_foo_3"]}}
```

2. Execute the program 

```bash
> cd Gearbest_Scraper
Gearbest_Scraper> start.bat
```

__or__

```bash
Gearbest_Scraper> python main.py
```

# Methods

Methods is how Gearbest_Scraper receive catalog ads.

So you can use a simple script instead parsing argument.

Windows:

```bash
Gearbest_Scraper> start.bat
```

Linux:

```bash
Gearbest_Scraper:~$ ./start.bash
```

Setting search method example:
 
```
Method: s
```

__Search__ is select by default.

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

# Configuration file:

The configuration file must have the following fields:

field|key|description|
|---|---|---|
|method||settings realted to its function|
|connection|request|to request web pages|
|connection|database|database settings|

## Configurations example:

Phone brands list example:
```json
{"search":{"list":["asus","huawai","lenovo","samsung","ulefone","xiaomi"]}}
```

HTTP Header example:
```json
{"headers":{"User-Agent":"Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}}
```

Defining database path:
```json
{"database":{"sqlite":{"path":"C:/Users/some_user/Documents/gearbest_scraper.db"}}}
```

