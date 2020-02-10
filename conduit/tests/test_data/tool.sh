#!/bin/bash

# A tool with some basic functionality to enable testing


while [ "$1" != "" ]; do
    case $1 in
        --file1 )           shift
                            file1=$1
                            ;;
        --file2 )           shift
                            file2=$1
                            ;;
        --file3 )           shift
                            file3=$1
                            ;;
        --int )             shift
                            arg_int=$1
                            ;;
        --bool )            shift
                            arg_bool=$1
                            ;;
        --float )           shift
                            arg_float=$1
                            ;;
        --double )          shift
                            arg_double=$1
                            ;;
        --string )          shift
                            arg_bool=$1
                            ;;
        * )                 echo "Unrecognized argument"
                            break
                            ;;
    esac
    shift
done

