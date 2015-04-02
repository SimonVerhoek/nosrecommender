#!/usr/bin/env python

class Article:

	articleCount = 0

	def __init__(self, url, title, categories, body, image):
		self.url = url
		self.title = title
		self.categories = categories
		self.body = body
		self.image = image
		Article.articleCount += 1

	def displayCount(self):
		print "Number of articles is %d" % Article.articleCount

	def displayArticle(self):
		print "url =", self.url
		print "title =", self.title
		print "categories =", self.categories
		print "body =", self.body
		print "image =", self.image

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
		Adds a given article to the index.
		"""
		self[self.indexName].append(article)

	def build(self, setting, mapping):
		"""
		Builds index in ElasticSearch.
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
		for i in self[self.indexName]:
			connection.index({  "title":i["title"],
	                            "categories":i["categories"],
	                            "body":i["body"], 
	                            "url":i["url"], 
	                            "image":i["image"]},
	                            self.indexName, "test-type")
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

	def displayCount(self):
		print "Number of indices is", Index.indexCount

	def displayIndex(self):
		print "index:", self

	def displayIndexName(self):
		print "indexName:", self.indexName

	def displayArticleCount(self):
		print "Number of articles:", len(self[self.indexName])

