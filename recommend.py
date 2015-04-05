#!/usr/bin/env python

__author__      = "Henk van Appeven, Simon Verhoek"
__maintainer__  = "Simon Verhoek"
__status__      = "Development"

from pyes import *
from datetime import datetime, date, timedelta
from urllib2 import urlopen
import re
import cookielib, urllib2
from cookielib import CookieJar
import json
import csv
from bs4 import BeautifulSoup
import os.path
import time

from classes import Article, Index

# needed for scraper to open link
cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
 
# seconds of interval between which new browsing
# history is checked
interval = 5  

# list of user's browsing history in urls 
# that builds up as long as application is running
visitedUrlsList = []

# name of file that is passed on by JS extension.
historyFileName = "urlsonly.json"

# create a connection with ElasticSearch
connection = ES('localhost:9200')

# index name as seen in ElasticSearch
indexName = "testindex"

# prepare index object
articleListName = "NOS Nieuws"

# set number of days back in time to
# be scraped. If set to 1, only today's
# archive is scraped.
noDays = 1

# location of HTML file to open in which
# recommended articles will be shown
recommendationsPage = "index.html"

# choose correct encoding, based on the
# article's language
encoding = "latin_1"

# number of articles that user needs to 
# read before recommendation cycle ends
NoArticlesToBeRead = 1

# the number of recommendations that should be given
noReccomendations = 30

# name of exported news archive
archiveName = "archive"
# if you want to create an index from a
# local file, give correct filepath here
localArchive =  "/Users/simonverhoek/Google Drive/Studie/Web search/Project/nosrecommender/" + archiveName + ".json"

# name of any exported recommendations file(s)
outputFileName = "recommendations"

# how the data should be formatted in ElasticSearch
mapping = { u'URL': {       'boost': 1.0,
                            'index': 'analyzed',
                            'store': 'yes',
                            'type': u'string',
                            "term_vector" : "with_positions_offsets"},
            u'title': {     'boost': 2.0,
                            'index': 'analyzed',
                            'store': 'yes',
                            'type': u'string',
                            "similarity": "BM25",
                            "term_vector" : "with_positions_offsets"},
            u'categories': {'boost': 1.0,
                            'index': 'analyzed',
                            'store': 'yes',
                            'type': u'string',
                            "similarity": "BM25",
                            "term_vector" : "with_positions_offsets"},
            u'body': {      'boost': 1.0,
                            'index': 'analyzed',
                            'store': 'yes',
                            'type': u'string',
                            "similarity": "BM25",
                            "term_vector" : "with_positions_offsets"},
            u'image': {     'boost': 0.0,
                            'index': 'analyzed',
                            'store': 'yes',
                            'type': u'string',
                            "term_vector" : "with_positions_offsets"}}

setting = {
    "analysis": {
        "filter": {
            "dutch_stop": {
                "type": "stop",
                "stopwords": "_dutch_" 
            }
        },
        "analyzer": {
            "dutch": {
                "tokenizer": "standard",
                "filter": [
                    "lowercase",
                    "dutch_stop"
                ]
            }
        }
    }
}

# BUILD INDEX

    # import news archive

    # instantiate index
    # build index
    # for every article in list
        # add to index instance
    # index articles

# WAITING FOR INPUT

    # if JSON found:
        # get article data
        # add to list of read articles

        # query index with list of read articles
        # check recommendations against list of read articles

        # add recommendations to index.html
    # else: 
        # recheck in 5 sec

def main():
    print
    print "===== PRESTEP 1: GETTING A NEWS ARCHIVE ====="
    print
    """
    Get a list of urls to NOS news articles
    to build an archive.
    """
    """ 
    EITHER: scrape the NOS news archive 
    """
    #newsArchive = getData(scrapeUrls(noDays, date), articleListName)

    # directly export it for later use
    #exportJson(newsArchive, archiveName)

    """ 
    OR: import a list of urls from a
    local .json file.
    """
    newsArchive = importJson(localArchive)
    print newsArchive
    #print "Skipped."

    newsArchive = sanitize_input(newsArchive)
    print newsArchive

    print
    print "===== PRESTEP 2: INDEXING THE NEWS ARCHIVE ====="
    print
    """
    Create an index in ElasticSearch, and add
    the news archive to this.
    """
    name = newsArchive.keys()[0]
    name = name.lower()
    name = name.replace(" ", "_")

    print name


    index = Index(name, newsArchive.values()[0])

    #print index

    Index.build(index, setting, mapping)
    Index.indexArticles(index)

    


def importJson(localFile):
    """
    Imports a JSON file from the given localFile
    and returns this.
    -   localFile should be a string containing the
        path to a certain local .json file.
    """
    content = json.loads(open(localFile, "rb").read())

    print "Imported content from " + localFile + "."
    return content

def sanitize_input(newsArchive):
    key = newsArchive.keys()[0]
    key = key.lower()
    key = key.replace(" ", "_")
    print key

    valueList = newsArchive.values()[0]
    valueList = valueList.encode(encoding)

    return newsArchive.encode(encoding)


# execute main
if __name__ == "__main__":
    main()



