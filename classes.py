#!/usr/bin/env python

from bs4 import BeautifulSoup
from urllib2 import urlopen

from scraper import *

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
		self.scrape(itemsToScrape)
		

	def scrape(self, *args):
		soup = BeautifulSoup(urlopen(self["url"]))

		# extract list from tuple
		args = args[0]

		if "title" in args:
			self.scrape_title(soup)
		if "categories" in args:
			self.scrape_categories(soup)
		if "body" in args:
			self.scrape_body(soup)
		if "image" in args:
			self.scrape_image(soup)		

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

class Archive(dict):
	"""
	Creates ElasticSearch-friendly news archive.
	Product looks like this:
	{archiveName: listofarticles}, where:
	-	archiveName = a string with the name of the archive.
		Is also the index name in ElasticSearch.
	-	listofarticles = a list containing at least one
		article dict (so like this: [{article1},...] )
	"""
	archiveCount = 0

	archiveName = ""

	def __init__(self, key, value):
		"""
		Instantiates a {key: value} archive dict.
		"""
		self.archiveName = key
		self.__setitem__(key, value)
		Archive.archiveCount += 1

	def add_article(self, article):
		"""
		Adds a given article to the instance
		article list.
		- article should be a dict of an article.
		"""
		self[self.archiveName].append(article)

	def build_index(self, setting, mapping):
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
			connection.indices.delete_index(self.archiveName)
			print 'Index with name "' + self.archiveName + '" already in Elasticsearch, removed it.'
		except:
			pass

		connection.indices.create_index(self.archiveName, setting)
		connection.indices.put_mapping("test_type", {'properties':mapping}, [self.archiveName])
		print 'Index with name "' + self.archiveName + '" added to ElasticSearch.'
		print

	def index_articles(self):
		"""
		Adds all articles of instance to
		ElasticSearch index.
		"""
		for article in self[self.archiveName]:
			connection.index(article, self.archiveName, "test-type")

		print 'Articles added to "' + self.archiveName + '" in ElasticSearch.'
		print

	def remove_index(self):
		"""
		Removes the index of this news archive instance
		from ElasticSearch.
		"""
		try:
			connection.indices.delete_index(self.archiveName)
			print "index", self.archiveName, "removed from ElasticSearch."
		except:
			pass

	def display_archive(self):
		print "index:", self

	def display_archiveName(self):
		print "archiveName:", self.archiveName

	def display_archiveCount(self):
		print "Number of indices:", Archive.archiveCount

	def display_articleCount(self):
		print "Number of articles:", len(self[self.archiveName])

