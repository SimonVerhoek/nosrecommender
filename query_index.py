#!/usr/bin/env python

from settings.index_settings import mapping
from settings.general_settings import archiveName
from classes import Bool
from functions import import_collection, query_index


readArticlesFileName = "read_articles"


def main():
	"""
	Imports a collection of read articles and queries this
	against an archive of news articles.
	"""
	readArticles = import_collection(readArticlesFileName)

	#print readArticles[readArticlesFileName]

	query = Bool()

	# for every article
	#	 add matches for elements in index_settings.mapping
	for article in readArticles[readArticlesFileName]:
		query.add_occurrence("should")

		for key, value in article.iteritems():
			if key in mapping.keys():
				query.add_match_query("match", key, value)

	query = Bool()
	query.add_occurrence("should")
	query.add_match_query("match", "title", "We moeten praten met Assad, zegt de VS")
	query.add_match_query("match", "categories", "Buitenland")

	#query.add_match_query("match", "title", "We moeten praten met Assad, zegt de VS")
	#query.add_match_query("match", "categories", "Buitenland")

	#query.add_match_query("match", "title", "We moeten praten met Assad, zegt de VS")
	#query.add_match_query("match", "categories", "Buitenland")

	print query

	export_query(query)

	recommendedArticles = query_index(query, archiveName)

	#print recommendedArticles


# execute main
if __name__ == "__main__":
	main()
