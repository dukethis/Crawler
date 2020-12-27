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

 HOST = "https://dukeart.netlib.re"
 URIS = ["/robots.txt", "/humans.txt", "/media/file/"]

 tags = ["a"]
 attributes = []
 
 bot.get_rules( HOST )
 print(HOST)

 for uri in URIS:
   url = HOST+uri
   hrefs = bot.parse_tags( url, tags, attributes)
   if type(hrefs)==list: print( '\n'.join( hrefs ) )
   else:
      print( hrefs )
 
 
