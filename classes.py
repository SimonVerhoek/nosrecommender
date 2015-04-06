#!/usr/bin/env python

class Article(dict):
	"""
	Creates a dict for news articles.
	It accepts a variable amount of key-value pairs
	as key = "value".
	"""
	articleCount = 0

	def __init__(self, **kwargs):
		for key, value in kwargs.items():
			self.update(kwargs)

		Article.articleCount += 1

	def displayCount(self):
		print "Number of articles is %d" % Article.articleCount

	def displayArticle(self):
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

