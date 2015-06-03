#!/usr/bin/env python


from classes import Article, Collection#, Query, Bool

# needed by Collection class only
from pyes import *

from os import path, chdir, pardir


from settings.index_settings import setting, mapping

# create a connection with ElasticSearch
connection = ES('localhost:9200')


def query_index(query, index):
	"""
	Queries index for recommended news articles.
	Returns Collection dict with recommended articles, together
	with their scores.
	-	query should be a Query dict.
	- 	index should be a string with the name of the ElasticSearch
		index to be queried. 
	"""
	# create new dict for storing recommended articles in
	recommendedArticles = Collection("recommendedArticles")

	returns = connection.search(query = query, index = index)
	for article in returns:
		# add ES' relevance score
		article["score"] = article._meta.score
		recommendedArticles.add_article(article)

	return recommendedArticles


def import_collection(fileName):
	"""
	Imports a collection from a JSON file.
	If no file is found, program is exited.
	- 	fileName should be a string with the name of 
		a JSON file, WITHOUT the ".json" extension.
	"""
	print 'Attempting to import from "files/' + fileName + '"...'

	fileName += ".json"

	# go to files directory
	chdir("files")

	if path.isfile(fileName):
		content = json.loads(open(fileName, "rb").read())
		readArticles = Collection(content)

		# move back to parent directory
		chdir(pardir)

		return readArticles
	else:
		print "File not found."
		exit()


def export_collection(collection):
	"""
	Exports collection to a JSON file.
	The name of the collection will be given as a filename.
	The file is stored in the "files" subdirectory.
	"""
	# go to files directory
	chdir("files")

	fileName = collection.keys()[0]

	outFile = open(fileName + ".json", "w+")
	json.dump(collection, outFile, indent = 4)
	outFile.close()

	# move back to parent directory
	chdir(pardir)

	print "Exported collection to files/%s.json." % fileName
	print
