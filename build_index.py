#!/usr/bin/env python

import os.path
import json
from datetime import datetime, date, timedelta
from urllib2 import urlopen
import cookielib, urllib2
from cookielib import CookieJar
import re
from classes import Article, Collection

# needed for scraper to open link
cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

# name of exported news archive
archiveName = "archive.json"

# if you want to create an index from a
# local file, give correct filepath here
localArchive =  "/Users/simonverhoek/Google Drive/Studie/Web search/Project/nosrecommender/" + archiveName

# set number of days back in time to
# be scraped. If set to 1, only today's
# archive is scraped.
noDays = 1


def main():
    print
    print "===== STEP 1: GETTING A NEWS ARCHIVE ====="
    print
    """
    Get a list of urls to NOS news articles
    to build an archive.
    """
    """ 
    OPTION 1: import a list of urls from a
    local .json file.
    """

    """ 
    OPTION 2: scrape the NOS news archive 
    """
    if check_file_existence(archiveName) == True:
        # import json file
        fileContent = import_collection(archiveName)
        name = fileContent.keys()[0]

        # create Collection instance
        archive = Collection(name, fileContent.values()[0])
    else:
        # scrape website for urls
        urls = scrape_urls(noDays, date)
        # create Collection instance
        # for every found url 
            # create Article instance
            # add article to collection
        print urls


    #newsArchive = getData(scrapeUrls(noDays, date), articleListName)

    # directly export it for later use
    #exportJson(newsArchive, archiveName)


def check_file_existence(fileName):
    """
    Checks if a certain file exists.
    -   fileName should be a string containing
        the name of a JSON file with therein
        a list strings of urls.
    """    
    if os.path.isfile(fileName):
        print
        print 'File named "' + fileName + '" found.'
        return True
    else:
        return False


def import_collection(localFile):
    """
    Imports a JSON file from the given localFile filepath.
    The content should be a dict in the ElasticSearch-friendly
    format.
    -   localFile should be a string containing the
        path to a certain local .json file.
    """
    content = json.loads(open(localFile, "rb").read())

    print "Imported content from " + localFile + "."
    return content  


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
