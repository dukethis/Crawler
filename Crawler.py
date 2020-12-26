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

#----------------
# CRAWLER CLASS -
#----------------

class Crawler(urllib3.PoolManager):

    def __init__(self, url=None, agent="WebCake/0.10", **kargs):

        # Identify your crawler with a User-Agent
        self.agent = str(agent)

        # Set up request headers
        HEADERS = { "User-Agent" : self.agent }
        HEADERS = HEADERS.update(kargs["headers"]) if "headers" in kargs.keys() else HEADERS

        # Derived from urllib3.PoolManager
        urllib3.PoolManager.__init__(
            self,
            cert_reqs = 'CERT_REQUIRED',
            ca_certs  = certifi.where(),
            headers   = HEADERS
        )
        # Basic HTTP parameters
        self.url      = url
        self.method   = kargs["method"]   if "method"   in kargs.keys() else "GET"
        self.redirect = kargs["redirect"] if "redirect" in kargs.keys() else 1
        self.timeout  = kargs["timeout"]  if "timeout"  in kargs.keys() else 10
        self.charset  = kargs["charset"]  if "charset"  in kargs.keys() else "utf-8"
        self.response = None
        self.content  = None
        self.status   = None
        self.rules    = None
 
 
    @property
    def host(self):
        if not self.url:
            raise Exception("Type error: URL is "+str(self.url))
        url = urllib3.util.parse_url(self.url)
        return "://".join( [url.scheme,url.host] )
        
    def get_rules(self,url):
        """ Retrieve robots.txt rules """
        URL = urllib3.util.parse_url(url)
        URL = "://".join([ URL.scheme, URL.host ])+"/robots.txt"
        req = self.GET( URL )
        data = req.data.decode('utf-8').split('\n')
        rules = []
        start=0
        for i,line in enumerate(data):
            if line.startswith("User-agent: *") or line.startswith("User-agent: ") and line.count(self.agent):
                start=1
            elif start and (line.startswith("Allow:") or line.startswith("Disallow:") or line.startswith("Crawl-delay:")):
                rules.append( line ) 
            elif start and line.startswith("User-agent"):
                start=0
        self.rules = rules
        return rules

    def test(self,url):
        """ Test a secific robots.txt rule """
        if not self.rules: self.get_rules()
        href = "/"+re.sub(".*/","",url)
        return any([ x.replace('Disallow:','').strip()==href for x in self.rules if x.count("Disallow") ])
         
    def HEAD(self, url):
        """ Simple HEAD Request """
        self.url = url
        req = self.request("HEAD", url)
        return json.dumps( dict(req.headers), indent=2 )

    def GET(self, url):
        """ Raw GET request """
        # robots.txt rules testing
        if not self.rules:
            print("Warning: no rules have been set. Please call the 'get_rules()' method.")
        # block request when not allowed (see testing method)
        elif self.test(url):
            print("Warning: this URL is not allowed.")
            return
        self.url = url
        try: req = self.request("GET", url)
        except Exception as e:
            req = e
        return req
        
    def get(self, url=None, headers={}, verbose=0):
        """ User-friendly GET request
        """
        self.url = url
        req = self.GET(url)
        # DEFINE CONTENT-TYPE / CHARSET
        c_type  = req.headers["Content-Type"] if "Content-Type" in req.headers else None
        charset = c_type.split(";")[1].strip().split("=")[1] if c_type.count(";") else "UTF-8"

        # ACTUAL CONTENT DATA
        text_content = req.data.decode( charset )

        # USE BEAUTIFULSOUP?
        if any([ c_type.count( x ) for x in ["html","rss","xml"]]):
            html_content = BeautifulSoup( text_content, "lxml" )
            self.content = html_content
        # OR JSON
        elif c_type.count("json"):
            self.content = json.dumps( eval(text_content), indent=2 )
        # OR RAW OUTPUT
        else:
            self.content = text_content

        return self.content
    
    def parse_tags(self, url, tags, attributes=[]):
        req = self.get(url)
        if attributes:
            res = req.find_all( tags )
            res = [ url+'/'+ re.sub('^\.?\/?','',x.get(attr)) if attr=='href' and not x.get(attr).startswith('http') else x.get(attr) for x in res for attr in attributes if x.get(attr) ]
            return res
        else:
            res = req.find_all( tags )
            res = [ str(x) for x in res ]
            return res
    
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
                "headers" : self.headers
            },
            "response": {
                "status"  : self.response.status        if self.response else self.status,
                "time"    : self.response.time          if self.response else None,
                "headers" : dict(self.response.headers) if self.response else {},
                "body"    : self.content
            }
        }
        return json.dumps( this, indent=4 )
