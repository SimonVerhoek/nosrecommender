#!/usr/bin/env python

import os.path
import json
from datetime import datetime, date, timedelta
from urllib2 import urlopen
import cookielib, urllib2
from cookielib import CookieJar
import re
from classes import Article, Collection
from sys import exit

# needed for scraper to open link
cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

# name of exported news archive
fileName = "archive.json"

# if you want to create an index from a
# local file, give correct filepath here
localArchive =  "/Users/simonverhoek/Google Drive/Studie/Web search/Project/nosrecommender/" + fileName

# If you want to create an index without a
# local file, set the name for the index here:
archiveName = "NOS archive"

# set number of days back in time to
# be scraped. If set to 1, only today's
# archive is scraped.
noDays = 1


def main():
    print
    print "===== STEP 1: BUILDING A NEWS ARCHIVE ====="
    print
    """ 
    OPTION 1: import an existing archive
    """
    get_existing_archive(fileName)
        
    """ 
    OPTION 2: scrape the news archive.
    The procedure is as follows: 
    1:  Scrape urls for a set number of days. 
    2:  Instantiate Collection.
    3:  For each url, instantiate Article. The article's
        contents are scraped automatically by the Article 
        class.
    4:  Add article to collection instance.
    """
    #build_new_archive(archiveName, noDays)

    # directly export it for later use
    #exportJson(newsArchive, archiveName)

def get_existing_archive(fileName):
    """
    Imports an existing archive from a
    .json file.
    filecontent[0] = collection name
    filecontent[1] = list of articles in file.
    """
    print 'Attempting to import from local file "' + fileName + '"...'
    if os.path.isfile(fileName):
        fileContent = import_collection(fileName)
        archive = Collection(fileContent[0], fileContent[1])
    else:
        print "File not found."
        exit()


def import_collection(localFile):
    """
    Imports a JSON file from the given localFile filepath.
    The content should be a dict in the ElasticSearch-friendly
    format.
    -   localFile should be a string containing the
        path to a certain local .json file.
    """
    content = json.loads(open(localFile, "rb").read())

    for k, v in content.iteritems():
        print "Imported: %s, %d articles" % (k, len(v))
        return k, v


def build_new_archive(archiveName, noDays):
    urls = scrape_urls(noDays, date)
    noArticles = len(urls)

    archive = Collection(archiveName)

    for articleNo, url in enumerate(urls):
        print "Processing article %d of %d..." % (articleNo+1, noArticles)
        article = Article(url)
        archive.add_article(article)

def scrape_urls(noDays, date):
    """ 
    Scrapes the NOS "archief" page for article urls
    for a set amount of days. Returns a list named 
    "urls" containing all found article urls.
    -   noDays should be an integer, ranging from 1.
    -   date should be datetime.today().
    """
    date = datetime.today()

    urls = []

    for i in xrange(0, noDays):

        # properly format date
        year = str(date.year)
        month = "%02d" % date.month
        day = "%02d" % date.day

        page = "http://nos.nl/nieuws/archief/" + year + "-" + month + "-" + day

        # get all links from this day's webpage
        archief = opener.open(page).read()
        links = re.findall(r'<li class="list-time__item"><a href="(.*?)" class="link-block">', archief)

        for link in links:
            link = "http://nos.nl" + link
            urls.append(link)

        # go one day back in time
        date = date - timedelta(days=1)

    print str(len(urls)) + " urls scraped from past " + str(noDays) + " days."
    return urls

# execute main
if __name__ == "__main__":
    main()
