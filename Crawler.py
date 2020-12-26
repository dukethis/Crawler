#!/usr/bin/python3.7
# coding: utf-8
""" Minimalist Crawler project : KISS!!
"""

import re,sys,json,time
import urllib3,certifi

from bs4 import BeautifulSoup

# ~ # TO AVOID BROKEN PIPES
# ~ from signal import signal, SIGPIPE, SIG_DFL
# ~ signal(SIGPIPE,SIG_DFL)

class Crawler(urllib3.PoolManager):

    def __init__(self, url=None, agent="Crawl-testing", **kargs):
        self.agent = str(agent)
        HEADERS = { "User-Agent" : self.agent }
        HEADERS = HEADERS.update(kargs["headers"]) if "headers" in kargs.keys() else HEADERS
        urllib3.PoolManager.__init__(
            self,
            cert_reqs = 'CERT_REQUIRED',
            ca_certs  = certifi.where(),
            headers   = HEADERS
        )
        self.url      = url
        self.method   = kargs["method"]   if "method"   in kargs.keys() else "GET"
        self.redirect = kargs["redirect"] if "redirect" in kargs.keys() else 1
        self.timeout  = kargs["timeout"]  if "timeout"  in kargs.keys() else 10
        self.charset  = kargs["charset"]  if "charset"  in kargs.keys() else "utf-8"
        self.response = None
        self.content  = None
        self.status   = None

    def HEAD(self, url):
        req = self.request("HEAD", url)
        return json.dumps( dict(req.headers), indent=2 )

    def GET(self, url):
        """ Raw GET request """
        try: req = self.request("GET", url)
        except Exception as e:
            req = e
        return req
        
    def get(self, url=None, headers={}, verbose=0):
        """ User-friendly GET request
        """
        req = self.GET(url)
        # DEFINE CONTENT-TYPE / CHARSET
        c_type  = req.headers["Content-Type"] if "Content-Type" in req.headers else None
        charset = c_type.split(";")[1].strip().split("=")[1] if c_type.count(";") else "UTF-8"

        # ACTUAL CONTENT DATA
        text_content = req.data.decode( charset )

        # USE BEAUTIFULSOUP?
        if any([ c_type.count( x ) for x in ["html","rss","xml"]]):
            html_content = BeautifulSoup( text_content, "lxml" )
            return html_content
        # OR JSON
        elif c_type.count("json"):
            return json.dumps( eval(text_content), indent=2 )
        # OR RAW OUTPUT
        else:
            return text_content
    
    def get_headers(self):
        return json.dumps( self.headers, indent=4 )

    def get_response_headers(self):
        return json.dumps( dict(self.response.headers), indent=4 )

    def __str__(self):
        """ JSON Datagram """
        this = {
            "request": {
                "url"     : self.url,
                "method"  : self.method,
                "charset" : self.charset,
                "headers" : self.headers
            },
            "response": {
                "status"  : self.response.status if self.response else self.status,
                "time"    : self.response.time if self.response else None,
                "headers" : dict(self.response.headers) if self.response else {},
                "body"    : self.content
            }
        }
        return json.dumps( this, indent=4 )
