#!/usr/bin/env python

__author__      = "Henk van Appeven, Simon Verhoek"
__maintainer__  = "Simon Verhoek"
__status__      = "Development"

from datetime import datetime, date, timedelta
from urllib2 import urlopen
import re
import cookielib, urllib2
from cookielib import CookieJar
import json

# needed for scraper to open link
cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

# create a connection with ElasticSearch
from pyes import *
connection = ES('localhost:9200')

# index name as seen in ElasticSearch
indexName = "testindex"

# name of exported file
outputFileName = "output"

# if you want to create an index from a
# local file, give correct filepath here
filePath = "/Users/simonverhoek/Google Drive/Studie/Web search/Project/nosrecommender/output.json"

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


# prepare index object
articleListName = "NOS Nieuws"
articleList = []
articles = {articleListName: articleList}

# get days to scrape
date = datetime.today()

days = []

# prepare links
newLinks = []

noDays = 1

for i in xrange(0, noDays):
    
    year = str(date.year)
    month = "%02d" % date.month
    day = "%02d" % date.day

    page = "http://nos.nl/nieuws/archief/" + year + "-" + month + "-" + day

    # get all links from this day's webpage
    archief = opener.open(page).read()
    links = re.findall(r'<li class="list-time__item"><a href="(.*?)" class="link-block">', archief)

    for link in links:
        link = "http://nos.nl" + link
        newLinks.append(link)

    # go one day back in time
    date = date - timedelta(days=1)






def getData(links, articleListName):
    """ 
    Scrapes the NOS "archief" page for articles.
    Returns an ElasticSearch-friendly JSON-object
    containing all the data of all articles.
    -   articleListName should be a string.
    -   links should be an array of article urls
        in string form.
    -   exportType should be a string containing 
        either "json" or "csv". Can be selected 
        at the top of this document under "choose
        export format".
    """
    # get content
    for i, link in enumerate(links):

        noLinks = len(links)

        linkSource = opener.open(link).read()

        articleType = re.findall(r'<article class="(.*?)">', linkSource)
        articleType = articleType[0]

        # filter out other article types as their content
        # is in other html elements, making it unfindable
        if articleType != "article":
            print "Incompatible article type -- passed."
            continue

        # scrape content
        titles = re.findall(r'class="article__title">(.*?)</h1>', linkSource)
        title = titles[0]
        categories = re.findall(r'class="link-grey">(.*?)</a>', linkSource)
        # if article contains multiple categories, put them in a 
        # single string with commas inbetween so ES can read all of them
        categories = ",".join(categories)
        paragraphs = re.findall(r'<p>(.*?)</p>', linkSource)
        images = re.findall(r'http://www.nos.nl/data/image/(.*?)jpg', linkSource)
        # check if article contains header image
        if len(images) >= 1:
            # assumes header is always the first <img> file in html doc
            image = "http://www.nos.nl/data/image/" + str(images[0]) + "jpg"
        else:
            image = "none"

        # concatenate multiple paragraphs of body text
        # into one string
        body = ""
        for paragraph in paragraphs:
            body += paragraph

        # print progress in terminal
        articleNo = str(i + 1)
        print "processing article " + articleNo + " of " + str(noLinks) + "..."

        # create article dict
        article = {}

        article["url"] = link
        article["title"] = title
        article["categories"] = categories
        article["body"] = body
        article["image"] = image

        # add article dict to list of articles
        articleList.append(article)

    print "All articles processed!"
    return articles


def importJson(filePath):
    """
    Imports the JSON file from the given filepath
    and returns this as an ElasticSearch-friendly
    JSON object named "articles".
    -   filePath should be a string containing the
        path to a certain local .json file.
    """
    print "Importing articles from " + filePath + "..."
    articles = json.loads(open(filePath, "rb").read())
    return articles


def exportJson(articles, outputFileName):
    """ 
    Exports the inserted object to a .json file.
    -   articles should be an ElasticSearch-friendly
        JSON object.
    -   articleListName should be a string.
    """
    outFile = open(outputFileName + ".json", "w")
    json.dump(articles, outFile, indent = 4)
    outFile.close()

    print "Exported articles to " + outputFileName + ".json."


def exportCsv(articles, outputFileName):
    """ 
    Exports the inserted object to a .csv file.
    -   articles should be an object.
    -   articleListName should be a string.
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


def createIndex(indexName, connection, mapping, setting):
    """ 
    creates an index in ElasticSearch.
    -   indexName should be a string.
    -   filePath should be a string containing the
        path to a certain (json) file.
    -   connection should be a string containing 
        the local ip address:port to the local
        ElasticSearch server.
    -   mapping should be a dictionary containing
        the inner details of the ElasticSearch
        index.
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


"""
Call functions here
"""
# choose to either scrape the website or 
# import from a local JSON file
getData(newLinks, articleListName)
#importJson(filePath)

# create an index in ElasticSearch
#createIndex(indexName, connection, mapping, setting)
#addToIndex(indexName, connection, articles)

# export data to either JSON or CSV file
exportJson(articles, outputFileName)
#exportCsv(articles, outputFileName)

