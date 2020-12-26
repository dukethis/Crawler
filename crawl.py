#!/usr/bin/python3
# coding: utf-8
""" Crawler.py Class Interface
"""

import re, json
from Crawler import *
from argparse import ArgumentParser

#-------------------------
# COMMAND-LINE INTERFACE -
#-------------------------

if __name__ == '__main__':

 ap = ArgumentParser()
 ap.add_argument('url', type=str)
 ap.add_argument('-t', '--tags',       type=str, nargs="*")
 ap.add_argument('-a', '--attributes', type=str, nargs="*")
 ap.add_argument('-n', '--name',       type=str, default="Crawl-testing")
 
 args = ap.parse_args()
 
 url = args.url
 
 bot = Crawler()

 bot.get_rules( url )
 
 req = bot.get(url)
 
 if args.tags:
  if args.attributes:
   res = req.find_all( args.tags )
   res = [ x.get(attr) for x in res for attr in args.attributes if x.get(attr) ]
   print( "\n".join( res ) )
  else:
   res = req.find_all( args.tags )
   res = [ str(x) for x in res ]
   print( "\n".join( res ) )
 else:
   print( req.prettify() )
 
 
