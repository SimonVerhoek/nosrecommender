#!/usr/bin/env python

import os.path
import os
import json
from sys import exit

from classes import Article, Collection

dir = os.path.dirname(__file__)

# name of exported news archive
fileName = "archive.json"

# if you want to create an index from a
# local file, give correct filepath here
localArchive =  "/Users/simonverhoek/Google Drive/Studie/Web search/Project/nosrecommender/" + fileName


def main():
    """
    Imports and builds an archive of news articles.
    """

    # import an existing archive.
    archive = import_archive(fileName)

    # build ElasticSearch index of archive
    Collection.build_index(archive)
    Collection.index_articles(archive)


def import_archive(fileName):
    """
    Imports an existing news archive.
    -   fileName should be the name of a local JSON file, 
        with an ElasticSearch-friendly format, in the 
        "/files" subfolder. 
    """
    print 'Attempting to import from "files/' + fileName + '"...'

    os.chdir("files")

    if os.path.isfile(fileName):
        content = json.loads(open(fileName, "rb").read())

        for k, v in content.iteritems():
            print "Imported: %s, %d articles" % (k, len(v))
            print

        archive = Collection(content.keys()[0], content.values()[0])
        return archive
    else:
        print "File not found."
        exit()

# execute main
if __name__ == "__main__":
    main()
