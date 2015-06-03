#!/usr/bin/env python

# needed by all classes
from bs4 import BeautifulSoup
from urllib2 import urlopen

# needed by Collection class only
from pyes import *

import json
from os import path, chdir, getcwd, pardir
dir = path.dirname(__file__)

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
		self["categories"] = ""
		for count, item in enumerate(soup.find_all(categoriesTag["type"], {
					categoriesTag.keys()[1]:categoriesTag.values()[1]
				})):
			if item.string in possibleCategories:
				if count > 0:
					# only add comma from second category on
					self["categories"] += "," 
				self["categories"] += item.string

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

	def __init__(self, collection):
		"""
		Instantiates a {key: value} archive dict.
		"""
		if type(collection) is str:
			"""
			When just a string is passed
			"""
			self.colName = collection
			self.__setitem__(self.colName, [])

		elif type(collection) is dict:
			"""
			When a dict with already existing articles
			in it is passed
			"""
			self.colName = collection.keys()[0]
			self.__setitem__(self.colName, [])

			for article in collection.values()[0]:
				self.add_article(article)

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
		# create a connection with ElasticSearch
		connection = ES('localhost:9200')

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
		# create a connection with ElasticSearch
		connection = ES('localhost:9200')

		for article in self[self.colName]:
			connection.index(article, self.colName, "test-type")

		print 'Articles added to "' + self.colName + '" in ElasticSearch.'
		print

	def remove_index(self):
		"""
		Removes the index of this news archive instance
		from ElasticSearch.
		"""
		# create a connection with ElasticSearch
		connection = ES('localhost:9200')
		
		try:
			connection.indices.delete_index(self.colName)
			print "index", self.colName, "removed from ElasticSearch."
		except:
			pass


	def import_from_json(self, fileName):
		"""
		DEPRECATED - replaced by import_collection function in
		functions.py

		Imports a collection from a JSON file.
		If no file is found, program is exited.
		- 	fileName should be a string with the name of 
			a JSON file, WITHOUT the ".json" extension.
		"""
		print 'Attempting to import from "files/' + fileName + '"...'
		
		fileName += ".json"
		chdir("files")

		if path.isfile(fileName):
			content = json.loads(open(fileName, "rb").read())

			for k, v in content.iteritems():
				print "Imported: %s, %d articles" % (k, len(v))
				print

			# assign content to Collection instance
			self.colName = content.keys()[0]
			for article in content.values()[0]:
				self.add_article(article)

			chdir(pardir)
		else:
			print "File not found."
			exit()

	def export_to_json(self):
		"""
		DEPRECATED - replaced by export_collection function in
		functions.py

		Exports collection to a JSON file.
		The name of the collection will be given as a filename.
		The file is stored in the "files" subdirectory.
		"""
		chdir("files")

		outFile = open(self.colName + ".json", "w+")
		json.dump(self, outFile, indent = 4)
		outFile.close()

		chdir(pardir)

		print "Exported collection to files/%s.json." % self.colName
		print

	def display_collection(self):
		print "Collection:", self

	def display_colName(self):
		print "Name of collection:", self.colName

	def display_colCount(self):
		print "Number of collections:", Collection.colCount

	def display_articleCount(self):
		print "Number of articles in %s: %d" %(self.colName, len(self[self.colName])) 


class Query(dict):
	queryType = ""

	def __init__(self, *args, **kwargs):
		self.__setitem__(self.queryType, {})

	def add_occurrence(self, occurence):
		"""
		Adds a new occurence to the query.
		Possible options (string):
		-	must
		- 	should
		- 	must_not
		"""
		self[self.queryType].__setitem__(occurence, [])

	def add_match_query(self, matchType, key, value):
		"""
		Adds a new match query to current occurrence.
		"""
		newMatch = {matchType: {key: value}}
		self[self.queryType].values()[0].append(newMatch)


class Bool(Query):
	queryType = "bool"
		







