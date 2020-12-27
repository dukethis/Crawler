#!/usr/bin/python3.7
# coding: utf-8
""" Minimalist Crawler project : KISS!!
"""

import re,sys,json,time,datetime
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
        self.rules    = { "Crawl-delay":10 }
        self.delay    = 10
        self.log(f"Crawler {id(self)} starts")
 
    def log(self, line):
        ts = datetime.datetime.now().strftime("%m-%d %H:%M:%S")
        sys.stdout.write(f"""{ts} {line}\n""")
 
    @property
    def host(self):
        if not self.url:
            raise Exception("Type error: URL is "+str(self.url))
        url = urllib3.util.parse_url(self.url)
        return "://".join( [url.scheme,url.host] )
        
    def get_rules(self,url):
        """ Retrieve robots.txt rules """
        tx = time.time()
        URL = urllib3.util.parse_url(url)
        URL = "://".join([ URL.scheme, URL.host ])+"/robots.txt"
        req = self.GET( URL )
        data = req.data.decode('utf-8').split('\n')
        rules = []
        start = 0
        self.log(f"Fetch rules from [{self.host}]")
        for i,line in enumerate(data):
            if line.startswith("User-agent: *") or line.startswith("User-agent: ") and line.count(self.agent):
                start=1
            elif start and (line.startswith("Allow:") or line.startswith("Disallow:") or line.startswith("Crawl-delay:")):
                rules.append( line ) 
            elif start and line.startswith("User-agent"):
                start=0
        self.rules = rules
        self.delay = max([ int(u.split(':')[1].strip()) for u in self.rules if u.lower().startswith("crawl-delay:")  ])
        tx = time.time()-tx
        self.log(f"Fetched {len(self.rules)} rules from [{self.host}] ({tx:.1f}s)")
        return rules

    def uri_testing(self,url):
        """ Test a secific robots.txt rule """
        if not self.rules: self.get_rules()
        href = urllib3.util.parse_url(url)
        href = href.path
        return any([ x.replace('Disallow:','').strip()==href for x in self.rules if x.count("Disallow") ])
         
    def HEAD(self, url):
        """ Simple HEAD Request """
        self.url = url
        req = self.request("HEAD", url)
        return json.dumps( dict(req.headers), indent=2 )

    def GET(self, url):
        """ Raw GET request """
        # robots.txt rules testing
        if len(self.rules)==0:
            self.log(f"Rules [{self.host}]")
            self.get_rules()
        # block request when not allowed (see testing method)
        if self.uri_testing(url):
            self.log(f"Warning: this URL is not allowed [{url}]")
            sys.exit(1)
        self.url = url
        try: req = self.request("GET", url)
        except Exception as e:
            req = e
        return req
        
    def get(self, url=None, headers={}, verbose=0):
        """ User-friendly GET request
        - Address the correct Content-Type
        - Parse the received content
        - Store it in self.content
        - Return the content
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
            self.content = html_content
        # OR JSON
        elif c_type.count("json"):
            self.content = json.dumps( eval(text_content), indent=2 )
        # OR RAW OUTPUT
        else:
            self.content = text_content

        return req
    
    def parse_tags(self, url, tags, attributes=[]):
        """ GET request and parse specific HTML 'tags' (eventually with specific 'attributes') 
        # tags & attributes : <tag attribute1="value1">innerText</tag>
        # With    attributes: it will be parsed and returned
        # Without attributes: whole tag is parsed as a string and returned 
        """
        req = self.get(url)
        if not req.headers["Content-Type"].count("html"):
            return self.content
            
        if attributes:
            res = req.find_all( tags )
            res = [ re.sub("/$","",url) + re.sub('^[.]*','',x.get(attr)) if attr=='href' and not x.get(attr).startswith('http') else x.get(attr) for x in res for attr in attributes if x.get(attr) ]
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
