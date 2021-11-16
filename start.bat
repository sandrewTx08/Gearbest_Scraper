@echo off
set main=main.py
if "%conf_param%" == "" set conf_param=configuration.json

set /P mode_param="Method: "

if "%mode_param:~0,1%" == "s" set mode_param=search
if "%mode_param:~0,1%" == "l" set mode_param=link
if "%mode_param:~0,1%" == "p" set mode_param=popular

set conf_arg=--conf %conf_param%
set mode_arg=--mode %mode_param%
set command=python %main% %conf_arg% %mode_arg%

%command%

