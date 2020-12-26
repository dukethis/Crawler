#!/usr/bin/python3
# coding: utf-8
""" Crawler.py Interface
"""

import re, json
from Crawler import *
from argparse import ArgumentParser

#-------------------------
# COMMAND-LINE INTERFACE -
#-------------------------

if __name__ == '__main__':

 ap = ArgumentParser("Simple Web Crawler")
 ap.add_argument('url', type=str)
 ap.add_argument('-t', '--tags',       type=str, nargs="*")
 ap.add_argument('-a', '--attributes', type=str, nargs="*")
 ap.add_argument('-n', '--name',       type=str, default="Crawl-testing")
 
 args = ap.parse_args()
 
 bot = Crawler()

 bot.get_rules( args.url )
 
 req = bot.get( args.url )
 
 hrefs = bot.parse_tags( args.url, args.tags, args.attributes)
 
 print( '\n'.join( hrefs ) )
 
 
 
