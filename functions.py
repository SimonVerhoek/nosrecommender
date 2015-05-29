#!/usr/bin/env python


from classes import Article, Collection, Query, Bool

# needed by Collection class only
from pyes import *

from settings.index_settings import setting, mapping

# create a connection with ElasticSearch
connection = ES('localhost:9200')

def query_index(query, index):

	# create new dict for storing recommended articles in
	recommendedArticles = Collection("recommendedArticles")

	returns = connection.search(query = query, index = index)
	for article in returns:
		# add ES' relevance score
		article["score"] = article._meta.score
		recommendedArticles.add_article(article)

	return recommendedArticles