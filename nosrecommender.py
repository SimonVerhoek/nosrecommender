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

from classes import Article

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
    #print "Skipped."

    print
    print "===== PRESTEP 2: INDEXING THE NEWS ARCHIVE ====="
    print
    """
    Create an index in ElasticSearch, and add
    the news archive to this.
    """
    createIndex(newsArchive)
    #print "Skipped."

    processBrowsingHistory()

def createIndex(newsArchive):
    """
    Creates an index in ElasticSearch and adds 
    a news archive in one call.
    -   Once an index of the given name already exists, 
        initialising a new one will replace the current
        one. 
    -   When no new index is initialised, the results of
        addToIndex will be appended to the existing index.
        WARNING: this may result into duplicate entries!
    """
    initIndex(indexName, connection, mapping, setting)
    addToIndex(indexName, connection, newsArchive)

def processBrowsingHistory():
    """
    Starts a timer to check periodically for
    a JSON file with urls visited by the user.
    Restarts itself until a file is found.
    If a file is found, it gets the content of 
    the given urls.
    """    
    time.sleep(interval)

    if checkIfFileExists(historyFileName) == True:
        print
        print "===== STEP 1: GETTING THE USER'S BROWSING HISTORY ====="
        print
        """   
        Grab a local .json file from your computer,
        containing the urls visited by the user.
        """
        getBrowsingHistory(historyFileName)
        browsingHistory = getData(visitedUrlsList, articleListName)

        print
        print "===== STEP 2: GETTING THE RECOMMENDED ARTICLES ====="
        print
        """    
        Let ElasticSearch compare the user's browsing
        history with its news archive, and recommend you
        the most relevant new articles.
        """
        recommendedArticles = getRecommendedArticles(browsingHistory, articleListName, noReccomendations)
        checkIfRead(browsingHistory, recommendedArticles)
        
        print
        print "===== STEP 3: SHOWING THE RECOMMENDED ARTICLES TO THE USER ====="
        print
        """
        Add articles to recommendations HTML page
        """
        addRecommendations(recommendedArticles, articleListName, recommendationsPage)

        print
        print "===== BROWSING HISTORY PROCESSED - CYCLE DONE ====="
        print
    else:
        print "Waiting for file with browsing history..."

    if len(visitedUrlsList) >= NoArticlesToBeRead:
        print
        print "===== STEP 4: EXPORTING DATA ====="
        print
        """
        If you want to export the articles,
        you can choose to do so here.
        """
        #print "Nothing exported."
        exportJson(recommendedArticles, outputFileName)
        exportCsv(recommendedArticles, outputFileName)
    else:
        processBrowsingHistory()
    

def getBrowsingHistory(historyFileName):
    """
    Imports JSON file with visited urls, scrapes 
    additional content and returns it in an
    ElasticSearch-friendly dictionary. Deletes
    JSON file after receiving the content.
    -   historyFileName should be a string containing
        the name of a JSON file with therein
        a list strings of urls.
    """                
    visitedUrls = importJson(historyFileName)
    os.remove(historyFileName)

    if type(visitedUrls) == dict:
        visitedUrls = visitedUrls.values()

    visitedUrlsList.extend(visitedUrls)


def checkIfFileExists(fileName):
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


def scrapeUrls(noDays, date):
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


def getData(urls, articleListName):
    """ 
    Scrapes the NOS "archief" page for the content
    of the articles of the given urls.
    Returns an ElasticSearch-friendly JSON-object
    containing all the data of all articles.
    -   urls should be a list containing strings
        with urls to NOS news articles.
    """
    articleList = []
    articles = {articleListName: articleList}

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
        images = re.findall(r'http://nos.nl/data/image/(.*?)jpg', linkSource)

        # clean content
        title = cleanContent("title", titles)
        categories = cleanContent("categories", categories)
        body = cleanContent("body", paragraphs)
        image = cleanContent("image", images)

        # create article class instance
        article = Article(  url = link, 
                            title = title,
                            categories = categories,
                            body = body, 
                            image = image)

        # add article as dict to list of articles
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
            image = "http://nos.nl/data/image/" + str(content[0]) + "jpg"
        else:
            image = "none"
        return image

    else:
        raise ValueError("Missing cleaning instructions for one or more types of content.")


def stripHtml(text):
    """
    Strips any HTML elements from a given string
    text.
    -   text should be a string.
    """
    cleanr = re.compile('<.*?>')
    cleanText = re.sub(cleanr,'', text)
    return cleanText


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
                            "url":i["url"], 
                            "image":i["image"]},
                            indexName, "test-type")

    print '"' + articleListName + '" articles added to index.'
    print


def getRecommendedArticles(visitedArticles, articleListName, noReccomendations):
    """
    Gets recommended news articles. Compares 
    visitedArticles to an ElasticSearch index.
    Returns a dictionary with the results.
    -   visitedArticles should be an ElasticSearch-friendly
        dictionary containing the articles visited
        by the user.
    -   articleListName should be a string.
    """   
    articleList = []
    articles = {articleListName: articleList}
    
    query = []
    
    for i in visitedArticles[articleListName]:
        query.append({"match": {"title": i["title"]}})
        query.append({"match": {"body": i["body"]}})
        query.append({"match": {"categories":i["categories"]}})
        query.append({"match": {"image":i["image"]}})

    q = {"bool": {"should": query}} 
    returns = connection.search(query = q, index = indexName)

    for item in returns[:noReccomendations]:
        # add ES' relevance score
        item["score"] = item._meta.score
        articleList.append(item)

    print str(noReccomendations) + " articles recommended."
    return articles


def checkIfRead(browsingHistory, recommendedArticles):
    """
    Checks if any of the recommended article have
    already been read by the user.
    -   browsingHistory should be an ElasticSearch-friendly
        JSON-object.
    -   recommendedArticles should be a list of strings
        containing the urls of recommended articles.
    """  
    noRemovedArticles = 0

    for visitedPage in browsingHistory[articleListName]:
        for recommendedUrl in recommendedArticles[articleListName]:
            if recommendedUrl["url"] == visitedPage["url"]:
                recommendedArticles[articleListName].remove(recommendedUrl)
                noRemovedArticles += 1
            else:
                pass
    print "removed " + str(noRemovedArticles) + " recommended articles which have already been read."


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
    print 'Writing recommended files to "' + recommendationsPage + '"...'

    # open html file
    htmlDoc = open(recommendationsPage)
    soup = BeautifulSoup(htmlDoc)

    # remove any previously recommended articles
    for li in soup.find_all("li"):
        li.replaceWith("")

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
        file.write(html.encode(encoding))

    print str(len(articles[articleListName])) + " new articles recommended."


def exportJson(articles, outputFileName):
    """ 
    Exports the inserted object to a .json file.
    -   articles should be a dictionary.
    -   outputFileName should be a string.
    """
    outFile = open(outputFileName + ".json", "w+")
    json.dump(articles, outFile, indent = 4)
    outFile.close()

    print "Exported articles to " + outputFileName + ".json."
    print


def exportCsv(articles, outputFileName):
    """ 
    Exports the inserted object to a .csv file.
    -   articles should be a dictionary.
    -   outputFileName should be a string.
    """
    writer = csv.writer(open(outputFileName + ".csv", "w+"))

    writer.writerow(["Titel", "Score"])
    for article in articles[articleListName]: 
        writer.writerow([article["title"].encode(encoding), article["score"]])

    print "Exported articles to " + outputFileName + ".csv."
    print

# execute main
if __name__ == "__main__":
    main()
