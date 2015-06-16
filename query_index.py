#!/usr/bin/env python

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

	print readArticles[readArticlesFileName]

	# for every article
		# add matches for elements in index_settings.mapping

	query = Bool()
	query.add_occurrence("should")
	query.add_match_query("match", "title", "We moeten praten met Assad, zegt de VS")
	query.add_match_query("match", "categories", "Buitenland")

	recommendedArticles = query_index(query, archiveName)

	#print recommendedArticles


# execute main
if __name__ == "__main__":
	main()
