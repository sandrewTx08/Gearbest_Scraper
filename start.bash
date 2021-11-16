#!/bin/bash
main="main.py"
conf="configuration.json"
mode="$2"

if [ "$mode" == "" ]
then read -p "Method:" mode 
fi

if [ "${mode:0:1}" == "s" ]; 
then 
    method="search" 
fi

if [ "${mode:0:1}" == "l" ]; 
then 
    method="link" 
fi

if [ "${mode:0:1}" == "p" ]; 
then 
    method="popular" 
fi

python $main $conf $method