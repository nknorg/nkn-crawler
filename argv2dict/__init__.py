#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Copyright (c) 2018 nkn.org. All Rights Reserved
:author: gdmmx
:date: 2018-08-13 10:52:21
:Usage Example: python argv2dict.py a=1 b=2 x=str1
"""

__version__ = '1.0.0'
__author__ = 'gdmmx <gdmmx@nkn.org>'

def argv2dict(*lst):
    """
    :Functional: Convert a [k=v, x=y, ...] list to a python' dict. It is useful for convert sys.argv to a dict
    :Example: argv2dict('a=1', 'b=2', 'x=str1')
    """
    if hasattr(lst, '__iter__'):    ### Is iterable
        return dict(map(lambda x:(str(x).split('=', 1)),
                        filter(lambda x:str(x).find('=') != -1, lst)
                ))
    return {}
