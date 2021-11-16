@echo off
:: Default filenames
set main=main.py
set conf=configuration.json
                                            
if "%2"=="" (set /P mode="Method: ") else (set mode=%2)

:: Replace ( -- )
set mode=%mode:--=%

if "%mode:~0,1%" == "s" set mode=search
if "%mode:~0,1%" == "l" set mode=link
if "%mode:~0,1%" == "p" set mode=popular

python %main% %conf% %mode%

