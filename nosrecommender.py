#!/usr/bin/env python

__author__      = "Henk van Appeven, Simon Verhoek"
__maintainer__  = "Simon Verhoek"
__status__      = "Development"

import time
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
#filePath = "/something/something/jsonfile.json"

mapping = { u'url': {   'boost': 1.0,
                        'index': 'analyzed',
                        'store': 'yes',
                        'type': u'string',
                        "term_vector" : "with_positions_offsets"},
            u'title': { 'boost': 1.0,
                        'index': 'analyzed',
                        'store': 'yes',
                        'type': u'string',
                        "term_vector" : "with_positions_offsets"},
            u'title': { 'boost': 1.0,
                        'index': 'analyzed',
                        'store': 'yes',
                        'type': u'string',
                        "term_vector" : "with_positions_offsets"},
            u'body': {  'boost': 1.0,
                        'index': 'analyzed',
                        'store': 'yes',
                        'type': u'string',
                        "term_vector" : "with_positions_offsets"}}

# prepare index object
articleListName = "NOS Nieuws"
articleList = []
articles = {articleListName: articleList}

# get all links from given webpage
page = 'http://nos.nl/nieuws/archief'
archief = opener.open(page).read()
links = re.findall(r'<li class="list-time__item"><a href="(.*?)" class="link-block">', archief)

# prepare links
newLinks = []
for link in links:
    link = "http://nos.nl" + link
    newLinks.append(link)

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
        if articleType == "article":

            titles = re.findall(r'class="article__title">(.*?)</h1>', linkSource)
            title = titles[0]
            categories = re.findall(r'class="link-grey">(.*?)</a>', linkSource)
            # if article contains multiple categories, put them in
            # a single string with commas inbetween so ES can read
            # all of them
            categories = ",".join(categories)
            paragraphs = re.findall(r'<p>(.*?)</p>', linkSource)
            images = re.findall(r'http://www.nos.nl/data/image/(.*?)jpg', linkSource)
            # check if article contains header image
            if len(images) >= 1:
                # assumes header is always the first <img> file in html doc
                image = "http://www.nos.nl/data/image/" + str(images[0]) + "jpg"
            else:
                image = "none"


        elif articleType == "liveblog-page":
            print "liveblog page -- passed."
            continue

        else:
            raise ValueError('found another unspecified article category!')

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

    print "export to " + outputFileName + ".json complete!"


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

    print "export to " + outputFileName + ".csv complete!"


def createIndex(indexName, connection, articles, mapping):
    """ 
    creates an index in ElasticSearch.
    -   indexName should be a string.
    -   filePath should be a string containing the
        path to a certain (json) file.
    -   connection should be a string containing 
        the local ip address:port to the local
        ElasticSearch server.
    -   articles should be a JSON object of the 
        mapping described at ...
    """
    # if index of this name already exists, delete it
    try:
        connection.indices.delete_index(indexName)
    except:
        pass

    # if user declared a local file, create
    # index of that file
    if 'filePath' in globals():
        print "Creating index of " + filePath + "..."
        articles = json.loads(open(filePath, "rb").read())

    # create index and its mapping
    connection.indices.create_index(indexName)
    connection.indices.put_mapping("test_type", {'properties':mapping}, [indexName])

    for i in articles["NOS Nieuws"]:
        connection.index({  "title":i["title"],
                            "categories":i["categories"],
                            "body":i["body"], 
                            "url":i["url"]}, 
                            indexName, "test-type")

    print "Index with name " + indexName + " created!"

# call functions
getData(newLinks, articleListName)
createIndex(indexName, connection, articles, mapping)

# export to either JSON or CSV file
#exportJson(articles, outputFileName)
#exportCsv(articles, outputFileName)

