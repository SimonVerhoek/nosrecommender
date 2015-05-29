#!/usr/bin/env python

from classes import Article, Collection

readArticlesFileName = "read_articles"

def main():
	"""
	Imports a collection of read articles and queries this
	against an archive of news articles.
	"""
	readArticles = Collection(readArticlesFileName)

	readArticles.import_from_json(readArticlesFileName)
	

# execute main
if __name__ == "__main__":
    main()