#!/usr/bin/python3
# coding: utf-8
""" Crawler interface
"""

import re, json

from Crawler import *
from argparse import ArgumentParser

# CLI INTERFACE
if __name__ == '__main__':

 ap = ArgumentParser()
 ap.add_argument('url',type=str)
 ap.add_argument('-t', '--tags', type=str, nargs="*")
 ap.add_argument('-a', '--attributes', type=str, nargs="*")
 
 args = ap.parse_args()
 
 url = args.url
 
 bot = Crawler( name="Crawl-testing; abuse?: dukeart at free.fr" )

 req = bot.get(url)
 
 res = []
 
 if args.tags:
  if args.attributes:
   res = req.find_all( args.tags )
   res = [ x.get(attr) for x in res for attr in args.attributes if x.get(attr) ]
  else:
   res = req.find_all( args.tags )
 print( "\n".join( res ) )
 
 
