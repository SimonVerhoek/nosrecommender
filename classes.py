#!/usr/bin/env python

class article:

	articleCount = 0

	def __init__(self, url, title, categories, body, image):
		self.url = url
		self.title = title
		self.categories = categories
		self.body = body
		self.image = image
		article.articleCount += 1

	def displayCount(self):
		print "Number of articles is %d" % article.articleCount

	def displayArticle(self):
		print "url = ", self.url
		print "title = ", self.title
		print "categories = ", self.categories
		print "body = ", self.body
		print "image = ", self.image