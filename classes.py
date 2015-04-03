#!/usr/bin/env python

class Article(dict):

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

class Index(dict):
	"""
	Creates ElasticSearch-friendly dicts.
	Product looks like this:
	{indexname: listofarticles}, where:
	-	indexname = a string with the name of the index
		how it should appear in ElasticSearch
	-	listofarticles = a list containing at least one
		dict (so like this: [{article1},...] )
	"""
	indexCount = 0

	indexName = ""

	def __init__(self, key, value):
		"""
		Instantiates a {key: value} dict.
		"""
		self.indexName = key
		self.__setitem__(key, value)
		Index.indexCount += 1

	def addArticle(self, article):
		"""
		Adds a given article to the instance
		article list.
		- article should be a dict of an article.
		"""
		self[self.indexName].append(article)

	def build(self, setting, mapping):
		"""
		Builds index in ElasticSearch.
		-   mapping should be a dictionary containing
        	the inner details of the ElasticSearch
        	index.
    	-   setting should be a dictionary containing
        	the settings for the ElasticSearch index
        	to be initialised.
		"""
		try:
			connection.indices.delete_index(self.indexName)
			print 'Index with name "' + self.indexName + '" already in Elasticsearch, removed it.'
		except:
			pass

		connection.indices.create_index(self.indexName, setting)
		connection.indices.put_mapping("test_type", {'properties':mapping}, [self.indexName])
		print 'Index with name "' + self.indexName + '" added to ElasticSearch.'

	def indexArticles(self):
		"""
		Adds all articles of instance to
		ElasticSearch index.
		"""
		for article in self[self.indexName]:
			connection.index(article, self.indexName, "test-type")

		print 'Articles added to "' + self.indexName + '" in ElasticSearch.'

	def remove(self):
		"""
		Removes the index from ElasticSearch.
		"""
		try:
			connection.indices.delete_index(self.indexName)
			print "index", self.indexName, "removed from ElasticSearch."
		except:
			pass

	def displayIndex(self):
		print "index:", self

	def displayIndexName(self):
		print "indexName:", self.indexName

	def displayIndexCount(self):
		print "Number of indices:", Index.indexCount

	def displayArticleCount(self):
		print "Number of articles:", len(self[self.indexName])

