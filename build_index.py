#!/usr/bin/env python

import os.path
import json
from sys import exit

from classes import Article, Collection


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
    Imports an existing archive from a .json file.
    Exits when file is not found.
    filecontent[0] = collection name
    filecontent[1] = list of articles in file.
    """
    print 'Attempting to import from local file "' + fileName + '"...'
    if os.path.isfile(fileName):
        fileContent = import_collection(fileName)
        archive = Collection(fileContent[0], fileContent[1])
        return archive
    else:
        print "File not found."
        exit()


def import_collection(localFile):
    """
    Imports a JSON file from the given localFile filepath.
    The content should be a dict in the ElasticSearch-friendly
    format.
    -   localFile should be a string containing the
        path to a certain local .json file.
    """
    content = json.loads(open(localFile, "rb").read())

    for k, v in content.iteritems():
        print "Imported: %s, %d articles" % (k, len(v))
        print
        return k, v


# execute main
if __name__ == "__main__":
    main()
