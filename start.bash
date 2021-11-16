#!/bin/bash
main="main.py"
conf_param="configuration.json"

read -p "Method: " mode_param

if [ "${mode_param:0:1}" == "s" ]; 
then 
    mode_param="search" 
fi

if [ "${mode_param:0:1}" == "l" ]; 
then 
    mode_param="link" 
fi

if [ "${mode_param:0:1}" == "p" ]; 
then 
    mode_param="popular" 
fi

conf_arg="--conf $conf_param"
mode_arg="--mode $mode_param"
command="python $main $conf_arg $mode_arg"

$command

