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

# create a connection with ElasticSearch
from pyes import *
connection = ES('127.0.0.1:9200')
connection = ES('localhost:9200')

# ElasticSearch data
indexName = "articleindex"
filePath = "/Users/simonverhoek/Desktop/output 2.json"

# choose export format
exportType = "json"
#exportType = "csv"

# needed for scraper to open link
cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

page = 'http://nos.nl/nieuws/archief'
archief = opener.open(page).read()

outputFileName = "output"

# this is how the index will be named in ElasticSearch
articleListName = "NOS Nieuws"

links = re.findall(r'<li class="list-time__item"><a href="(.*?)" class="link-block">', archief)

articleList = []
articles = {articleListName: articleList}

# prepare links
newLinks = []
for link in links:
    link = "http://nos.nl" + link
    newLinks.append(link)

def export(links, articleListName, exportType):
    """ 
    Exports scraped data as either a .csv file or
    an ElasticSearch-friendly JSON object. 
    -   articleListName should be a string.
    -   links should be an array of article urls
        in string form.
    -   exportType should be a string containing 
        either "json" or "csv". Can be selected 
        at the top of this document under "choose
        export format".
    """

    # open appropriate file(type)
    if exportType == "json":
        outFile = open(outputFileName + ".json", "w")
    elif exportType == "csv":
        csv = open(outputFileName + ".csv", "a+")

    # get content
    for i, link in enumerate(links):

        noLinks = len(links)

        linkSource = opener.open(link).read()

        articleType = re.findall(r'<article class="(.*?)">', linkSource)
        articleType = articleType[0]

        # determine article type
        if articleType == "article":
            titles = re.findall(r'class="article__title">(.*?)</h1>', linkSource)
            title = titles[0]
            categories = re.findall(r'class="link-grey">(.*?)</a>', linkSource)
            paragraphs = re.findall(r'<p>(.*?)</p>', linkSource)
            images = re.findall(r'http://www.nos.nl/data/image/(.*?)jpg', linkSource)
            # check if article contains header image
            if len(images) >= 1:
                # assumes header is always the first <img> file in html doc
                image = "http://www.nos.nl/data/image/" + str(images[0]) + "jpg"
            else:
                image = "none"


        elif articleType == "liveblog-page":
            # filter out liveblog articles as their content
            # is in other html elements, making them unfindable
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

        # write data to file
        if exportType == "json":
            article = {}
            article["url"] = link
            article["title"] = title
            article["categories"] = categories
            article["body"] = body
            article["image"] = image

            # add article dict to list of articles
            articleList.append(article)

            if i == noLinks-1:
                # write JSON object to file
                json.dump(articles, outFile, indent = 4)
                outFile.close()
                print "export to " + outputFileName + ".json complete!"  
                return articles

        elif exportType == "csv":
            csv.write("\n")
            csv.write(link)
            csv.write(",")        
            csv.write(title)
            csv.write(",")
            for category in categories:
                csv.write(category)
            csv.write(",")
            csv.write(body)
            if i == noLinks-1:
                print "export to " + outputFileName + ".csv complete!"



def createIndex(indexName, filePath, connection, articles):
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

    connection.indices.create_index(indexName)

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
                u'body': {  'boost': 1.0,
                            'index': 'analyzed',
                            'store': 'yes',
                            'type': u'string',
                            "term_vector" : "with_positions_offsets"}}

    connection.indices.put_mapping("test_type", {'properties':mapping}, [indexName])

    #data = json.loads(open(filePath, "rb").read())

    for i in articles["NOS Nieuws"]:
        connection.index({  "title":i["title"],
                            "body":i["body"], 
                            "url":i["url"]}, 
                            indexName, "test-type")

    print "index with name " + indexName + " created!"

# call functions
export(newLinks, articleListName, exportType)
createIndex(indexName, filePath, connection, articles)
