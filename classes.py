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

	indexCount = 0

	indexName = ""

	def __init__(self, key, value):
		self.indexName = key
		self.__setitem__(key, value)
		Index.indexCount += 1

	def addArticle(self, key, article):
		self[key].append(article) 

	def build(self, setting):

		try:
			connection.indices.delete_index(self.indexName)
		except:
			pass

		connection.indices.create_index(self.indexName, setting)
		print 'Index with name "' + self.indexName + '" added to ElasticSearch.'

	def remove(self):
		try:
			connection.indices.delete_index(self.indexName)
		except:
			pass

		print "index", self.indexName, "removed from ElasticSearch."


	def displayCount(self):
		print "Number of indices is", Index.indexCount

	def displayIndex(self):
		print "index:", self

	def displayIndexName(self):
		print "indexName:", self.indexName

