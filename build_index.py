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
    print "===== STEP 1: BUILDING A NEWS ARCHIVE ====="
    print
    if check_file_existence(archiveName) == True:
        """ 
        OPTION 1: import a list of urls from a
        local .json file.
        filecontent[0] = collection name
        filecontent[1] = list of articles in file.
        """
        fileContent = import_collection(archiveName)
        archive = Collection(fileContent[0], fileContent[1]) 
    else:
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
        urls = scrape_urls(noDays, date)
        noArticles = len(urls)

        archive = Collection("test")

        for articleNo, url in enumerate(urls):
            print "Processing article %d of %d..." % (articleNo+1, noArticles)
            article = Article(url)
            archive.add_article(article)
            articleNo += 1

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

    for k, v in content.iteritems():
        print "Imported: %s, %d articles" % (k, len(v))
        return k, v


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
