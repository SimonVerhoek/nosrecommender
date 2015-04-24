#!/usr/bin/env python

import os.path
import json
from datetime import datetime, date, timedelta
from sys import exit
from bs4 import BeautifulSoup
from urllib2 import urlopen

from classes import Article, Collection


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
    OPTION 1: Import an existing archive.
    """
    get_existing_archive(fileName)
        
    """ 
    OPTION 2: Build a new archive.
    """
    #build_new_archive(archiveName, noDays)


def get_existing_archive(fileName):
    """
    Imports an existing archive from a .json file.
    Exits when file is not found.
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
    """
    Builds new archive by scraping the given news website.
    The procedure is as follows: 
    1:  Scrape urls for a set number of days. 
    2:  Instantiate Collection.
    3:  For each url, instantiate Article. The article's
        contents are scraped automatically by the Article 
        class.
    4:  Add article to collection instance.
    """
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
        soup = BeautifulSoup(urlopen(page))
        for link in soup.find_all("a", {"class":"link-block"}):
            # filter out non-article links
            if link["href"][1:8] == "artikel":
                link = "http://nos.nl" + link["href"]
                urls.append(link)

        # go one day back in time
        date = date - timedelta(days=1)

    print str(len(urls)) + " urls scraped from past " + str(noDays) + " days."
    return urls


# execute main
if __name__ == "__main__":
    main()
