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
from bs4 import BeautifulSoup
import os.path
import time

# needed for scraper to open link
cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
 
# input arguments for checkIfFileExists().
interval = 1                        # in seconds
historyFileName = "urlsonly.json"   # name of file

# create a connection with ElasticSearch
connection = ES('localhost:9200')

# index name as seen in ElasticSearch
indexName = "testindex"

# prepare index object
articleListName = "NOS Nieuws"
articleList = []
articles = {articleListName: articleList}

urls = []

# set number of days back in time to
# be scraped. If set to 1, only today's
# archive is scraped.
noDays = 2

# location of HTML file to open in which
# recommended articles will be shown
recommendationsPage = "index.html"

# if you want to create an index from a
# local file, give correct filepath here
localFile = "/something/something/file.json"

# name of exported file
outputFileName = "output"

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
                            "term_vector" : "with_positions_offsets"},
            u'body': {      'boost': 1.0,
                            'index': 'analyzed',
                            'store': 'yes',
                            'type': u'string',
                            "similarity": "BM25",
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

def main():
    """
    STEP 1: GETTING A NEWS ARCHIVE

    Get a list of urls to NOS news articles
    to build an archive.
    """
    """ 
    EITHER: scrape the NOS news archive 
    """
    urls = scrapeUrls(noDays, date)
    newsArchive = getData(urls)

    """ 
    OR: import a list of urls from a
    local .json file.
    """
    #importJson(localFile)

    """
    STEP 2: INDEXING THE NEWS ARCHIVE

    Create an index in ElasticSearch, and add
    the news archive to this.
    -   Once an index of the given name already exists, 
        initialising a new one will replace the current
        one. 
    -   When no new index is initialised, the results of
        addToIndex will be appended to the existing index.
        WARNING: this may result into duplicate entries!
    """
    initIndex(indexName, connection, mapping, setting)
    addToIndex(indexName, connection, newsArchive)

    """
    STEP 3: GETTING THE USER'S BROWSING HISTORY
    
    Grab a local .json file from your computer,
    containing the urls visited by the user.
    """
    browsingHistory = getBrowsingHistory(interval, historyFileName)

    """
    STEP 4: GETTING THE RECOMMENDED ARTICLES
    
    Let ElasticSearch compare the user's browsing
    history with its news archive, and recommend you
    the most relevant new articles.
    """
    recommendedArticles = getRecommendedArticles(browsingHistory, articleListName)

    """
    STEP 5: SHOWING THE RECOMMENDED ARTICLES TO THE USER

    Add articles to recommendations HTML page
    """
    #addRecommendations(articles, articleListName, recommendationsPage)
    
    """
    If you want to export the articles,
    you can choose to do so here.
    """
    #exportJson(articles, outputFileName)
    #exportCsv(articles, outputFileName)


def getBrowsingHistory(interval, historyFileName):
    """
    Starts a timer to check periodically for
    a JSON file with urls visited by the user.
    Restarts itself until a file is found.
    If a file is found, it gets the content of 
    the given urls.
    -   interval should be an integer in 
        seconds.
    -   historyFileName should be a string containing
        the name of a JSON file with therein
        a list strings of urls.
    """    
    time.sleep(interval)

    if checkIfFileExists(historyFileName) == False:
        print "Waiting for file with browsing history..."
        getBrowsingHistory(interval, historyFileName)
    else:
        return getData(importJson(historyFileName))


def checkIfFileExists(fileName):
    """
    Checks if a certain file exists.
    -   fileName should be a string containing
        the name of a JSON file with therein
        a list strings of urls.
    """    
    if os.path.isfile(fileName):
        print 'File named "' + fileName + '" found.'
        return True
    else:
        return False


def getRecommendedArticles(visitedArticles, articleListName):
    """
    Gets recommended news articles. Compares 
    visitedArticles to an ElasticSearch index.
    Returns a dictionary with the results.
    -   visitedArticles should be an ElasticSearch-friendly
        dictionary containing the articles visited
        by the user.
    -   articleListName should be a string.
    """   
    query = []
    for i in visitedArticles[articleListName]:
        query.append({"match" :{"title": i["title"]}})
        query.append({"match": {"body": i["body"]}})
        query.append({"match": {"categories":i["categories"]}})

    q = {"bool": {"should": query}} 
    results = connection.search(query = q, index = "nos_rss_dutch3")

    print "recommended articles:"
    for result in results[:10]:
        print result["url"]


def scrapeUrls(noDays, date):
    """ 
    Scrapes the NOS "archief" page for article urls
    for a set amount of days. Returns a list named 
    "urls" containing all found article urls.
    -   noDays should be an integer, ranging from 1.
    -   date should be datetime.today().
    """
    date = datetime.today()

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


def getData(urls):
    """ 
    Scrapes the NOS "archief" page for the content
    of the articles of the given urls.
    Returns an ElasticSearch-friendly JSON-object
    containing all the data of all articles.
    -   urls should be a list containing strings
        with urls to NOS news articles.
    """
    noUrls = len(urls)

    # get content
    for i, link in enumerate(urls):

        # print progress in terminal
        articleNo = str(i + 1)
        print "Scraping article " + articleNo + " of " + str(noUrls) + "..."

        linkSource = opener.open(link).read()

        articleType = re.findall(r'<article class="(.*?)">', linkSource)
        articleType = articleType[0]

        # filter out other article types as their content
        # is in other html elements, making it unfindable
        if articleType != "article":
            print "Incompatible article type -- passed."
            continue

        # scrape raw content
        titles = re.findall(r'class="article__title">(.*?)</h1>', linkSource)
        categories = re.findall(r'class="link-grey">(.*?)</a>', linkSource)       
        paragraphs = re.findall(r'<p>(.*?)</p>', linkSource)
        images = re.findall(r'http://www.nos.nl/data/image/(.*?)jpg', linkSource)

        # clean content
        title = cleanContent("title", titles)
        categories = cleanContent("categories", categories)
        body = cleanContent("body", paragraphs)
        image = cleanContent("image", images)

        # create article dict
        article = {}

        article["url"] = link
        article["title"] = title
        article["categories"] = categories
        article["body"] = body
        article["image"] = image

        # add article dict to list of articles
        articleList.append(article)

    print "All articles scraped!"
    return articles

def cleanContent(contentType, content):
    """ 
    Cleans the given content. How exactly the
    it is cleaned, may differ per given content. 
    Returns cleaned content.
    -   contentType should be a string.
    -   exportType should be a string containing 
        either "json" or "csv". Can be selected 
        at the top of this document under "choose
        export format".
    """
    if contentType == "title":
        title = content[0]
        title = title.replace("&#039;", " ")
        return title

    elif contentType == "categories":
        # if article contains multiple categories, put them in a 
        # single string with commas inbetween so ES can read all of them
        categories = ",".join(content)
        return categories

    elif contentType == "body":
        # concatenate multiple paragraphs of body text
        # into one string
        body = ""
        for paragraph in content:
            body += paragraph
        # strip any HTML tags from body
        body = stripHtml(body)
        return body

    elif contentType == "image":
        # check if article contains header image
        if len(content) >= 1:
            # assumes header is always the first <img> file in html doc
            image = "http://www.nos.nl/data/image/" + str(content[0]) + "jpg"
        else:
            image = "none"
        return image

    else:
        raise ValueError("Missing cleaning instructions for one or more types of content.")


def stripHtml(text):
    """
    Strips any HTML elements from a given string
    text, and returns this as cleanText
    -   text
    """
    cleanr = re.compile('<.*?>')
    cleanText = re.sub(cleanr,'', text)
    return cleanText


def importJson(localFile):
    """
    Imports the JSON file from the given localFile
    and returns this as an ElasticSearch-friendly
    JSON object named "articles".
    -   localFile should be a string containing the
        path to a certain local .json file.
    """
    print "Importing content from " + localFile + "..."
    content = json.loads(open(localFile, "rb").read())
    return content


def initIndex(indexName, connection, mapping, setting):
    """ 
    creates an index in ElasticSearch.
    -   indexName should be a string.
    -   connection should be a string containing 
        the local ip address:port to the local
        ElasticSearch server.
    -   mapping should be a dictionary containing
        the inner details of the ElasticSearch
        index.
    -   setting should be a dictionary containing
        the settings for the ElasticSearch index
        to be initialised.
    """
    # if index of this name already exists, delete it
    try:
        connection.indices.delete_index(indexName)
    except:
        pass

    # create index and its mapping
    connection.indices.create_index(indexName, setting)
    connection.indices.put_mapping("test_type", {'properties':mapping}, [indexName])
    print 'Index with name "' + indexName + '" created.'


def addToIndex(indexName, connection, articles):    
    """ 
    Adds a given dictionary to a given index
    in ElasticSearch.
    -   indexName should be a string containing
        the name of an existing index in 
        ElasticSearch.
    -   connection should be a string containing 
        the local ip address:port to the local
        ElasticSearch server.
    -   articles should be an ElasticSearch-friendly
        JSON object of the mapping described at 
        the top of this document.
    """
    for i in articles[articleListName]:
        connection.index({  "title":i["title"],
                            "categories":i["categories"],
                            "body":i["body"], 
                            "url":i["url"]}, 
                            indexName, "test-type")

    print '"' + articleListName + '" articles added to index.'


def addRecommendations(articles, articleListName, recommendationsPage):
    """
    Adds articles to the recommendations HTML page.
    -   articles should be an ElasticSearch-friendly
        JSON object.
    -   articleListName should be a string.
    -   recommendationsPage should be a string containing the 
        path to the HTML file in which to paste the 
        recommended articles.
    """
    for article in articles[articleListName]:

        # article format
        articleBlock = [ 
            "<li class='list-item space-bottom-xl'>",
            '<a href="' + article["url"] + '" class="link-block">',
            "<div class='list-left-content link-reset'>",
            '<h3 class="list-left-title link-hover">' + article["title"] + '</h3>',
            '<div class="meta">',
            '<time datetime="2015-03-06T12:13:48+0100">12:13</time>',
            "<span class='hide-small'>in Binnenland</span>",
            "</div>",
            "</div>",
            '<figure class="list-image">',
            '<img src="' + article["image"] + '" alt="" class=""/>',
            '</figure>',
            "</a>",
            "</li>" ]

        # open html file
        htmlDoc = open(recommendationsPage)
        soup = BeautifulSoup(htmlDoc)

        # find correct <ul> tag
        indexArticleList = soup.find("ul", {"class":"list-vertical padded-small"})

        # append index file with all strings inside article[]
        for elements in articleBlock:
            indexArticleList.append(elements)

        # correctly format html tags
        html = soup.prettify(formatter=None)

        htmlDoc.close()

        # overwrite index file
        with open(recommendationsPage, "wb") as file:
            # file is encoded to prevent "'ascii' codec can't 
            # encode character [...] in position [...]: 
            # ordinal not in range([...])" error
            file.write(html.encode("utf-8"))

    print str(len(articles[articleListName])) + " new articles recommended."


def exportJson(articles, outputFileName):
    """ 
    Exports the inserted object to a .json file.
    -   articles should be a dictionary.
    -   outputFileName should be a string.
    """
    outFile = open(outputFileName + ".json", "w")
    json.dump(articles, outFile, indent = 4)
    outFile.close()

    print "Exported articles to " + outputFileName + ".json."


def exportCsv(articles, outputFileName):
    """ 
    Exports the inserted object to a .csv file.
    -   articles should be a dictionary.
    -   outputFileName should be a string.
    """
    csv = open(outputFileName + ".csv", "a+")

    for article in articles[articleListName]:
        csv.write("\n")
        csv.write(article["url"])
        csv.write(",")        
        csv.write(article["title"])
        csv.write(",")
        for category in article["categories"]:
            csv.write(category)
        csv.write(",")
        csv.write(article["body"])
        csv.write(",")
        csv.write(article["image"])

    print "Exported articles to " + outputFileName + ".csv."

# execute main
if __name__ == "__main__":
    main()
