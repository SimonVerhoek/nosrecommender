#!/usr/bin/env python

from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup
from urllib2 import urlopen
import json

from classes import Article, Collection

# If you want to create an index without a
# local file, set the name for the index here:
# WARNING:  name should be lowercase and without
#           spaces!
archiveName = "nosarchive"

# set number of days back in time to
# be scraped. If set to 1, only today's
# archive is scraped.
noDays = 1

def main():
	""" 
    Scrape the NOS archive for articles
    """
	archive = build_new_archive(archiveName, noDays)

	""" 
    Export the built archive to a JSON file.
    """
	export_json(archive)


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

    Collection.display_articleCount(archive)
    return archive


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


def export_json(archive):
    """ 
    Exports the inserted object to a .json file.
    -   articles should be a dictionary.
    -   outputFileName should be a string.
    """
    fileName = archive.keys()[0]

    outFile = open(fileName + ".json", "w+")
    json.dump(archive, outFile, indent = 4)
    outFile.close()

    print "Exported articles to " + fileName + ".json."
    print


# execute main
if __name__ == "__main__":
    main()
