#!/usr/bin/env python3
import os

def find_file_mod(name):
    try:
        for root, dirs, files in os.walk('~/connectomics_web_portal/saber'):
            if name in files:
                filepath = os.path.join(root, name)
            else:
                raise FileNotFoundError('FileNotFound')
        return filepath
    except FileNotFoundError:
        empty_dict = {}
        print('Unable to locate workflow: ' + name)
        return empty_dict
