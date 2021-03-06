#!/usr/bin/env python

from bs4 import BeautifulSoup
from urllib2 import urlopen

# import settings
from settings.article_settings import (
	possibleCategories, 
	titleTag, 
	categoriesTag, 
	textTag, 
	imageTag
)
from settings.index_settings import setting, mapping

class Article(dict):
	"""
	Creates a dict for news articles.
	A string containing a url is mandatory for 
	instantiating an article. Supported attributes
	are preset without a value, as shown in global
	attribute 'defaults'. One can override these values
	by adding extra input arguments as key = "value". 
	The "value" then overrides the default value of 'None'.

	If an instance is found to lack information (one of the
	values == None), this is automatically scraped from the
	given url.

	This class supports the following metadata:
	- title (string)
	- categories (list of one or more strings)
	- body text (string)
	- image (string)
	"""
	articleCount = 0

	defaults = {
		"title": None,
		"categories": None,
		"body": None,
		"image": None
	}

	def __init__(self, url, **kwargs):
		self.__setitem__("url", url)
		self.update(Article.defaults)

		# if any other values found, 
		# replace default value
		for key, value in kwargs.items():
			self.update(kwargs)

		Article.articleCount += 1

		# check if no data is missing
		self.check_completeness()


	def check_completeness(self):
		""" 
		Checks if no data is missing.
		If any tag is missing, its data is scraped from the
		article website.
		""" 
		itemsToScrape = []
		for key, value in self.items():
			if value == None:
				itemsToScrape.append(key)
		if len(itemsToScrape) > 0:
			self.scrape(itemsToScrape)
		

	def scrape(self, *args):
		soup = BeautifulSoup(urlopen(self["url"]))

		scraped = []

		# extract list from tuple
		args = args[0]

		if "title" in args:
			try:
				self.scrape_title(soup)
				scraped.append("title")
			except:
				print "Scraping title failed."
		if "categories" in args:
			try:
				self.scrape_categories(soup)
				scraped.append("categories")
			except:
				print "Scraping categories failed."
		if "body" in args:
			try:
				self.scrape_body(soup)
				scraped.append("body text")
			except:
				print "Scraping body text failed."
		if "image" in args:
			try:
				self.scrape_image(soup)	
				scraped.append("image")
			except:
				print "Scraping image failed."	

		print "Scraped:", ", ".join(scraped)

	def scrape_title(self, soup):
		self["title"] = soup.find(titleTag["type"], {
					titleTag.keys()[1]:titleTag.values()[1]
				}).text

	def scrape_categories(self, soup):
		self["categories"] = []
		for item in soup.find_all(categoriesTag["type"], {
					categoriesTag.keys()[1]:categoriesTag.values()[1]
				}):
			if item.string in possibleCategories:
				self["categories"].append(item.string)

	def scrape_body(self, soup):
		self["body"] = ""
		for paragraph in soup.find_all(textTag["type"]):
			self["body"] += paragraph.text
			
	def scrape_image(self, soup):
		self["image"] = soup.find(imageTag["type"], {
			imageTag.keys()[1]:imageTag.values()[1]
		}).get("src")

			
		

	def display_articleCount(self):
		print "Number of articles instantiated:", Article.articleCount

	def display_article(self):
		for key, value in self.items():
			print key, "=", value
		


from pyes import *

# create a connection with ElasticSearch
connection = ES('localhost:9200')

class Collection(dict):
	"""
	Creates ElasticSearch-friendly news archive.
	Product looks like this:
	{colName: listofarticles}, where:
	-	colName = a string with the name of the archive.
		Is also the index name in ElasticSearch.
	-	listofarticles = a list containing at least one
		article dict (so like this: [{article1},...] )
	"""
	colCount = 0

	colName = ""

	def __init__(self, key, value=[]):
		"""
		Instantiates a {key: value} archive dict.
		"""
		self.colName = key
		self.__setitem__(key, value)
		Collection.colCount += 1

	def add_article(self, article):
		"""
		Adds a given article to the instance
		article list.
		- article should be a dict of an article.
		"""
		self[self.colName].append(article)

	def build_index(self):
		"""
		Builds index for news archive in ElasticSearch.
		-   mapping should be a dictionary containing
        	the inner details of the ElasticSearch
        	index.
    	-   setting should be a dictionary containing
        	the settings for the ElasticSearch index
        	to be initialised.
		"""
		try:
			connection.indices.delete_index(self.colName)
			print 'Index with name "' + self.colName + '" already in Elasticsearch, removed it.'
		except:
			pass

		connection.indices.create_index(self.colName, setting)
		connection.indices.put_mapping("test_type", {'properties':mapping}, [self.colName])
		print 'Index with name "' + self.colName + '" added to ElasticSearch.'
		print

	def index_articles(self):
		"""
		Adds all articles of instance to
		ElasticSearch index.
		"""
		for article in self[self.colName]:
			connection.index(article, self.colName, "test-type")

		print 'Articles added to "' + self.colName + '" in ElasticSearch.'
		print

	def remove_index(self):
		"""
		Removes the index of this news archive instance
		from ElasticSearch.
		"""
		try:
			connection.indices.delete_index(self.colName)
			print "index", self.colName, "removed from ElasticSearch."
		except:
			pass

	def display_collection(self):
		print "Collection:", self

	def display_colName(self):
		print "Name of collection:", self.colName

	def display_colCount(self):
		print "Number of collections:", Collection.colCount

	def display_articleCount(self):
		print "Number of articles in %s: %d" %(self.colName, len(self[self.colName])) 

